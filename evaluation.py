""" Johanna Götz """
""" Code partially taken and adapted from Niklas Baumert's thesis code """

import csv
import logging
import os
from wiki_parsing import *
from database import Database
from recognizer import *
from entity_recognition import *
from evaluation_classes import *


# Use relative paths
PATH_PREFIX = ''
if os.name == 'nt':
    PATH_PREFIX = '.'

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(stream=sys.stdout, level=LOGLEVEL)


# Collect all evaluation results
overall_eval_results = list()


# Taken from Niklas Baumert's evaluation code
def my_mappings(map_file):
    my_conll_map = dict()
    my_gmb_map = dict()
    with open(map_file, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        _ = reader.__next__()  # get header line and ignore it
        for line in reader:
            cat, conll, gmb, = line[:3]
            my_conll_map[cat] = conll
            my_gmb_map[cat] = gmb

    def conll_map(category):
        return my_conll_map.get(category, '')

    def gmb_map(category):
        return my_gmb_map.get(category, '')
    return {'conll': conll_map, 'gmb': gmb_map}


# Taken from Niklas Baumert's evaluation code
def spacy_gmb_mapping():
    spacy_map = {
        'PERSON': 'per',
        'NORP': 'gpe',
        'FAC': 'geo',
        'ORG': 'org',
        'GPE': 'gpe',
        'LOC': 'geo',
        'PRODUCT': '',
        'EVENT': 'eve',
        'WORK_OF_ART': '',
        'LAW': '',
        'LANGUAGE': '',
        'DATE': 'tim',
        'TIME': 'tim',
        'PERCENT': '',
        'MONEY': '',
        'QUANTITY': '',
        'ORDINAL': '',
        'CARDINAL': '',
        'PER': 'per',
        'MISC': ''
    }
    """
    PERSON	People, including fictional.
    NORP	Nationalities or religious or political groups.
    FAC	Buildings, airports, highways, bridges, etc.
    ORG	Companies, agencies, institutions, etc.
    GPE	Countries, cities, states.
    LOC	Non-GPE locations, mountain ranges, bodies of water.
    PRODUCT	Objects, vehicles, foods, etc. (Not services.)
    EVENT	Named hurricanes, battles, wars, sports events, etc.
    WORK_OF_ART	Titles of books, songs, etc.
    LAW	Named documents made into laws.
    LANGUAGE	Any named language.
    DATE	Absolute or relative dates or periods.
    TIME	Times smaller than a day.
    PERCENT	Percentage, including "%".
    MONEY	Monetary values, including unit.
    QUANTITY	Measurements, as of weight or distance.
    ORDINAL	"first", "second", etc.
    CARDINAL	Numerals that do not fall under another type.

    PER	Named person or family.
    LOC	Name of politically or geographically defined location (cities, provinces, countries, international regions, bodies of water, mountains).
    ORG	Named corporate, governmental, or other organizational entity.
    MISC	Miscellaneous entities, e.g. events, nationalities, products or works of art.
    """

    def mapping(category):
        return spacy_map.get(category, '')
    return mapping


# Taken from Niklas Baumert's evaluation code
def spacy_conll_mapping():
    spacy_map = {
        'PERSON': 'person',
        'NORP': 'organization',
        'FAC': 'location',
        'ORG': 'organization',
        'GPE': 'organization',
        'LOC': 'location',
        'PRODUCT': 'misc',
        'EVENT': 'misc',
        'WORK_OF_ART': 'misc',
        'LAW': 'misc',
        'LANGUAGE': 'misc',
        'DATE': 'misc',
        'TIME': 'misc',
        'PERCENT': 'misc',
        'MONEY': 'misc',
        'QUANTITY': 'misc',
        'ORDINAL': 'misc',
        'CARDINAL': 'misc',
        'PER': 'person',
        'MISC': 'misc'
    }

    def mapping(category):
        return spacy_map.get(category, '')
    return mapping


# Taken from Niklas Baumert's evaluation code and adapted to work with my code
def measure_metrics(sent_gold, my_answers, spacy_answers, my_mapping=lambda x: x,
                    spacy_mapping=lambda x: x):
    logging.warning('Sent gold: ' + repr(sent_gold))
    logging.warning('My answers: ' + repr(my_answers))
    logging.warning('Spacy answers: ' + repr(map(lambda x: x.orth_, spacy_answers)))
    my_detection = Metric()
    my_tag = Metric()
    my_linking = Metric()
    spacy_detection = Metric()
    spacy_tag = Metric()
    for sent_idn in range(len(sent_gold)):
        logging.warning('Sentence/document %s:' % (sent_idn,))
        logging.warning('Send gold: %s' % (repr(sent_gold[sent_idn]),))
        logging.warning('My answers: %s' % (repr(my_answers[sent_idn]),))
        logging.warning('Spacy answers: %s' % (
            str(list(map(lambda x: x.orth_, spacy_answers[sent_idn]))),)
        )
        spacy_entities = [ent.orth_ for ent in spacy_answers[sent_idn].ents]
        logging.warning('Spacy entities: %s' % (repr(spacy_answers[sent_idn].ents),))
        # The wiki data contains the page title, so the second element is needed
        if type(sent_gold[sent_idn]) == tuple:
            gold_tokens = sent_gold[sent_idn][1]
        # GMB contains the tokens directly
        else:
            gold_tokens = sent_gold[sent_idn]
        for token_idn in range(len(gold_tokens)):
            gold_token = gold_tokens[token_idn]
            spacy_token = spacy_answers[sent_idn][token_idn]
            logging.warning('Spacy token stuff: %s' % (repr(spacy_token.ent_type_), ))
            try:
                my_token = my_answers[sent_idn][token_idn]
            except IndexError:
                logging.warning('~~~ IndexError:')
                logging.warning(repr(my_answers[sent_idn]))
                logging.warning(repr(token_idn))
                logging.warning('~~~~~~~~~~~~')
            logging.warning('Current tokens: gold: %s; mine: %s; spacy: %s' % (
                repr(gold_token), repr(my_token), repr(spacy_token))
            )
            # Entity detection
            if (gold_token.tag and gold_token.tag != 'O') or gold_token.link:
                logging.warning('Check for detected entities: %s ~~~ %s ~~~ %s' % (
                    repr(gold_token), repr(my_token), repr(spacy_token.orth))
                )
                if my_token:
                    my_detection.tp += 1
                else:
                    my_detection.fn += 1
                if spacy_token.orth_ in spacy_entities:
                    spacy_detection.tp += 1
                else:
                    spacy_detection.fn += 1
            else:
                if my_token:
                    my_detection.fp += 1
                if spacy_token.orth_ in spacy_entities:
                    spacy_detection.fp += 1
            # Get the categories
            if my_token and my_token.categories is not None:
                category = my_token.categories
            else:
                category = [None]
            # Entity categorization
            if gold_token.tag and gold_token.tag != 'O':
                gold_tag = gold_token.tag.split('-')[-1]
                # Use both categories and use map with my_mapping to get all mapped categories
                logging.warning('Categories: %s maps to %s; Spacy category: %s; Expected category: %s' % (
                    repr(category), repr(list(map(my_mapping, category))),
                    repr(spacy_mapping(spacy_token.ent_type_)), repr(gold_tag))
                )
                if my_token and (gold_tag in map(my_mapping, category)):
                    my_tag.tp += 1
                else:
                    my_tag.fn += 1
                spacy_ent_type = spacy_mapping(spacy_token.ent_type_)
                if gold_tag == spacy_ent_type:
                    spacy_tag.tp += 1
                else:
                    spacy_tag.fn += 1
            else:
                if my_token and category[0] is not None:
                    my_tag.fp += 1
                if spacy_token.ent_type_:
                    spacy_tag.fp += 1
            # Entity Linking
            # Spacy has no EL functionality.
            if gold_token.link:
                logging.warning('My link: "%s"; expected link: "%s"' % (repr(my_token.wikilink) if my_token is not None else 'NONE', repr(wiki_format(gold_token.link))))
                # The wiki format function is used here for better invariance
                if my_token and wiki_format(gold_token.link) == my_token.wikilink:
                    my_linking.tp += 1
                else:
                    my_linking.fn += 1
            else:
                if my_token and my_token.wikilink:
                    my_linking.fp += 1
    return my_detection, my_tag, my_linking, spacy_detection, spacy_tag


# Taken from Niklas Baumert's thesis code (former name: "results")
# but in a separate function and with more functionality
def print_results(expected_results, my_answers, spacy_answers, my_mapping,
                  spacy_mapping, scoring_factors, threshold, use_adjectives,
                  use_numbers, dataset):
    (my_detection, my_tag, my_linking,
     spacy_detection, spacy_tag) = measure_metrics(expected_results, my_answers,
                                                   spacy_answers, my_mapping,
                                                   spacy_mapping)
    # Create the evaluation values objects and collect all results
    global overall_eval_results
    overall_eval_results.extend([
        EvalVals('detection', 'winerli', dataset, scoring_factors, threshold,
                 use_adjectives, use_numbers, my_detection),
        EvalVals('categorization', 'winerli', dataset, scoring_factors,
                 threshold, use_adjectives, use_numbers, my_tag),
        EvalVals('linking', 'winerli', dataset, scoring_factors, threshold,
                 use_adjectives, use_numbers, my_linking),
        EvalVals('detection', 'spacy', dataset, *(['N/A'] * 4), spacy_detection),
        EvalVals('categorization', 'spacy', dataset, *(['N/A'] * 4), spacy_tag),
        EvalVals('linking', 'spacy', dataset, *(['N/A'] * 4), None)
    ])
    # Print everything
    print('=' * 30)
    print('Results using the following settings:')
    print('Dataset: ' + dataset)
    print('Scoring factors: ' + repr(scoring_factors))
    print('Threshold: ' + repr(threshold))
    print('Use adjectives: ' + repr(use_adjectives))
    print('Use numbers: ' + repr(use_numbers))
    print('=' * 30)
    print('My Solution:')
    print('-' * 30)
    print('Detection')
    my_detection.print_metrics()
    print('Categorization')
    my_tag.print_metrics()
    print('Linking')
    my_linking.print_metrics()
    print()
    print('=' * 30)
    print('Spacy:')
    print('-' * 30)
    print('Detection')
    spacy_detection.print_metrics()
    print('Categorization')
    spacy_tag.print_metrics()
    print('Linking')
    print('Spacy doesn\'t do EL')
    print('=' * 30)


# Generate a markdown table from the collected evaluation results
def generate_markdown_tables(eval_results):
    sorted_results = sorted(eval_results, key=lambda x: (x.task, x.system,
                                                         x.dataset, x.scoring,
                                                         x.adjectives, x.numbers))
    # Turn the dataset into a nice string
    datasets = {'GMB: /evaluation/input/ner_dataset.csv': 'GMB-Walia',
                'Wikipedia: /evaluation/input/Wikipedia_NER_EL_with_links_fullarticles.tsv': 'Wikipedia w/ links',
                'Wikipedia: /evaluation/input/Wikipedia_NER_EL.tsv': 'Wikipedia w/o links'}
    # Turn the system information into a nice string
    systems = {'winerli': 'WiNERLi 2.0', 'spacy': 'SpaCy 3.2.4'}
    # Turn (adjectives, numbers) into a string
    options = {(False, False): 'w/o a/n.', (False, True): 'w/o adj.',
               (True, False): 'w/o num.', (True, True): ''}
    result_tables = dict()
    line_template = '| {:19.19s} | {:11.11s} | {:9.9s} | {:36.36s} | {:9.9s} | {:6.6s} | {:6.6s} |\n'
    for result in sorted_results:
        system_name = systems[result.system]
        # Add the table lines for each task
        try:
            scoring_line = '`{:s}` {:s}'.format(
                str(result.scoring), options[(result.adjectives, result.numbers)]
            )
        except:
            scoring_line = 'N/A'
        # Fill in the metrics
        if result.metrics is not None:
            line = line_template.format(
                datasets[result.dataset], system_name,
                str(result.threshold), str(scoring_line),
                str(result.metrics.precision), str(result.metrics.recall),
                str(result.metrics.f1)
            )
        else:
            line = line_template.format(
                datasets[result.dataset], system_name, *tuple('N/A' for _ in range(5))
            )
        # Create dictionaries

        if result.task not in result_tables:
            result_tables[result.task] = dict()
        if system_name not in result_tables[result.task]:
            result_tables[result.task][system_name] = ''
        # Add the line
        result_tables[result.task][system_name] += line
    # Add header lines to each table
    for task in result_tables:
        for system_name in result_tables[task]:
            title = '{:s}:\n\n'.format(task.capitalize())
            header = line_template.format('Dataset', 'System', 'Threshold', 'Scoring factors',
                                          'Precision', 'Recall', 'F1')
            separator = line_template.format(*tuple('-' * 50 for _ in range(7)))
            table_head = title + header + separator
            result_tables[task][system_name] = table_head + result_tables[task][system_name]
    return result_tables


# Load the annotated handcrafted Wikipedia-based evaluation set
# Adapted from Niklas Baumert's evaluation code with adjustments to work with my code
# and the improvement of using the whole text as one instead of split into sentences
def load_annotated_wiki(handcrafted_evaluation_set, contains_spaces):
    raw_data = handcrafted_evaluation_set
    with open(raw_data, 'r') as file:
        # Build the full sentence from the words in the file
        sentences_data = list()
        reader = csv.reader(file, delimiter='\t', quoting=csv.QUOTE_NONE)
        # One line consists of a word, the corresponding entity (if there's one)
        # and the entity's category (if there's one)
        for line in reader:
            if len(line) == 4:
                word, link, tag = line
            else:
                word, link, tag = line
            if not word:
                if link:
                    page_title = link.replace('_', ' ')
                    sentences_data.append((page_title, list()))
                    continue
                else:
                    continue
            sentences_data[-1][1].append(Token(word, '', tag, link))
    sentences_text = list()
    # Turn the parsed word data into fulltext sentences
    for page_title, tokens in sentences_data:
        sentences_text.append(['', ''])
        sentences_text[-1][0] = page_title
        sentences_text[-1][1] += (' ' if not contains_spaces else '').join([x.word for x in tokens]).replace(' \'s', '\'s')
    # Return the parsed sentence data and the sentences as a simple text
    return sentences_data, sentences_text


# Load the GMB evaluation set
# Adapted from Niklas Baumert's evaluation code with adjustments
def load_gmb(gmb_evaluation_set):
    raw_data = gmb_evaluation_set
    with open(raw_data, 'r', encoding='latin-1') as file:
        reader = csv.reader(file)
        reader.__next__()  # Read the header line and ignore it
        sentences_data = list()
        sent_num = 0
        for line in reader:
            sentence, word, pos, tag = line
            if sentence:
                _, sent_num = sentence.split(' ')
                sent_num = int(sent_num)
                sentences_data.append(list())
            sentences_data[sent_num - 1].append(Token(word, pos, tag, ''))
    sentences_text = list()
    for sent in sentences_data:
        # This is used to give the data the same shape as the Wikipedia data
        sentences_text.append(['', ''])
        sentences_text[-1][1] += ' '.join([x.word for x in sent])
    return sentences_data, sentences_text


@timeit(1)
def recognition_results(aliasmap_db, page_category_db, links_db,
                        category_db, gender_db, scoring_factors, threshold,
                        use_adjectives, use_numbers, nlp, text):
    # Set up the entity recogniser
    er = EntityRecogniser(nlp, threshold, use_adjectives=use_adjectives,
                          use_numbers=use_numbers, use_nonbinary=False)
    er.database = aliasmap_db
    er.page_category_db = page_category_db
    er.links_db = links_db
    er.gender_database = gender_db
    er.category_database = category_db
    er.scoring_factors = scoring_factors
    # Go through all the article pages
    my_answers = list()
    for pair in text:
        page_title = pair[0]
        page_text = pair[1]
        recognition_result = clean_recognise(page_title, page_text, er, 1)
        # Collect all results
        collected_results = []
        for result in recognition_result:
            # Only append the entities, not the sentences
            collected_results += result[0]
        # Collect all entity recognition results
        logging.warning(repr('Collect answers...'))
        my_answers.append(collected_results)
    return my_answers


def start(logfile_name,
          aliasmap_db, page_category_db, links_db, infobox_category_file_name,
          gender_data_file_name, scoring_factors, threshold, use_adjectives,
          use_numbers, evaluation_sets,
          contains_spaces, category_map):

    # Load gender data
    gender_db = dict()
    load_gender_data(gender_db, gender_data_file_name)
    # Load category data
    category_db = dict()
    load_infobox_category_data(category_db, infobox_category_file_name, cleanup=True)
    # Load spaCy
    nlp = spacy.load('en_core_web_sm')
    # Avoid splitting at apostrophes
    nlp.tokenizer.rules = {key: value for key, value in nlp.tokenizer.rules.items() if "'" not in key and "’" not in key and "‘" not in key}
    # How many characters spacy will handle. 1M char ~ 1GB RAM.
    nlp.max_length = 3000000

    # Run the evaluation for each evaluation set
    for eval_set in evaluation_sets:
        if eval_set['type'] == 'wikipedia':
            wiki_data, wiki_text = load_annotated_wiki(eval_set['set'], eval_set['contains_spaces'])
        elif eval_set['type'] == 'gmb':
            gmb_data, gmb_text = load_gmb(eval_set['set'])

        my_answers = recognition_results(aliasmap_db, page_category_db, links_db,
                                         category_db, gender_db, scoring_factors,
                                         threshold, use_adjectives, use_numbers,
                                         nlp, wiki_text)
        logging.debug('My answers: ' + repr(my_answers))
        logging.debug('Expected result: ' + repr(wiki_data))

        # Wiki evaluation
        if eval_set['type'] == 'wikipedia':
            print('Hand-annotated Wikipedia')
            logging.warning('Hand-annotated Wikipedia')
            # Mappings for Wikipedia and for Spacy
            my_mapping = my_mappings(category_map)['conll']
            spacy_mapping = spacy_conll_mapping()
            # Spacy's categorization
            spacy_answers = list()
            for pair in wiki_text:
                # Spacy requires the pre-cleaned text
                cleaned_text, _, _ = find_filter_links(pair[1])
                spacy_answers.append(nlp(cleaned_text))
            logging.debug(repr(spacy_answers))
            logging.debug('~~~ Tag: ' + repr(spacy_answers[0][1].tag))
            # Results
            print_results(wiki_data, my_answers, spacy_answers, my_mapping,
                          spacy_mapping, scoring_factors, threshold, use_adjectives,
                          use_numbers, 'Wikipedia: %s' % str(eval_set['set']))

        elif eval_set['type'] == 'gmb':
            logging.debug('~~~ GMB text: ' + repr(gmb_text))
            # GMB evaluation
            my_answers = recognition_results(aliasmap_db, page_category_db, links_db,
                                             category_db, gender_db, scoring_factors,
                                             threshold, use_adjectives, use_numbers,
                                             nlp, gmb_text)
            print('Annotated Corpus for Named Entity Recognition from '
                  'kaggle.com/abhinavwalia95/entity-annotated-corpus/home')
            logging.warning('Annotated Corpus for Named Entity Recognition from '
                            '')
            # Mappings for GMB and for Spacy
            my_mapping = my_mappings(category_map)['gmb']
            spacy_mapping = spacy_gmb_mapping()
            # Spacy's categorization
            spacy_answers = list()
            for pair in gmb_text:
                spacy_answers.append(nlp(pair[1]))
            # Results
            print_results(gmb_data, my_answers, spacy_answers, my_mapping,
                          spacy_mapping, scoring_factors, threshold, use_adjectives,
                          use_numbers, 'GMB: %s' % str(eval_set['set']))


@timeit(1)
def main():
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
        threshold = int(os.getenv('THRESHOLD', ''))
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

    # Check the environment variable for whether the tokens have spaces at the end of not
    # This is needed to be able to create sentences again from the single tokens
    contains_spaces = os.getenv('CONTAINS_SPACES', '')
    if contains_spaces.lower() == 'true':
        contains_spaces = True
    else:
        contains_spaces = False

    # Check the environment variable for which evaluation sets should be used
    try:
        evaluation_sets = eval(os.getenv('EVALUATION_SETS', '').lower())
    except:
        evaluation_sets = ['wikipedia', 'gmb']

    # Check the environment variable for the gender data file name
    gender_data_file_name = os.path.join(
        PATH_PREFIX + '/evaluation/databases', os.getenv('GENDER_DATA_FILE', 'gender_data.tsv')
    )

    # Check the environment variable for the infobox category file name
    infobox_category_file_name = os.path.join(
        PATH_PREFIX + '/evaluation/databases', os.getenv('INFOBOX_CATEGORY_FILE', 'infobox_category.tsv')
    )

    # Check the environment variable for the database containing the categories each article belongs to
    page_category_db = Database(
        os.path.join(PATH_PREFIX + '/evaluation/databases', os.getenv('PAGE_CATEGORY_DB', 'page_category_db.db')),
        read_only=True
    )

    # Check the environment variable for the database containing data which article links to which other article
    links_db = Database(
        os.path.join(PATH_PREFIX + '/evaluation/databases', os.getenv('LINKS_DB', 'links_db.db')),
        read_only=True)

    # Check the environment variable for the aliasmap database
    aliasmap_db = Database(
        os.path.join(PATH_PREFIX + '/evaluation/databases', os.getenv('ALIASMAP_DB', 'aliasmap.db')),
        read_only=True)

    # Check the environment variable for the result table file
    result_table_file = os.path.join(
        PATH_PREFIX + '/evaluation/output', os.getenv('RESULT_TABLE_FILE', None)
    )

    # Check the environment variables for the evaluation sets and the category mapping
    wiki_evaluation_set = os.path.join(
        PATH_PREFIX + '/evaluation/input', os.getenv('WIKI_EVALUATION_SET', 'Wikipedia_NER_EL.tsv')
    )
    gmb_evaluation_set = os.path.join(
        PATH_PREFIX + '/evaluation/input', os.getenv('GMB_EVALUATION_SET', 'ner_dataset.csv')
    )
    category_map = os.path.join(
        PATH_PREFIX + '/evaluation/input', os.getenv('CATEGORY_MAP', 'category_map.csv')
    )

    # The settings for several evaluation sets
    multi_evaluation_sets = eval(os.getenv('MULTI_EVALUATION_SETS', 'None'))
    evaluation_sets = []
    # There are multiple evaluation sets with their own settings
    if multi_evaluation_sets is not None:
        for tup in multi_evaluation_sets:
            curr_eval_set = dict()
            # Default values
            curr_set = None
            curr_type = None
            curr_contains_spaces = contains_spaces
            # Set values
            for key, value in tup:
                if key == 'set':
                    curr_set = value
                elif key == 'type':
                    curr_type = value
                elif key == 'contains_spaces':
                    curr_contains_spaces = value
            # Add the set if all necessary settings are given
            if curr_set is not None and curr_type is not None and curr_contains_spaces is not None:
                curr_eval_set['set'] = os.path.join(PATH_PREFIX + '/evaluation/input', curr_set)
                curr_eval_set['type'] = curr_type
                curr_eval_set['contains_spaces'] = curr_contains_spaces
                evaluation_sets.append(curr_eval_set)
    # Use the regular settings
    else:
        for eval_set in evaluation_sets:
            curr_eval_set = dict()
            if eval_set == 'wikipedia':
                curr_eval_set['set'] = wiki_evaluation_set
                curr_eval_set['type'] = eval_set
                curr_eval_set['contains_spaces'] = contains_spaces
            elif eval_set == 'gmb':
                curr_eval_set['set'] = gmb_evaluation_set
                curr_eval_set['type'] = eval_set
                curr_eval_set['contains_spaces'] = contains_spaces
            evaluation_sets.append(curr_eval_set)

    logging.critical(evaluation_sets)

    multi_settings = eval(os.getenv('MULTI_SETTINGS', 'None'))
    if multi_settings is not None:
        for tup in multi_settings:
            # Default values
            curr_scoring_factors = scoring_factors
            curr_threshold = threshold
            curr_use_adjectives = use_adjectives
            curr_use_numbers = use_numbers
            # Set values
            for key, value in tup:
                if key == 'scoring_factors':
                    curr_scoring_factors = value
                elif key == 'threshold':
                    curr_threshold = value
                elif key == 'use_adjectives':
                    curr_use_adjectives = value
                elif key == 'use_numbers':
                    curr_use_numbers = value
            start(PATH_PREFIX + os.path.join('/log', logfile_name),
                  aliasmap_db, page_category_db, links_db,
                  infobox_category_file_name, gender_data_file_name,
                  scoring_factors=curr_scoring_factors,
                  threshold=curr_threshold,
                  use_adjectives=curr_use_adjectives,
                  use_numbers=curr_use_numbers,
                  evaluation_sets=evaluation_sets,
                  contains_spaces=contains_spaces,
                  category_map=category_map)

    else:

        start(PATH_PREFIX + os.path.join('/log', logfile_name),
              aliasmap_db, page_category_db, links_db,
              infobox_category_file_name, gender_data_file_name,
              scoring_factors=scoring_factors, threshold=threshold,
              use_adjectives=use_adjectives, use_numbers=use_numbers,
              evaluation_sets=evaluation_sets, contains_spaces=contains_spaces,
              category_map=category_map)
    # Close all databases
    page_category_db.close()
    links_db.close()
    aliasmap_db.close()
    # Create a result table
    if result_table_file is not None:
        global overall_eval_results
        overall_eval_results
        tables = generate_markdown_tables(overall_eval_results)
        with open(result_table_file, 'w') as outfile:
            for task in tables:
                for system_name in tables[task]:
                    outfile.write(tables[task][system_name])
                    outfile.write('\n\n')


if __name__ == '__main__':
    main()
