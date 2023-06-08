""" Johanna Götz """

import bz2
import logging
import sys
import time
import re
import traceback
from multiprocessing import Queue
from unicodedata import normalize


def timeit(repeats):
    def timed_func(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            for _ in range(repeats):
                result = func(*args, **kwargs)
            end = time.time()
            logging.critical('%r: %2.2f ms' % (func.__name__,
                             (end - start) * 1000))
            return result
        return wrapper
    return timed_func


# Parse the wiki dump index file
def parse_index(index_file):
    offsets = []
    # Read all the index data and get the offsets
    # The offset is always the same for 100 articles at a time
    with bz2.open(index_file, 'rt', encoding='UTF-8', newline='\n') as index:
        for line in index:
            offset, _, _ = line.strip().split(':', maxsplit=2)
            offsets.append(int(offset))
    offset_ranges = []
    offset_range_start = offsets[0]
    # Get the pairs of first offset and last offset for each process, also add the number of articles
    for offset in offsets:
        if offset > offset_range_start:
            offset_ranges.append((offset_range_start, offset,
                                  offset - offset_range_start))
            offset_range_start = offset
    offset_ranges.append((offset_range_start, None, -1))
    return offset_ranges


# Extract a chunk defined by the offset range
def parse_xml_multi(wiki_dump, offset_range, task_queue):
    logging.warning(repr(offset_range))
    try:
        with open(wiki_dump, 'rb') as bz2_file:
            bz2_file.seek(offset_range[0])
            compressed_content = bz2_file.read(offset_range[2])
            decompressed_content = bz2.decompress(compressed_content).decode()
            if offset_range[2] == -1:
                # Cut off the final closing mediawiki tag
                end_pos = decompressed_content.rfind('</mediawiki>')
                try:
                    decompressed_content = decompressed_content[:end_pos]
                except:
                    pass
            # Add a new root tag for the block
            task_queue.put((offset_range, '<mediawiki>\n%s\n</mediawiki>\n' % (decompressed_content,)))
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        logging.critical(e)
        logging.critical(traceback.format_exc())
        sys.exit(1)


# Generate chunks of the dump using the offset ranges given in the index file
def generate_chunks(wiki_dump, index_file, task_queue):
    offset_ranges = parse_index(index_file)
    for offset_range in offset_ranges:
        parse_xml_multi(wiki_dump, offset_range, task_queue)


# Generate chunks from a file when no index file is given
# In this case, one chunk is exactly one page
def generate_chunks_noindex(wiki_dump, task_queue):
    logging.critical(wiki_dump)
    # Handle normal text files
    if wiki_dump.endswith('.txt') or wiki_dump.endswith('.xml'):
        try:
            with open(wiki_dump, 'r') as input_file:
                page_content = input_file.read()
            # It seems to be a Wikipedia page
            if page_content.strip('\r\n').startswith('<mediawiki>'):
                task_queue.put((None, page_content))
            # It's just text
            else:
                logging.critical('<mediawiki>\n<page>\n<ns>0</ns>\n<title></title>\n<text>\n'
                                 + page_content
                                 + '\n</text>\n</page>\n</mediawiki>\n')
                task_queue.put((None, '<mediawiki>\n<page>\n<ns>0</ns>\n<title></title>\n<text>\n'
                                + page_content
                                + '\n</text>\n</page>\n</mediawiki>\n'))
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            sys.exit(1)
    # Handle bz2 files
    else:
        try:
            page_start = bytes('<page>', encoding='utf-8')
            wiki_end = bytes('</mediawiki>', encoding='utf-8')
            page_content = None
            with bz2.BZ2File(wiki_dump, 'rb') as xml_file:
                for chunk in xml_file:
                    found_start = chunk.find(page_start)
                    found_end = chunk.find(wiki_end)
                    # Neither the start of a page nor the end of the whole dump has been encountered
                    if found_start < 0 and found_end < 0:
                        # Since there's some stuff before the first page,
                        # we have to ignore anything that comes before the first page has started
                        # which will be the case at a position > 0
                        # There is an ongoing page to which the chunk is added
                        if page_content is not None:
                            page_content += chunk.decode()
                    else:
                        # We just found a regular page start
                        if found_end < 0:
                            # There is an ongoing page
                            if page_content is not None:
                                page_content += chunk[:found_start].decode()
                                task_queue.put((None, '<mediawiki>\n%s\n</mediawiki>\n' % (page_content,)))
                            page_content = chunk[found_start:].decode()
                        # We're at the end of the whole wiki dump
                        else:
                            # There is an ongoing page
                            if page_content is not None:
                                page_content += chunk[:found_end].decode()
                                task_queue.put((None, '<mediawiki>\n%s\n</mediawiki>\n' % (page_content,)))
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            sys.exit(1)


# Return the LNRM representation of a string
# The "baumert" argument is for using Niklas Baumert's version of doing some stuff
# NFKC was chosen here but NFKD might work as well
def lnrm_repr(string, normalisation='NFKC', baumert=False):
    if baumert:
        clean_string = string.lower()
        chars = '!?.,-_ \\(){}[]#\t\n'
    else:
        # Normalise the unicode chars:
        # https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize
        # And use the LNRM definition from here (2.3):
        # https://www.researchgate.net/publication/265107266_Stanford-UBC_entity_linking_at_TAC-KBP
        clean_string = normalize(normalisation, string).lower()
        chars = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n '
    for c in chars:
        clean_string = clean_string.replace(c, '')
    return 'lnrm__' + clean_string


# Create the Wikipedia-style link name of a string
# Wikipedia links are case-sensitive except for the first letter
# https://en.wikipedia.org/wiki/Help:Link#Conversion_to_canonical_form
def wiki_format(string):
    spaces_replaced = re.sub(r'(\s|_)+', '_', string.strip())
    first_char = spaces_replaced[:1]
    first_char_upper = first_char.upper()
    # If the first char gets converted into more than one char,
    # keep the original as it was probably a weird special char
    # (like ß => SS which is not the title of the original page anymore)
    return (first_char_upper if len(first_char_upper) == 1 else first_char) + spaces_replaced[1:]
