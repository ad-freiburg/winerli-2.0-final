""" Johanna Götz """

import json
import logging
import os
import sys
import time
import datetime
import traceback
import xml.sax
import regex as re
from multiprocessing import Process, Queue, cpu_count
from wiki_parsing import *
from parse_info import InfoboxLinkParser
from database import Database


logging.addLevelName(100, 'PROHIBIT_LOGGING')
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(stream=sys.stdout, level=LOGLEVEL)

# Use relative paths
PATH_PREFIX = '/'
if os.name == 'nt':
    PATH_PREFIX = '.'

overall_start = time.time()


class WikipediaXMLHandler(xml.sax.handler.ContentHandler):
    __slots__ = ('process_num', 'output_queue', 'logging', 'stack',
                 'invalid_link', 'disambiguation_regex', 'disambiguation_regex_baumert',
                 'name_synonyms', 'name_synonyms', 'page_title', 'is_article_page',
                 'is_disambiguation', 'redirect_target', 'page_counter', 'baumert')

    def __init__(self, process_num, output_queue, baumert=False):
        self.process_num = process_num
        self.output_queue = output_queue
        self.stack = []
        self.baumert = baumert
        # Regex to detect special links and also interlanguage links
        self.invalid_link = re.compile(r'^(File|Image|wikt|Wikipedia|WP|Media|Wikisource|Species|Commons|Help|Talk|[a-z]{2}):')
        # Regexes to extract data
        self.disambiguation_regex = re.compile(
            r'(?i){{(?:disambiguation|disambig|disamb|dab|hndis|(?:[a-z\-]*?(?:dab|dis|disambiguation|disambig|disamb)))(?:[- ]cleanup)?(?:\|[a-z\-,= ]*?)?}}')
        self.disambiguation_regex_baumert = re.compile(
            r'(?i){{(?:disambiguation)(?:\|[a-z\-]*?)?}}')
        self.name_synonyms = (
            'name',
            # Country
            'common_name', 'conventional_long_name',
            # Book
            'title_orig', 'working_title', 'isbn',
            # Film
            'film_name',
            # Musical artist
            'alias',
            # Infobox song
            'English_title',
            # Television
            'show_name', 'show_name_2', 'native_name', 'alt_name',
            # Person
            'native_name', 'birth_name', 'birthname', 'full_name', 'fullname'
            # Royalty
            'title',
            # Company
            'trading_name', 'romanized_name', 'ISIN'
        )
        self.page_counter = 0

    # Reset all variables for the next page
    def reset(self):
        self.page_title = ''
        self.is_article_page = False
        self.is_disambiguation = False
        self.redirect_target = None
        logging.info('---')

    # Find out if a page is a disambiguation page
    def is_disambiguation_page(self, text):
        # The disambiguation template occurs at the end
        if not self.baumert:
            return self.disambiguation_regex.search(text[-500:]) is not None
        else:
            return self.disambiguation_regex_baumert.search(text[-500:]) is not None

    # Extract links and data from infoboxes
    def extract_links_and_infoboxes(self, text):
        try:
            logging.warning('%s: Parsing infoboxes and links...' % datetime.datetime.now())
            ip = InfoboxLinkParser(text)
            ip.parse()
            logging.warning('%s: ...done.' % datetime.datetime.now())
            wikilink = wiki_format(self.page_title)
            # Handle link data
            categories = []
            logging.warning('%s: Filter data and add to database...' % datetime.datetime.now())
            # Collect all data that goes into the aliasmap
            aliasmap_data = []
            # Collect all data that goes into the links db
            links_data = []
            # Examine all the extracted links
            for curr_tuple in ip.get_links():
                url, link_string = curr_tuple
                # If a page contains a link that links to a section of the same page
                # it can happen that the url is empty.
                # Use the current page name in this case
                if len(url) == 0:
                    url = self.page_title
                # Remove the colon, see https://en.wikipedia.org/wiki/Help:Colon_trick
                elif url[0] == ':':
                    url = url[1:]
                # Ignore certain special links and also interlanguage links
                if self.invalid_link.search(url) is not None:
                    continue
                # Extract a page's categories
                elif url[:9] == 'Category:':
                    categories.append(url[9:])
                    continue
                aliasmap_data.append((link_string, url))
                # Insert the page and the link into the link database
                links_data.append((wikilink, wiki_format(url)))
            # Handle infobox data
            infobox_cat_data = []
            for category, infobox in ip.get_infoboxes():
                for key, value in infobox.items():
                    if key in self.name_synonyms:
                        # Don't save the 'name' argument if it's equal to the title to prevent overemphasising
                        if not value or (key == 'name' and value == self.page_title):
                            continue
                        aliasmap_data.append((value, self.page_title))
                # Save the category data
                for cat in re.sub('(<!--.*?-->)', '', category, flags=re.DOTALL).split(','):
                    infobox_cat_data.append(cat.strip())
            # Add all the data
            self.apply('INSERT_UPDATE_ALIASMAP', aliasmap_data)
            self.apply('INSERT_INTO_LINKS_DB', links_data)
            self.apply('INSERT_INTO_INFOBOXCATEGORY_FILE', [(wikilink, json.dumps(infobox_cat_data) if len(infobox_cat_data) > 0 else None)])
            # Serialise the categories list and add it to the database
            self.apply('INSERT_INTO_PAGECATEGORY_DB', [(wikilink, json.dumps(categories))])
            logging.warning('%s: ...all filtering and adding done.' % datetime.datetime.now())
            self.page_counter += 1
        except Exception as e:
            logging.critical(text)
            raise e

    # Handle the start tag and its attributes
    def startElement(self, tag, attrs):
        self.stack.append([tag, ''])
        if tag == 'page':
            logging.warning('-' * 10)
            logging.warning('%s: Start with new page...' % datetime.datetime.now())
            # Reset variables
            self.reset()
        # Handle redirects
        elif tag == 'redirect':
            logging.warning('%s: Start with new redirect...' % datetime.datetime.now())
            self.redirect_target = attrs.getValue('title')
            logging.info('Redirect "%s" to "%s"',
                         self.page_title, self.redirect_target)
            # If a valid redirect has been found, add it
            # Also, add the current page with its redirect to the extracted links
            if self.redirect_target is not None:
                # Add the page and the redirect target
                self.apply('INSERT_UPDATE_ALIASMAP', [(self.page_title, self.redirect_target)])
                self.apply('INSERT_REDIRECT', [(wiki_format(self.page_title), wiki_format(self.redirect_target))])

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
            # Add the page itself
            # Replace spaces by underscores
            self.apply('INSERT_UPDATE_ALIASMAP', [(self.page_title, self.page_title)])
            self.apply('INSERT_UPDATE_ARTICLE_PAGES', [(self.page_title,)])
            logging.info('Page "%s"', self.page_title)
        elif tag == 'ns':
            # If this is a page or an article, the value is 0
            self.is_article_page = content == '0'
            logging.info('Is article? %s', self.is_article_page)
        elif tag == 'text':
            text = content
            # If the page is an article and not a redirect
            if self.is_article_page and self.redirect_target is None:
                self.is_disambiguation = self.is_disambiguation_page(text)
                logging.info('Is disambiguation? %s', self.is_disambiguation)
                # Take note that the current page is a disambiguation page
                # The page will still be parsed later on
                if self.is_disambiguation:
                    self.apply('INSERT_REDIRECT', [(wiki_format(self.page_title), '__DISAMBIGUATION__')])
                # Extract urls + the link texts
                self.extract_links_and_infoboxes(text)
        elif tag == 'page':
            logging.warning('%s: ...page "%s" has ended.' % (datetime.datetime.now(), self.page_title))
        elif tag == 'mediawiki':
            # Reset variables
            self.reset()
            logging.warning('Process %d: Parsing block finished in %s s' % (self.process_num, time.time() - overall_start))

    def apply(self, action, data):
        self.output_queue.put((self.process_num, action, data))


class AliasmapOutput:
    __slots__ = ('final_db', 'links_db', 'page_category_db', 'infobox_category_file', 'drop_and_vacuum', 'filter_red_links')

    def __init__(self, final_db, links_db=None, page_category_db=None, infobox_category_file=None,
                 drop_and_vacuum=False, filter_red_links=False):
        self.final_db = final_db
        self.links_db = links_db
        self.page_category_db = page_category_db
        self.infobox_category_file = infobox_category_file
        self.drop_and_vacuum = drop_and_vacuum
        self.filter_red_links = filter_red_links

    def create_dbs(self):
        # Create tables and indices
        try:
            self.final_db.query("""
                CREATE TABLE IF NOT EXISTS `temp_aliasmap` (
                    `lnrm` TEXT NOT NULL,
                    `wikilink` TEXT NOT NULL,
                    `num` INTEGER NOT NULL DEFAULT 0,
                    `relevance` NUMERIC NOT NULL DEFAULT 0,
                    PRIMARY KEY (`lnrm`, `wikilink`)
                ) WITHOUT ROWID
            """)
            self.final_db.query("""
                CREATE TABLE IF NOT EXISTS `redirects` (
                    `wikilink` TEXT NOT NULL,
                    `target` TEXT NOT NULL
                )
            """)
            self.final_db.query("""
                CREATE TABLE IF NOT EXISTS `article_pages` (
                    `wikilink` TEXT NOT NULL
                )
            """)
            self.final_db.query("""
                CREATE INDEX IF NOT EXISTS `lnrm_wikilink_index`
                ON `temp_aliasmap` (`lnrm` ASC, `wikilink`)
            """)
            self.final_db.query("""
                CREATE INDEX IF NOT EXISTS `wikilink_index`
                ON `temp_aliasmap` (`wikilink`)
            """)
            self.final_db.query("""
                CREATE INDEX IF NOT EXISTS `wikilink_article_index`
                ON `article_pages` (`wikilink`)
            """)
            self.final_db.query("""
                PRAGMA journal_mode = OFF
            """)
            self.final_db.query("""
                PRAGMA synchronous = OFF
            """)
            self.final_db.query("""
                PRAGMA locking_mode = EXCLUSIVE
            """)
            self.final_db.commit()
            self.final_db.start_transaction()
        except Exception as e:
            print(e)
            # If database could not be opened or something...
            sys.exit(1)
        if self.links_db is not None:
            # Create the database that consists of pairs of a wikilink and sites it links to,
            # so that one can easily find out for a given page A (wikilink) if another page B links to it (links_to)
            self.links_db.query("""
                CREATE TABLE IF NOT EXISTS `links` (
                    `wikilink` TEXT NOT NULL,
                    `links_to` TEXT NOT NULL,
                    PRIMARY KEY (`wikilink`, `links_to`)
                )
            """)
            self.links_db.query("""
                CREATE INDEX IF NOT EXISTS `links_to_index`
                ON `links` (`links_to`)
            """)
            self.links_db.query("""
                PRAGMA journal_mode = OFF
            """)
            self.links_db.query("""
                PRAGMA synchronous = OFF
            """)
            self.links_db.query("""
                PRAGMA locking_mode = EXCLUSIVE
            """)
            self.links_db.commit()
            self.links_db.start_transaction()

        if self.page_category_db is not None:
            # Create the database that lists the categories for each page if given as an argument
            self.page_category_db.query("""
                CREATE TABLE IF NOT EXISTS `categories` (
                    `wikilink` TEXT NOT NULL,
                    `categories` TEXT NOT NULL,
                    PRIMARY KEY (`wikilink`)
                )
            """)
            self.page_category_db.query("""
                CREATE INDEX IF NOT EXISTS `wikilink_index`
                ON `categories` (`wikilink`)
            """)
            self.page_category_db.query("""
                PRAGMA journal_mode = OFF
            """)
            self.page_category_db.query("""
                PRAGMA synchronous = OFF
            """)
            self.page_category_db.query("""
                PRAGMA locking_mode = EXCLUSIVE
            """)
            self.page_category_db.commit()
            self.page_category_db.start_transaction()

        if self.infobox_category_file is not None:
            # File to save the infobox categories for each page
            self.infobox_category_file = open(self.infobox_category_file, 'w', encoding='utf-8')

    # Commit data to all databases
    @timeit(1)
    def write_to_dbs(self, start_new_batch=True):
        logging.warning('%s: Writing batch after %s s' % (datetime.datetime.now(), time.time() - overall_start))
        self.final_db.commit()
        if self.page_category_db is not None:
            self.page_category_db.commit()
        if self.links_db is not None:
            self.links_db.commit()
        if start_new_batch:
            self.final_db.start_transaction()
            if self.page_category_db is not None:
                self.page_category_db.start_transaction()
            if self.links_db is not None:
                self.links_db.start_transaction()

    # Insert and update the database with new data
    def insert_update_aliasmap(self, lnrm_text, wikilink_text):
        lnrm = lnrm_repr(lnrm_text)
        wikilink = wiki_format(wikilink_text)
        self.final_db.query("""
            INSERT OR IGNORE INTO `temp_aliasmap` (lnrm, wikilink) VALUES(?, ?);
        """, (lnrm, wikilink))
        self.final_db.query("""
            UPDATE `temp_aliasmap`
            SET `num` = `num` + 1
            WHERE `lnrm` = ? AND `wikilink` = ?;
        """, (lnrm, wikilink))

    # Add the article page to the database
    def insert_article_page(self, wikilink_text):
        wikilink = wiki_format(wikilink_text)
        self.final_db.query("""
            INSERT INTO `article_pages` (`wikilink`)
            VALUES(?);
        """, (wikilink,))

    # Insert redirect into database
    def insert_redirect(self, wikilink, redirect_target):
        logging.info('Database: Adding "%s" with redirect "%s"' % (wikilink, redirect_target))
        self.final_db.query("""
            INSERT INTO `redirects` (`wikilink`, `target`)
            VALUES (?,?);
        """, (wikilink, redirect_target))

    # Insert a link into the database
    def insert_into_links_db(self, wikilink, links_to):
        if self.links_db is not None:
            self.links_db.query("""
                INSERT OR IGNORE INTO `links` (`wikilink`, `links_to`)
                VALUES (?,?);
            """, (wikilink, links_to))

    # Insert categories into database
    def insert_into_pagecategory_db(self, wikilink, categories):
        try:
            if self.page_category_db is not None:
                logging.info('Database: Adding "%s" with categories "%s"' % (wikilink, categories))
                self.page_category_db.query("""
                    INSERT INTO `categories` (`wikilink`, `categories`)
                    VALUES (?,?);
                """, (wikilink, categories))
        except:
            logging.critical('Error in dump -- duplicate page: %s' % repr(wikilink))

    def insert_into_infoboxcategory_file(self, wikilink, categories):
        if self.infobox_category_file is not None and categories is not None:
            print(wikilink, categories, sep='\t', file=self.infobox_category_file)

    def finalise(self):
        # Write the data from the very last page
        self.write_to_dbs(start_new_batch=False)
        # Close infobox category file
        if self.infobox_category_file is not None:
            self.infobox_category_file.close()
        # Calculate the scores
        self.calculate_scores()
        # Drop temp data and vacuum
        if self.drop_and_vacuum:
            self.drop_temp_and_vacuum()
        # Close all of the databases
        self.final_db.commit_and_close()
        if self.links_db is not None:
            self.links_db.commit_and_close()
        if self.page_category_db is not None:
            self.page_category_db.commit_and_close()

    # Calculate the scores for each occurrence
    @timeit(1)
    def calculate_scores(self):
        # Create an index for the redirects table
        # This doesn't need to be done before because the table is never queried earlier
        self.final_db.query("""
            CREATE INDEX IF NOT EXISTS `redirects_wikilink_index`
            ON `redirects` (`wikilink`)
        """)
        # Set the redirects and update the number of occurrences
        logging.critical('Calculating redirects...')
        if not self.filter_red_links:
            self.final_db.query("""
                CREATE TABLE `aliasmap` AS
                SELECT `lnrm`, `target` AS `wikilink`, SUM(`num`) as `num`, 0 as `relevance`
                FROM (
                    SELECT
                    `temp_aliasmap`.`lnrm` AS `lnrm`,
                    `temp_aliasmap`.`wikilink` AS `wikilink`,
                    CASE
                        WHEN `redirects`.`target` IS NOT NULL
                        THEN `redirects`.`target`
                        ELSE `temp_aliasmap`.`wikilink`
                        END AS `target`,
                    `temp_aliasmap`.`num` AS `num`
                    FROM `temp_aliasmap`
                    LEFT OUTER JOIN `redirects` ON `temp_aliasmap`.`wikilink` = `redirects`.`wikilink`
                ) `final_values`
                WHERE `final_values`.`target` <> '__DISAMBIGUATION__'
                GROUP BY `final_values`.`lnrm`, `final_values`.`target`
                ;
            """)
        else:
            self.final_db.query("""
                CREATE TABLE `aliasmap` AS
                SELECT `lnrm`, `target` AS `wikilink`, SUM(`num`) as `num`, 0 as `relevance`
                FROM (
                    SELECT
                    `temp_aliasmap`.`lnrm` AS `lnrm`,
                    `temp_aliasmap`.`wikilink` AS `wikilink`,
                    CASE
                        WHEN `redirects`.`target` IS NOT NULL
                        THEN `redirects`.`target`
                        ELSE `temp_aliasmap`.`wikilink`
                        END AS `target`,
                    `temp_aliasmap`.`num` AS `num`
                    FROM `temp_aliasmap`
                    LEFT OUTER JOIN `redirects` ON `temp_aliasmap`.`wikilink` = `redirects`.`wikilink`
                    LEFT OUTER JOIN `article_pages` ON `temp_aliasmap`.`wikilink` = `article_pages`.`wikilink`
                    WHERE `article_pages`.`wikilink` IS NOT NULL
                ) `final_values`
                WHERE `final_values`.`target` <> '__DISAMBIGUATION__'
                GROUP BY `final_values`.`lnrm`, `final_values`.`target`
                ;
            """)
        self.final_db.query("""
            CREATE INDEX `aliasmap_lnrm_wikilink_index`
            ON `aliasmap` (`lnrm` ASC, `wikilink`)
        """)
        self.final_db.query("""
            CREATE INDEX `aliasmap_wikilink_index`
            ON `aliasmap` (`wikilink`)
        """)
        self.final_db.query("""
            CREATE INDEX `aliasmap_lnrm_index`
            ON `aliasmap` (`lnrm`)
        """)
        logging.critical('Calculating redirects finished in %s s', (time.time() - overall_start))
        # Calculate the scores
        logging.critical('Calculating scores...')
        self.final_db.query("""
            WITH `sums`(`lnrm`, `sum`) AS (
                SELECT `lnrm`, SUM(`num`)
                FROM `aliasmap`
                GROUP BY `lnrm`
            )
            UPDATE `aliasmap`
            SET `relevance` = CAST(`num` as FLOAT) / (
                SELECT `sum`
                FROM `sums`
                WHERE `aliasmap`.`lnrm` = `sums`.`lnrm`
            );
        """)
        logging.critical('Calculating scores finished in %s s', (time.time() - overall_start))
        self.final_db.commit()

    # Drop the temporary table and vacuum
    @timeit(1)
    def drop_temp_and_vacuum(self):
        logging.critical('Dropping temporary table and vacuuming...')
        self.final_db.query("""DROP TABLE `temp_aliasmap`;""")
        self.final_db.commit()
        self.final_db.query("""VACUUM;""")
        self.final_db.commit()
        logging.critical('DROP and VACUUM finished in %s s', (time.time() - overall_start))


def worker(input, output, i):
    logging.warning('Process %s' % i)
    page_counter = 0
    block_counter = 0
    for args in iter(input.get, 'STOP'):
        my_WikiXMLHandler = WikipediaXMLHandler(i, output)
        parser = xml.sax.make_parser(['xml.sax.IncrementalParser'])
        parser.setContentHandler(my_WikiXMLHandler)
        try:
            logging.info('EVERYTHING OKAY HERE:\n' + '\n'.join(
                ['Process: ', repr(i), 'Offsets: ', repr(args[0]),
                 args[1][:200].replace('\n', ' ') + ' [...] ' + args[1][-200:].replace('\n', ' ')])
            )
            parser.feed(args[1])
            block_counter += 1
            page_counter += my_WikiXMLHandler.page_counter
        except Exception as e:
            logging.critical('PROBLEM HERE:\n' + '\n'.join(
                [repr(e), repr(traceback.format_exc()), 'Process: ', repr(i),
                 'Offsets: ', repr(args[0]),
                 args[1][:200].replace('\n', ' ') + ' [...] ' + args[1][-200:].replace('\n', ' ')])
            )
    logging.critical('Process %d processed %d blocks containing a total of %d article pages.' % (i, block_counter, page_counter))


def handle_result(result, final_db, links_db, page_category_db, infobox_category_file, batch_size,
                  drop_and_vacuum=False, filter_red_links=False):
    batch_counter = 0
    aliasmap_output = AliasmapOutput(final_db, links_db, page_category_db, infobox_category_file,
                                     drop_and_vacuum, filter_red_links)
    aliasmap_output.create_dbs()
    for i, action, data in iter(result.get, 'STOP'):
        for args in data:
            if action == 'INSERT_UPDATE_ALIASMAP':
                aliasmap_output.insert_update_aliasmap(*args)
            elif action == 'INSERT_UPDATE_ARTICLE_PAGES':
                aliasmap_output.insert_article_page(*args)
            elif action == 'INSERT_REDIRECT':
                aliasmap_output.insert_redirect(*args)
            elif action == 'INSERT_INTO_LINKS_DB':
                aliasmap_output.insert_into_links_db(*args)
            elif action == 'INSERT_INTO_PAGECATEGORY_DB':
                aliasmap_output.insert_into_pagecategory_db(*args)
            elif action == 'INSERT_INTO_INFOBOXCATEGORY_FILE':
                aliasmap_output.insert_into_infoboxcategory_file(*args)
        batch_counter += 1
        if (batch_counter % batch_size == 0):
            aliasmap_output.write_to_dbs()
    aliasmap_output.finalise()


def start(wiki_dump, index_file, final_db, links_db=None, page_category_db=None,
          infobox_category_file=None, batch_size=100000, max_num_processes=None,
          drop_and_vacuum=False, filter_red_links=False):
    # One process is needed for the extraction of content of the bz2 file
    # One process is needed for the output
    # The rest can do the parsing
    if max_num_processes is None:
        max_num_processes = cpu_count()
    NUMBER_OF_PROCESSES = max(min(cpu_count(), max_num_processes) - 2, 1)

    logging.critical('Start with %s processes!' % str(NUMBER_OF_PROCESSES))

    processes = []

    # Create queues
    task_queue = Queue(maxsize=2 * NUMBER_OF_PROCESSES)
    done_queue = Queue(maxsize=16 * NUMBER_OF_PROCESSES)

    # Start worker processes
    if len(index_file) > 0:
        input_proc = Process(target=generate_chunks,
                             args=(wiki_dump, index_file, task_queue))
    else:
        input_proc = Process(target=generate_chunks_noindex,
                             args=(wiki_dump, task_queue))

    for i in range(NUMBER_OF_PROCESSES):
        processes.append(Process(target=worker, args=(task_queue, done_queue, i)))

    output_proc = Process(target=handle_result, args=(done_queue, final_db,
                                                      links_db, page_category_db,
                                                      infobox_category_file, batch_size,
                                                      drop_and_vacuum, filter_red_links))

    input_proc.start()
    for p in processes:
        p.start()
    output_proc.start()

    input_proc.join()

    # Tell child processes to stop
    for i in range(NUMBER_OF_PROCESSES):
        task_queue.put('STOP')

    for p in processes:
        p.join()

    done_queue.put('STOP')
    output_proc.join()


@timeit(1)
def main():
    # How many processes should be use at maximum?
    max_num_processes = os.getenv('NUMBER_PROCESSES', None)
    if max_num_processes is not None:
        max_num_processes = int(max_num_processes)

    # Check the environment variable for whether the temporarily table should be dropped and VACUUM should be performed or not
    drop_and_vacuum = os.getenv('DROP_AND_VACUUM', '')
    if drop_and_vacuum.lower() == 'true':
        drop_and_vacuum = True
    else:
        drop_and_vacuum = False

    # Check the environment variable for whether "red links" (= links with link targets for which ni article page exists yet) should be filtered out or not
    filter_red_links = os.getenv('FILTER_RED_LINKS', '')
    if filter_red_links.lower() == 'true':
        filter_red_links = True
    else:
        filter_red_links = False

    # The input and output directories
    input_directory = os.getenv('INPUT_DIRECTORY', 'input_aliasmap')
    output_directory = os.getenv('OUTPUT_DIRECTORY', 'output_aliasmap')

    # Check the environment variable for the filename of the aliasmap database
    print(os.path.join(PATH_PREFIX, output_directory, os.getenv('ALIASMAP_DB', 'aliasmap.db')))
    final_db = Database(
        os.path.join(PATH_PREFIX, output_directory, os.getenv('ALIASMAP_DB', 'aliasmap.db')),
        create_anew=True
    )

    # Check the environment variable for the filename of the links database
    links_db_name = os.getenv('LINKS_DB', '')
    if len(links_db_name) > 1:
        links_db = Database(
            os.path.join(PATH_PREFIX, output_directory, links_db_name),
            create_anew=True
        )
    else:
        links_db = None

    # Check the environment variable for the filename of the page categories database
    page_category_db_name = os.getenv('PAGE_CATEGORY_DB', '')
    if len(page_category_db_name) > 1:
        page_category_db = Database(
            os.path.join(PATH_PREFIX, output_directory, page_category_db_name),
            create_anew=True
        )
    else:
        page_category_db = None

    # Check the environment variable for the filename of the infobox categories file
    infobox_category_file_name = os.getenv('INFOBOX_CATEGORY_FILE', '')
    if len(infobox_category_file_name) > 1:
        infobox_category_file = os.path.join(PATH_PREFIX, output_directory, infobox_category_file_name)
    else:
        infobox_category_file = None

    index_file = os.getenv('INDEX_FILE', '')

    start(os.path.join(PATH_PREFIX, input_directory, os.getenv('INPUT_FILE', '')),
          (os.path.join(PATH_PREFIX, input_directory, index_file)) if len(index_file) > 0 else '',
          final_db, links_db, page_category_db, infobox_category_file,
          batch_size=15000, max_num_processes=max_num_processes,
          drop_and_vacuum=drop_and_vacuum, filter_red_links=filter_red_links)


if __name__ == '__main__':
    main()
