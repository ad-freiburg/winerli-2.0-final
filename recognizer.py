import csv
import os
import re
import json
import time
import spacy
import spacy.symbols
from spacy.tokens import Token, Doc
from copy import deepcopy
from pprint import pprint

from database import Database
from wikilink import Wikilink
from entity import Entity
from wiki_parsing import *


# Use relative paths
PATH_PREFIX = ''
if os.name == 'nt':
    PATH_PREFIX = '.'


# Taken from Niklas Baumert's bachelor's thesis code
# (Original function: "get_gender_database")
# Get the gender data for entities
def load_gender_data(gender_db, source):
    """Load the gender.tsv into a dict that maps wikilinks of people to their gender.

    Args:
        param gender_db (dict): An (empty) dictionary to which the result data will be written.
        source (str): The name of a file containing tab-separated value pairs.
                      The first element is an entity name.
                      The second element is the gender.

    Returns:
        Nothing
    """
    with open(source, encoding='UTF-8') as file:
        reader = csv.reader(file, delimiter='\t', quoting=csv.QUOTE_ALL)
        for _, row in enumerate(reader):
            try:
                entity_name = row[0].replace('@en', '').strip()
                entity_gender = row[1].replace('@en', '').strip().split(' ')[0].lower()
                entity_name = wiki_format(entity_name)
                gender_db[entity_name] = entity_gender
            # Some lines might be broken
            except IndexError:
                logging.critical('Broken line:')
                logging.critical(str(_))
                logging.critical(repr(row))


# Based on Niklas Baumert's bachelor's thesis code
# (Original function: "get_category_data")
# Get the infobox categories that appear on the page for the entity
def load_infobox_category_data(infobox_cat_db, source, cleanup=False):
    """Load the infobox_category.tsv into a dict that maps wikilinks to a list of infobox categories.

    Args:
        infobox_cat_db (dict): An (empty) dictionary to which the result data will be written.
        source (str): The name of a file containing tab-separated value pairs.
                      The first element is a wikilink.
                      The second is a json-encoded list of infobox categories.

    Returns:
        Nothing
    """
    with open(source, encoding='UTF-8') as file:
        reader = csv.reader(file, delimiter='\t', quoting=csv.QUOTE_ALL)
        cleaned_categories = []
        for _, row in enumerate(reader):
            entity = row[0]
            categories = json.loads(row[1])
            # Clean up the category data
            if cleanup:
                cleaned_categories = []
                for category in categories:
                    # Filter out empty categories
                    if category == '':
                        continue
                    # Some infobox categories (ship, aircraft) use nested infoboxes
                    # and the topmost infobox has a name like "ship begin",
                    # so remove the " begin" part, so that only a usable category remains
                    elif category.endswith(' begin'):
                        cleaned_categories.append(category.split(' begin')[0])
                    elif category.endswith(' (new)'):
                        cleaned_categories.append(category.split(' (new)')[0])
                    else:
                        cleaned_categories.append(category)
            # Store the data
            infobox_cat_db[entity] = categories if len(cleaned_categories) == 0 else cleaned_categories


# Find all links and replace them by the link texts
# Also, return all the links as dictionary with their position as key
def find_filter_links(text, pos=0):
    rgx = re.compile(r'\[\[(?P<wikilink>[^<>\[\]{}|]+?)(?:\|(?P<linktext>.+?))?\]\]')
    link_dict = dict()
    category_links = list()
    found = rgx.search(text, pos)
    # As long as we find a link
    while found is not None:
        span = found.span()
        start_pos = span[0]
        end_pos = span[1]
        content = found.groupdict()
        # For anchor links, only use the page itself
        content['wikilink'] = content['wikilink'].split('#')[0]
        # If the display text is None, it's the same as the wikilink
        if content['linktext'] is None:
            content['linktext'] = content['wikilink']
        # Save category links separately and remove them from the text
        if content['wikilink'].startswith('Category:'):
            category_links.append(content)
            # Remove the link
            text = text[:start_pos] + text[end_pos:]
        else:
            link_dict[start_pos] = content
            # Replace the link
            text = text[:start_pos] + content['linktext'] + text[end_pos:]
        # Search for the next occurence
        pos = start_pos
        found = rgx.search(text, pos)
    return text.strip(), link_dict, category_links


# The actual recogniser
class EntityRecogniser:
    database = None
    links_db = None
    page_category_db = None
    gender_database = None
    category_database = None
    # The scoring factors consist of a tuple of 4 values, one for each of the approaches 2-5.
    #
    # If one of the factors for approach 2, 3 and 5 is smaller than 1, the approach will be disabled completely.
    # If the value is at least 1, it'll be used as a multiplier applied to the relevance score in case of the binary approaches (2, 3 and 5).
    # If the multiplier for approach 4 is 0, the approach will be disabled.
    #
    # For approach 4, the multiplier can be smaller than 1 and
    # it will always be multiplied with the overlap coefficient to which 1 has been added to get a number in the range of 1 and 2.
    # If the result is smaller than 1, it'll be set to 1, otherwise it'll be used as-is.
    # This allows to factor in the overlap coefficient to a lesser degree.
    scoring_factors = (0, 0, 0, 0)
    pronoun_data_template = {'it': '', 'he': '', 'she': ''}

    def __init__(self, nlp, threshold=0.5, use_adjectives=True, use_numbers=False,
                 use_nonbinary=False):
        self.category_data = dict()
        self.pronoun_data = deepcopy(self.pronoun_data_template)
        self.partial_entity_data = dict()
        self.nlp = nlp
        self.threshold = threshold
        self.all_links = None
        self.page_category_links = None
        self.trivially_linked_entities_by_lnrm = dict()
        self.trivially_linked_entities_by_wikilink = dict()
        self.page_title = None
        self.current_page_categories = None
        self.page_categories = dict()
        self.page_categories_overlap = dict()
        self.links_db_results = None
        self.entities_by_lnrm = dict()
        self.use_adjectives = use_adjectives
        self.use_numbers = use_numbers
        self.contains_links = True
        self.use_nonbinary = use_nonbinary
    
    def start(self, text, page_title):
        self.page_title = page_title
        # Add the current page to the trivially linked entities
        self.current_page_entity = None
        if len(self.page_title) > 0:
            lnrm = lnrm_repr(self.page_title)
            wikilink = wiki_format(self.page_title)
            self.current_page_entity = Entity(wikilink, None, None, None, None)
            self.trivially_linked_entities_by_lnrm[lnrm] = dict()
            self.trivially_linked_entities_by_lnrm[lnrm][wikilink] = self.current_page_entity
            self.trivially_linked_entities_by_wikilink[lnrm] = self.current_page_entity
        # Filter out the links
        cleaned_text, self.all_links, self.page_category_links = find_filter_links(text)
        # Does the text contain links?
        self.contains_links = (len(self.all_links) > 0)
        doc = self.nlp(cleaned_text)
        for sent_tokens in doc.sents:
            logging.warning('New sentence:' + repr(sent_tokens))
            entities = self._recognize(sent_tokens)
            yield (entities, sent_tokens.as_doc())
        # Reset the data dictionaries for the next doc.
        self.category_data.clear()
        self.pronoun_data.clear()
        self.pronoun_data = deepcopy(self.pronoun_data_template)
        self.partial_entity_data.clear()
        self.trivially_linked_entities_by_lnrm.clear()
        self.trivially_linked_entities_by_wikilink.clear()
        self.page_title = None
        self.current_page_categories = None
        self.page_categories.clear()
        self.page_categories_overlap.clear()
        self.links_db_results = None
        self.entities_by_lnrm.clear()

    def reset(self):
        # Reset the data dictionaries for the next doc.
        self.category_data.clear()
        self.pronoun_data.clear()
        self.pronoun_data = deepcopy(self.pronoun_data_template)
        self.partial_entity_data.clear()
    
    def _recognize(self, tokens):
        logging.warning('Recognition: Start recognition...')
        n = len(tokens)
        entities = [None for _ in range(n)]
        prev_link = None
        i = 0
        while i < n:
            # Process trivial entities which are entities that are directly linked
            token = tokens[i]
            str_pos = token.idx
            #token_len = len(token)
            link = self.all_links.get(str_pos, None)
            logging.warning('Recognition current token: "' + repr(token) + '"; Link? ' + repr(link))
            #print('Token:', '"' + token.text + '"', token.pos_, token.dep_, str_pos, 'Control: "' + my_string[str_pos:str_pos + len(token)] + '"', token_len, 'Link: ' + repr(link), sep=' # ')
            # If there is an ongoing link
            if prev_link is not None:
                prev_link_len = str_pos - prev_link.start_pos()
                logging.warning('Explicitly given link stuff: Pos: %s ----- Start pos: %s ----- Calculated len: %s ----- Real len: %s' % (str_pos, prev_link.start_pos(), prev_link_len, len(prev_link)))
                # Add the token if it belongs to the link text
                if prev_link_len < len(prev_link):
                    prev_link.add_token(token)
                    logging.warning('Recognition: Token is part of a link!')
                    i += 1
                    continue
                # The link is finished
                # Create the entity and add it
                else:
                    categories = self.category_database.get(prev_link.wikilink)
                    pronoun = self._pronoun_lookup(prev_link.wikilink)
                    entity = Entity(redirect, None, len(prev_link.tokens), categories, pronoun)
                    for position in range(start_i, i):
                        entities[position] = entity
                    # Add the entity with its LNRM representation
                    # to be able to find it again later when a subsequence with the same LNRM appears again
                    # Assumption:
                    # Usually, an entity is only explicitly linked the first time it is mentioned in the article.
                    # If the same text appears again, boost the relevance of the entity that this text linked to.
                    logging.warning('%s ~~~ %s' % (repr(tokens[start_i:i].text), repr(prev_link.linktext)))
                    lnrm = lnrm_repr(prev_link.linktext)
                    if lnrm not in self.trivially_linked_entities_by_lnrm:
                        self.trivially_linked_entities_by_lnrm[lnrm] = dict()
                    self.trivially_linked_entities_by_lnrm[lnrm][redirect] = (entities[i - 1])
                    # Add the entity with its wikilink
                    # to be able to find it again later when a subsequence appears
                    # for which one of the possible entities has already been linked to explicitly on the page
                    # Assumption:
                    # Usually, an entity is only explicitly linked the first time it is mentioned in the article.
                    # If there are several possible entities for the text, boost the one that had previously appeared as a link target.
                    self.trivially_linked_entities_by_wikilink[redirect] = entities[i - 1]
                    logging.info('Trivially linked by LNRM: ' + repr(self.trivially_linked_entities_by_lnrm) + '; trivially linked by wikilink: ' + repr(self.trivially_linked_entities_by_wikilink))
                    prev_link = None
                    logging.warning('Recognition: Link has ended.')
            # If we found a link, add the data and continue with the next token
            if link is not None:
                logging.warning('Recognition: Token is part of a link!')
                # Check if the wikilink is a redirect
                start_time = time.time()
                redirect_query = self.database.query(
                    """
                    SELECT `target`
                    FROM `redirects`
                    WHERE `wikilink` is ?
                    """,
                    (wiki_format(link['wikilink']),)
                )
                end_time = time.time()
                logging.warning('Redirect query took %2.2f ms' % ((end_time - start_time) * 1000))
                if len(redirect_query) > 0:
                    redirect = redirect_query[0][0]
                else:
                    redirect = wiki_format(link['wikilink'])
                # Only continue if the redirect doesn't lead to a disambiguation page
                if redirect != '__DISAMBIGUATION__':
                    prev_link = Wikilink(redirect, link['linktext'])
                    prev_link.add_token(token)
                    start_i = i
                    i += 1
                    continue
                else:
                    link['wikilink'] = '__DISAMBIGUATION__'

            # Create sub-sequences to check
            for j in range(i, n):
                # The current token belongs to an explicitly given link, so stop sub-sequence generation here
                # If we got in here because the current link links to a disambiguation page, don't repeat this
                if tokens[j].idx in self.all_links and self.all_links[tokens[j].idx]['wikilink'] != '__DISAMBIGUATION__':
                    logging.warning('Token "%s" is a link' % tokens[j].text)
                    i = j - 1
                    break

                sub_sequence = tokens[i:j + 1]
                logging.warning('Recognition: Current subsequence: "' + repr(sub_sequence) + '"; PoS: ' + repr(list(map(lambda x: x.pos_, sub_sequence))))

                # If a punctuation symbol at the beginning of the sub-sequence is encountered,
                # start a new sub-sequence
                if sub_sequence[0].pos in (spacy.symbols.PUNCT,):
                    logging.warning('Recognition: It\'s just punctuation.')
                    break
                
                # If the last token of the current sub-sequence is an adposition or a puncuation symbol,
                # the sequence should continue in order to not lose information
                if sub_sequence[-1].pos in (spacy.symbols.ADP, spacy.symbols.PUNCT):
                    logging.warning('Recognition: Ends in punctuation or an adposition.')
                    continue
                
                # If the sub-sequence has a "the", assume that it's (infobox) category information
                if i - 1 >= 0 and tokens[i - 1].pos == spacy.symbols.DET and tokens[i - 1].lower_ not in ('a', 'an'):
                    category = sub_sequence.text.lower()
                    logging.warning('Recognition: Subsequence might be a category. Possible categories: ' + repr(self.category_data.get(category, '[No categories found]')))
                    # Check if the category has been encountered already
                    if category in self.category_data:
                        entity = self.category_data[category]
                        # If there is an entity, assign it to the whole string (determiner + category name)
                        if entity:
                            for position in range(i - 1, j + 1):
                                entities[position] = entity
                            continue
                
                # The latest token in the sub-sequence should be a (proper) noun or a pronoun   
                # NOTE Change by Johanna: Keep leading adjectives
                if self.use_adjectives and not self.use_numbers:
                    if sub_sequence[-1].pos not in (spacy.symbols.NOUN, spacy.symbols.PROPN, spacy.symbols.PRON, spacy.symbols.ADJ):
                        i = j
                        logging.warning('Recognition: Subsequence doesn\'t end in a proper noun or adjective.')
                        break
                # Allow extending the subsequence with a number of it already has at least one element
                elif self.use_adjectives and self.use_numbers:
                    if sub_sequence[-1].pos not in (spacy.symbols.NOUN, spacy.symbols.PROPN, spacy.symbols.PRON, spacy.symbols.ADJ, spacy.symbols.NUM):
                        i = j
                        logging.warning('Recognition: Subsequence doesn\'t end in a proper noun, adjective or number.')
                        break
                elif self.use_numbers:
                    if sub_sequence[-1].pos not in (spacy.symbols.NOUN, spacy.symbols.PROPN, spacy.symbols.PRON, spacy.symbols.NUM):
                        i = j
                        logging.warning('Recognition: Subsequence doesn\'t end in a proper noun or number.')
                        break
                else:
                    if sub_sequence[-1].pos not in (spacy.symbols.NOUN, spacy.symbols.PROPN, spacy.symbols.PRON, ):
                        i = j
                        logging.warning('Recognition: Subsequence doesn\'t end in a proper noun.')
                        break

                # Check if there is an entity for that pronoun
                # If there is, use it and continue with the next sub-sequence.
                if sub_sequence[0].pos in (spacy.symbols.PRON,):
                    logging.warning('Recognition: Is there an entity for this pronoun? ' + repr(self.pronoun_data))
                    pronoun = sub_sequence[0].lower_
                    try:
                        entity = self.pronoun_data[pronoun]
                        if entity:
                            entities[i] = entity
                            break
                    except KeyError:
                        # If the sequence consists only of a pronoun,
                        # continue with the next iteration
                        if len(sub_sequence) == 1:
                            continue

                # Is the sub-sequence a partial name for a previous entity? If yes, use that.
                if sub_sequence[0].lower_ in self.partial_entity_data:
                    logging.warning('Recognition: Is the sub-sequence a partial name? ' + repr(self.partial_entity_data))
                    entities[i] = self.partial_entity_data[sub_sequence[0].lower_]

                # Get the LNRM representation of the current sub-sequence
                lnrm = lnrm_repr(sub_sequence.text.lower())

                # Get the result with the highest relevance for the given LNRM representation
                start_time = time.time()
                results = self.database.query(
                    """
                    SELECT `wikilink`, `relevance`
                    FROM `aliasmap`
                    WHERE `lnrm` is ?
                    ORDER BY `relevance` DESC;
                    """,
                    (lnrm,)
                )
                end_time = time.time()
                logging.warning('Aliasmap query took %2.2f ms' % ((end_time - start_time) * 1000))
                logging.info('Recognition: Query the database:  ' + repr(results))
                # There was no result for this subsequence
                if results is None or len(results) == 0:
                    # When there's no result for the current sub-sequence,
                    # adding more words to it will most likely not improve the result.
                    # If the sub-sequence starts with an adjective, skip it and try with the rest.
                    if self.use_adjectives and sub_sequence[0].pos in (spacy.symbols.ADJ,):
                        # The i value doesn't need to be changed because the outer loop will increment it.
                        pass
                    # If the sub-sequence starts with an adposition or a pronoun,
                    # skip it and try with the rest
                    elif sub_sequence[0].pos in (spacy.symbols.ADP, spacy.symbols.PRON):
                        # The i value doesn't need to be changed because the outer loop will increment it.
                        pass
                    # Otherwise, skip to the last word as base for sub-sequences.
                    elif i < j:
                        # Decrement i because the outer loop will increment it again.
                        i = j - 1
                    break
                else:
                    # Save the results in a dictionary with wikilink as the key
                    # Set the score to the relevance initially
                    results_as_dict = dict()
                    for result in results:
                        results_as_dict[result[0]] = {'relevance': result[1], 'score': result[1]}

                logging.warning('Recognition: Approach 1: Most relevant database query result: %s' % repr(results[0]))

                # Approach 2:
                # Check if this exact sub-sequence had already appeared as a link text in an explicitly given link
                # Note: This approach is only relevant if the text contains links
                if self.contains_links and self.scoring_factors[0] > 1:
                    previously_linked_entities = self.trivially_linked_entities_by_lnrm.get(lnrm, None)
                    logging.warning('Recognition: Approach 2: The text "%s" with LNRM "%s" was previously explicitly linked to the following entities: %s' % (sub_sequence.text, lnrm, repr(None if previously_linked_entities is None else list(previously_linked_entities.values()))))
                    #logging.warning('Recognition: Approach 2: Previously linked entities: %s' % repr(previously_linked_entities))
                    # If it had appeared but doesn't have a relevance set already, get it from the query result and set it
                    if previously_linked_entities is not None:
                        for _, previously_linked_entity in previously_linked_entities.items():
                            # Multiply with the scoring factor
                            try:
                                results_as_dict[previously_linked_entity.wikilink]['score'] *= self.scoring_factors[0]
                            except Exception as e:
                                logging.critical('There is no result for wikilink %s. Please check if your aliasmap is out of date.' % (repr(previously_linked_entity.wikilink),))
                                logging.critical(repr(results_as_dict))
                                logging.critical(e)
                            logging.warning('Recognition: Approach 2: The entity with wikilink "%s" and relevance %s has previously appeared as a link. The new score is %s.' % (previously_linked_entity.wikilink, repr(results_as_dict[previously_linked_entity.wikilink]['relevance']), repr(results_as_dict[previously_linked_entity.wikilink]['score'])))

                # Approach 3:
                # Check which of the possible entities have appeared as link targets already in explicitly given links
                # Note: This approach is only relevant if the text contains links
                if self.contains_links and self.scoring_factors[1] > 1:
                    # Is the following line even necessary?
                    previously_seen_wikilinks = list(filter(lambda x: self.trivially_linked_entities_by_wikilink.get(x[0], None) is not None, results))
                    logging.warning('Recognition: Approach 3: The following entities have previously appeared in link targets: ' + repr(previously_seen_wikilinks))
                    # Multiply with the scoring factor
                    for possible_entity in results:
                        possible_entity_wikilink = possible_entity[0]
                        if possible_entity_wikilink in self.trivially_linked_entities_by_wikilink:
                            results_as_dict[possible_entity_wikilink]['score'] *= self.scoring_factors[1]
                            logging.warning('Recognition: Approach 3: The entity with wikilink "%s" and relevance %s has previously appeared as a link target. The new score is %s.' % (possible_entity_wikilink, repr(results_as_dict[possible_entity_wikilink]['relevance']), repr(results_as_dict[possible_entity_wikilink]['score'])))
                
                # Approach 4:
                # Check the overlap in page categories between the current page and the possible entities
                if self.scoring_factors[2] > 0 and len(self.page_title) > 0:
                     # Get the categories for the current page if it hasn't been set yet
                    if self.current_page_categories is None:
                        self.current_page_categories = set(json.loads(
                            self.page_category_db.query(
                                """
                                SELECT `categories`
                                FROM `categories`
                                WHERE `wikilink` is ?
                                """,
                                (self.page_title,)
                            )[0][0]
                        ))
                        logging.warning('Recognition: Approach 4: The current page belongs to the following categories: %s' % repr(self.current_page_categories))
                    # Get all possible entities who categories haven't already been retrieved 
                    entities_without_categories = [possible_entity[0] for possible_entity in results if possible_entity[0] not in self.page_categories]
                    # Get the categories
                    if len(entities_without_categories) > 0:
                        page_category_db_query_result = self.page_category_db.query(
                            """
                            SELECT `wikilink`, `categories`
                            FROM `categories`
                            WHERE `wikilink` IN (%s)
                            """ % ','.join('?' * len(entities_without_categories)),
                            entities_without_categories
                        )
                        # Set the categories and calculate the overlap
                        for page_category_result in page_category_db_query_result:
                            possible_entity_wikilink = page_category_result[0]
                            self.page_categories[possible_entity_wikilink] = set(json.loads(page_category_result[1]))
                            # Calculate the overlap between the current page's categories and each entity candidate's categories
                            # according to https://en.wikipedia.org/wiki/Overlap_coefficient
                            if possible_entity_wikilink not in self.page_categories_overlap:
                                divisor = min(len(self.current_page_categories), len(self.page_categories[possible_entity_wikilink]))
                                # Avoid the dreaded division by zero
                                if divisor == 0:
                                    overlap_coeff = 0
                                else:
                                    overlap_coeff = len(self.current_page_categories.intersection(self.page_categories.get(possible_entity_wikilink, set()))) / divisor
                                self.page_categories_overlap[possible_entity_wikilink] = overlap_coeff
                            logging.info('Recognition: Approach 4: The category overlap coefficient between the current page and possible entity "%s" is: %s' % (repr(possible_entity_wikilink), repr(self.page_categories_overlap[possible_entity_wikilink])))
                    # Calculate the scores
                    for possible_entity in results:
                        possible_entity_wikilink = possible_entity[0]
                        if possible_entity_wikilink in self.page_categories_overlap:
                            if self.page_categories_overlap[possible_entity_wikilink] > 0:
                                # Since the overlap is always between 0 and 1, 1 is added, so that by multiplying the value can only get larger
                                # The scoring value allows scaling of the influence of the overlap
                                # Since this can result in a value lower than 1, which would give a score smaller than the relevance, it has to be 1 at minimum
                                results_as_dict[possible_entity_wikilink]['score'] *= max(((self.scoring_factors[2] - 1) * self.page_categories_overlap[possible_entity_wikilink]) + 1, 1)
                                logging.warning('Recognition: Approach 4: Entity candidate "%s" with relevance %s now has score %s due to %s percent overlap' % (repr(possible_entity_wikilink), repr(results_as_dict[possible_entity_wikilink]['relevance']), repr(results_as_dict[possible_entity_wikilink]['score']), repr(self.page_categories_overlap[possible_entity_wikilink])))   

                # Approach 5:
                # For every possible entity that we found for the current LNRM,
                # check if any of them links to the current page
                # The idea behind this is that entities that might be related to each other also link to each other
                # Get all the pages that link to the current one
                if self.scoring_factors[3] > 1 and self.current_page_entity is not None:
                    if self.links_db_results is None:
                        self.links_db_results = set(
                            el[0] for el in self.links_db.query(
                                """
                                SELECT `wikilink`
                                FROM `links`
                                WHERE `links_to` is ?
                                """,
                                (self.page_title,)
                            )
                        )
                        logging.warning('Recognition: Approach 5: The following pages link to the current one: %s' % repr(self.links_db_results))
                    # If the entity links to the current page, give its relevance a boost of some kind
                    # Also, if the wikilink of an entity candidate is the same as the current page, boost it, too
                    for possible_entity in results:
                        possible_entity_wikilink = possible_entity[0]
                        if (possible_entity_wikilink in self.links_db_results) or (possible_entity_wikilink == self.current_page_entity.wikilink):
                            results_as_dict[possible_entity_wikilink]['score'] *= self.scoring_factors[3]
                            logging.warning('Recognition: Approach 5: The following entity candidate\'s page links to the current page: %s. The relevance is %s and the new score is %s.' % (repr(possible_entity_wikilink), repr(results_as_dict[possible_entity_wikilink]['relevance']), repr(results_as_dict[possible_entity_wikilink]['score'])))

                # Standard approach (approach 1):
                # Get the data from the query result that has the highest relevance score
                # Assumption: The more words make an entity, the more specific it is.
                specificity = len(sub_sequence)
                # Get the Entity with the maximum score
                max_score = 0
                max_score_wikilink = None
                for wikilink in results_as_dict:
                    if results_as_dict[wikilink]['score'] > max_score:
                        max_score = results_as_dict[wikilink]['score']
                        max_score_wikilink = wikilink
                #logging.warning('Recognition: All of the possible entities:  ' + repr(results_as_dict))
                # Reject the entity with the highest score if the score doesn't exceed the threshold
                logging.warning('Recognition: Max score:  %s; max score wikilink: %s; threshold: %s' % (repr(max_score), repr(max_score_wikilink), repr(self.threshold)))
                if max_score < self.threshold:
                    continue
                # Create the entity
                categories = self.category_database.get(max_score_wikilink)
                pronoun = self._pronoun_lookup(max_score_wikilink)
                data = Entity(max_score_wikilink, results_as_dict[max_score_wikilink]['relevance'], specificity, categories, pronoun, results_as_dict[max_score_wikilink]['score'])
                logging.warning('Recognition: Here\'s our current entity for the text "%s":  %s' %(repr(sub_sequence), repr(data)))
                logging.warning('Recognition: Another entity for this text could be: "%s"' %(repr(entities[i]), ))

                # Add the category data
                if categories is not None:
                    for category in categories:
                        self.category_data[category] = data
                        # Split the categories into single words and assign the data, too
                        words = category.split(' ')
                        if len(words) > 1:
                            for word in words:
                                self.category_data[word] = data
                
                # Add the pronoun data
                if pronoun is not None:
                    self.pronoun_data[pronoun] = data

                # Associate partial names with the entity.
                # This is only done for select pronouns because 'it' is only used
                # when no gender data could be found
                if len(sub_sequence) > 1 and pronoun in ('he', 'she', 'o'):
                    # The pronoun condition limits partially named entities to just people.
                    for word in sub_sequence:
                        stored_data = self.partial_entity_data.get(word.lower_)
                        # If there is no data stored yet for this part of the sub-sequence,
                        # store it
                        if stored_data is None:
                            self.partial_entity_data[word.lower_] = data
                        # If there is stored data but it is less specific, replace it
                        else:
                            if stored_data.specificity < specificity:
                                self.partial_entity_data[word.lower_] = data
                            elif stored_data.specificity == specificity and stored_data.score <= max_score:
                                self.partial_entity_data[word.lower_] = data

                # Save the entity to the entities list.
                for position in range(i, j + 1):
                    stored_data = entities[position]
                    if stored_data is None:
                        entities[position] = data
                    else:
                        if stored_data.specificity < specificity:
                            entities[position] = data
                        elif stored_data.specificity == specificity and stored_data.score <= max_score:
                            entities[position] = data
            i += 1
        return entities

    def _pronoun_lookup(self, entity):
        try:
            gender = self.gender_database[entity]
        except KeyError:
            return 'it'
        if gender == 'male':
            return 'he'
        elif gender == 'female':
            return 'she'
        elif self.use_nonbinary and gender == 'non-binary':
            return 'they'
        else:
            return 'o'
