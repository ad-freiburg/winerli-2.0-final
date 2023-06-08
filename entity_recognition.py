""" Johanna Götz """

import logging
import os
import sys
import time
import datetime
import traceback
import xml.sax
import csv
import spacy
import spacy.symbols
from multiprocessing import Process, Queue, cpu_count
from spacy.tokens import Token, Doc
from wiki_parsing import *
from cleanup_page import PageCleaner
from database import Database
from recognizer import *


logging.addLevelName(100, 'PROHIBIT_LOGGING')
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(stream=sys.stdout, level=LOGLEVEL)

# Use relative paths
PATH_PREFIX = ''
if os.name == 'nt':
    PATH_PREFIX = '.'

overall_start = time.time()


class WikipediaXMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self, process_num, output_queue):
        self.process_num = process_num
        self.output_queue = output_queue
        self.stack = []

    # Reset the variables for the next page
    def reset(self):
        self.page_title = ''
        self.is_article_page = False
        self.is_redirect = False
        logging.info('---')

    # Handle the start tag and its attributes
    def startElement(self, tag, attrs):
        self.stack.append([tag, ''])
        if tag == 'page':
            logging.warning('-' * 10)
            logging.warning('%s: Start with new page...' % datetime.datetime.now())
            # Reset variables
            self.reset()
            self.log(('...has started at %s.' % datetime.datetime.now()))
        # Handle redirects
        elif tag == 'redirect':
            self.is_redirect = True

    # Handle the content
    def characters(self, content):
        index = len(self.stack) - 1
        if index >= 0:
            self.stack[index][1] += content

    # Handle the ending tag
    def endElement(self, tag):
        stacked_tag, content = self.stack.pop()
        logging.debug('Tags: %s --- %s; equal? %s' % (tag, stacked_tag, tag == stacked_tag))
        if tag == 'title':
            self.page_title = content
            logging.warning('Page "%s"', self.page_title)
        elif tag == 'ns':
            # If this is a page or an article, the value is 0
            self.is_article_page = (content == '0')
            logging.info('Is article? %s', self.is_article_page)
        elif tag == 'text':
            text = content
            # If the page is an article and not a redirect
            if self.is_article_page and not self.is_redirect:
                try:
                    self.apply((self.page_title, text))
                except Exception as e:
                    logging.critical(e)
                    logging.critical(traceback.format_exc())
                    self.log((e, traceback.format_exc()))
        elif tag == 'page':
            logging.warning('%s: ...page "%s" has ended.' % (datetime.datetime.now(), self.page_title))
            self.log(('...has ended at %s.' % datetime.datetime.now()))
            if self.is_article_page:
                pass
        elif tag == 'mediawiki':
            # Reset variables
            self.reset()
            logging.warning('Parsing finished in %s s', (time.time() - overall_start))
            self.log(('Parsing finished in %s s.' % (time.time() - overall_start)))

    def apply(self, data):
        self.output_queue.put((self.process_num, data))


def parse_worker(input, output, i):
    logging.warning('Parse process %s' % i)
    for args in iter(input.get, 'STOP'):
        my_WikiXMLHandler = WikipediaXMLHandler(i, output)
        parser = xml.sax.make_parser(['xml.sax.IncrementalParser'])
        parser.setContentHandler(my_WikiXMLHandler)
        offset_range = args[0]
        content = args[1]
        try:
            logging.critical('EVERYTHING OKAY HERE:\n' + '\n'.join(['Process: ', repr(i),
                                                                    'Offsets: ', repr(offset_range),
                                                                    content[:200].replace('\n', ' ') + ' [...] ' + content[-200:].replace('\n', ' ')]))
            parser.feed(content)
        except Exception as e:
            logging.critical('PROBLEM HERE:\n' + '\n'.join(
                [repr(e), 'Process: ', repr(i), 'Offsets: ', repr(offset_range),
                 content[:200].replace('\n', ' ') + ' [...] ' + content[-200:].replace('\n', ' ')]
            ))


def clean_recognise(page_title, page_text, entity_recogniser, process_num):
    # Clean up the page
    try:
        pc = PageCleaner(page_text)
        stripped_text = pc.strip_templates()
        logging.debug('Text content: ' + stripped_text[:300])
        # Do some recognition stuff...
        logging.warning('Recognition process %i does recognition on page %s...' % (process_num, page_title))
        recognition_result = entity_recogniser.start(stripped_text, wiki_format(page_title))
        logging.warning('Recognition process %i finished recognition on page %s...' % (process_num, page_title))
        return recognition_result
    except Exception as e:
        logging.critical('Page %s could not be cleaned up because an error occurred:' % page_title)
        logging.critical(e)
        logging.critical('Page %s will be skipped.' % page_title)
        return None


@timeit(1)
def clean_recognise_worker(input, output, i, gender_data_file_name,
                           infobox_category_file_name, aliasmap_db,
                           page_category_db, links_db, scoring_factors,
                           threshold, use_adjectives=True, use_numbers=False,
                           use_nonbinary=False):
    logging.warning('Recognition process %s' % i)
    # Load gender data
    gender_db = dict()
    load_gender_data(gender_db, gender_data_file_name)
    # Load category data
    category_db = dict()
    load_infobox_category_data(category_db, infobox_category_file_name, cleanup=True)
    # Load spaCy
    nlp = spacy.load('en_core_web_sm', disable=['ner', 'textcat'])
    # Avoid splitting at apostrophes
    nlp.tokenizer.rules = {key: value for key, value in nlp.tokenizer.rules.items() if "'" not in key and "’" not in key and "‘" not in key}
    # How many characters spacy will handle. 1M char ~ 1GB RAM.
    nlp.max_length = 3000000
    # Do cleaning and recognition
    # Set up the entity recogniser
    er = EntityRecogniser(nlp, threshold, use_adjectives=use_adjectives,
                          use_numbers=use_numbers, use_nonbinary=use_nonbinary)
    er.database = aliasmap_db
    er.page_category_db = page_category_db
    er.links_db = links_db
    er.gender_database = gender_db
    er.category_database = category_db
    er.scoring_factors = scoring_factors
    # Go through all the article pages
    for _, args in iter(input.get, 'STOP'):
        page_title = args[0]
        page_text = args[1]
        recognition_result = clean_recognise(page_title, page_text, er, i)
        if recognition_result is not None:
            # Collect all results
            collected_results = []
            for result in recognition_result:
                collected_results.append(result)
            output.put(collected_results)


def handle_result(i, result, wordsfile_name, docsfile_name, write_scores=0):
    logging.warning('Writing process %s' % i)
    # Each process numbers their records independently
    record_id = 0
    with open(wordsfile_name % i, 'w', newline='') as wordsfile, open(docsfile_name % i, 'w', newline='') as docsfile:
        wordsfile_writer = csv.writer(wordsfile, delimiter='\t',
                                      escapechar='\\', quoting=csv.QUOTE_NONE,
                                      lineterminator='\n')
        docsfile_writer = csv.writer(docsfile, delimiter='\t',
                                     escapechar='\\', quoting=csv.QUOTE_NONE,
                                     lineterminator='\n')
        for args in iter(result.get, 'STOP'):
            for result_element in args:
                entities = result_element[0]
                sent_tokens = result_element[1]
                length = len(sent_tokens)
                # Get rid of all tabs and newlines
                cleaned_sent_tokens = sent_tokens[:].orth_.replace('\t', '').replace('\r', '').replace('\n', '')
                if len(cleaned_sent_tokens) > 0:
                    record_id += 1
                    prefixed_id = str(record_id)
                    docsfile_writer.writerow((str(prefixed_id), cleaned_sent_tokens))
                else:
                    continue
                for j in range(length):
                    token = sent_tokens[j]
                    logging.warning('Writing output: "' + repr(token) + '"; real thingy: "' + repr(token.text.encode('unicode_escape')) + '"; pure thingy: ' + repr(token.text))
                    # Ignore newlines
                    if token.text.strip('\r\n\t ') == '':
                        continue
                    if token.pos == spacy.symbols.PUNCT:
                        # Don't print any punctuation symbols in the words_file.
                        continue
                    # Only one score is written
                    if write_scores != 2:
                        wordsfile_writer.writerow((token.text.replace('\t', ''), '0', str(prefixed_id), '1'))
                    # Both scores are written
                    else:
                        wordsfile_writer.writerow((token.text.replace('\t', ''), '0', str(prefixed_id), '1', '1'))
                    entity = entities[j]
                    if entity is not None:
                        # Write only the relevance
                        if write_scores == 0:
                            wordsfile_writer.writerow(('<' + entity.wikilink + '>', '1',
                                                      str(prefixed_id),
                                                      str(entity.relevance) if entity.relevance is not None else str(1.0)))
                        # Write only the final score
                        elif write_scores == 1:
                            wordsfile_writer.writerow(('<' + entity.wikilink + '>', '1',
                                                      str(prefixed_id),
                                                      str(entity.score)))
                        # Write both scores
                        elif write_scores == 2:
                            wordsfile_writer.writerow(('<' + entity.wikilink + '>', '1',
                                                      str(prefixed_id),
                                                      str(entity.relevance) if entity.relevance is not None else str(1.0),
                                                      str(entity.score)))
                logging.warning('Writing docsfile line: "' + repr(sent_tokens[:].orth_))


def start(wiki_dump, index_file, wordsfile_name, docsfile_name, logfile_name,
          aliasmap_db, page_category_db, links_db, infobox_category_file_name,
          gender_data_file_name, scoring_factors, threshold,
          use_adjectives, use_numbers, use_nonbinary, write_scores,
          num_write_processes, num_parse_processes, max_num_processes=None):
    # One process is needed for the extraction of content of the bz2 file
    # The rest can do the parsing, recognition and output writing
    if max_num_processes is None:
        max_num_processes = cpu_count()
    NUMBER_OF_PROCESSES = max(min(cpu_count(), max_num_processes) - num_write_processes - num_parse_processes - 1, 1)

    parse_processes = []
    recognise_processes = []
    write_procs = []

    # Create queues
    # Will contain the blocks of wiki articles to be parsed in the next step
    task_queue = Queue()
    # Will contain the xml-parsed pages to be processed for entity recognition
    parsed_queue = Queue()
    # Will contain the recognition results to be written to the output files
    recognised_queue = Queue()

    # Start worker processes
    # This program can take an index file and if one is given,
    # then the chunks will be generated using the index file
    # Otherwise each chunk will consist of exactly one page
    if len(index_file) > 0:
        input_proc = Process(target=generate_chunks, args=(wiki_dump, index_file, task_queue))
    else:
        input_proc = Process(target=generate_chunks_noindex, args=(wiki_dump, task_queue))

    for i in range(num_parse_processes):
        parse_processes.append(Process(target=parse_worker, args=(task_queue, parsed_queue, i)))

    for i in range(NUMBER_OF_PROCESSES):
        recognise_processes.append(Process(target=clean_recognise_worker,
                                           args=(parsed_queue, recognised_queue, i,
                                                 gender_data_file_name,
                                                 infobox_category_file_name,
                                                 aliasmap_db, page_category_db,
                                                 links_db, scoring_factors,
                                                 threshold, use_adjectives,
                                                 use_numbers, use_nonbinary)))

    for i in range(num_write_processes):
        write_procs.append(Process(target=handle_result, args=(i, recognised_queue, wordsfile_name, docsfile_name, write_scores)))

    input_proc.start()
    for p in parse_processes:
        p.start()

    for p in recognise_processes:
        p.start()

    for p in write_procs:
        p.start()

    input_proc.join()

    # Tell child processes to stop
    for i in range(num_parse_processes):
        task_queue.put('STOP')

    for p in parse_processes:
        p.join()

    for i in range(NUMBER_OF_PROCESSES):
        parsed_queue.put('STOP')

    for p in recognise_processes:
        p.join()

    for i in range(num_write_processes):
        recognised_queue.put('STOP')

    for p in write_procs:
        p.join()


@timeit(1)
def main():
    # The name of the wiki dump file
    input_file = os.getenv('INPUT_FILE', '')

    # The index file for the wiki dump
    index_file = os.getenv('INDEX_FILE', '')

    # How many processes should be used at maximum?
    max_num_processes = os.getenv('NUMBER_PROCESSES', None)
    if max_num_processes is not None:
        max_num_processes = int(max_num_processes)

    # How many write-only processes should be used at maximum?
    num_write_processes = os.getenv('NUMBER_WRITE_PROCESSES', None)
    if num_write_processes is not None:
        num_write_processes = int(num_write_processes)

    # How many parse-only processes should be used at maximum?
    num_parse_processes = os.getenv('NUMBER_PARSE_PROCESSES', None)
    if num_parse_processes is not None:
        num_parse_processes = int(num_parse_processes)

    # Check the environment variable for the wordsfile name
    wordsfile_name = os.getenv('WORDS_FILE', '')
    if len(wordsfile_name) < 1:
        wordsfile_name = 'wordsfile_%s.tsv'

    # Check the environment variable for the docsfile name
    docsfile_name = os.getenv('DOCS_FILE', '')
    if len(docsfile_name) < 1:
        docsfile_name = 'docsfile_%s.tsv'

    # Check the environment variable for the log file name
    logfile_name = os.getenv('LOG_FILE', '')
    if len(logfile_name) < 1:
        logfile_name = 'log_%s.txt'

    # Check the environment variable for the scoring factors
    try:
        scoring_factors = eval(os.getenv('SCORING_FACTORS', ''))
    except:
        scoring_factors = (0, 0, 0, 0)

    # Check the environment variable for the threshold value
    try:
        threshold = float(os.getenv('THRESHOLD', ''))
    except:
        threshold = 0.5

    # Check the environment variable for whether adjectives should be used in the recognition or not
    use_adjectives = os.getenv('USE_ADJECTIVES', '')
    if use_adjectives.lower() == 'false':
        use_adjectives = False
    else:
        use_adjectives = True

    # Check the environment variable for whether numbers should be used in the recognition or not
    use_numbers = os.getenv('USE_NUMBERS', '')
    if use_numbers.lower() == 'true':
        use_numbers = True
    else:
        use_numbers = False

    # Check the environment variable for whether the non-binary gender should be used in the recognition or not
    use_nonbinary = os.getenv('USE_NONBINARY', '')
    if use_nonbinary.lower() == 'true':
        use_nonbinary = True
    else:
        use_nonbinary = False

    # Check the environment variable for which type of score should be written in the output
    # 0 = relevance
    # 1 = final score
    # 2 = both
    write_scores = os.getenv('WRITE_SCORES', '')
    if write_scores is not None:
        write_scores = int(write_scores)
    else:
        write_scores = 0

    # Check the environment variable for the gender data file name
    gender_data_file_name = os.path.join(PATH_PREFIX + '/databases', os.getenv('GENDER_DATA_FILE', 'gender_data.tsv'))

    # Check the environment variable for the infobox category file name
    infobox_category_file_name = os.path.join(PATH_PREFIX + '/databases', os.getenv('INFOBOX_CATEGORY_FILE', 'infobox_category.tsv'))

    # Check the environment variable for the database containing the categories each article belongs to
    page_category_db = Database(os.path.join(PATH_PREFIX + '/databases', os.getenv('PAGE_CATEGORY_DB', 'page_category_db.db')), read_only=True)

    # Check the environment variable for the database containing data which article links to which other article
    links_db = Database(os.path.join(PATH_PREFIX + '/databases', os.getenv('LINKS_DB', 'links_db.db')), read_only=True)

    # Check the environment variable for the aliasmap database
    aliasmap_db = Database(os.path.join(PATH_PREFIX + '/databases', os.getenv('ALIASMAP_DB', 'aliasmap.db')), read_only=True)

    start(PATH_PREFIX + os.path.join('/input', input_file),
          (PATH_PREFIX + os.path.join('/input', index_file)) if len(index_file) > 0 else '',
          PATH_PREFIX + os.path.join('/output', wordsfile_name),
          PATH_PREFIX + os.path.join('/output', docsfile_name),
          PATH_PREFIX + os.path.join('/log', logfile_name),
          aliasmap_db,
          page_category_db,
          links_db,
          infobox_category_file_name,
          gender_data_file_name,
          scoring_factors=scoring_factors,
          threshold=threshold,
          use_adjectives=use_adjectives,
          use_numbers=use_numbers,
          use_nonbinary=use_nonbinary,
          write_scores=write_scores,
          num_write_processes=num_write_processes,
          num_parse_processes=num_parse_processes,
          max_num_processes=max_num_processes)
    # Close all databases
    page_category_db.close()
    links_db.close()
    aliasmap_db.close()


if __name__ == '__main__':
    if os.getenv('RUN_TESTS', None) is not None:
        import pytest
        sys.exit(pytest.main())
    else:
        main()
