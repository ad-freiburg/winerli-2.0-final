""" Johanna Götz """
""" Code mostly taken from Niklas Baumert's thesis code """

import csv
import datetime
import os
import re
from wiki_parsing import wiki_format


def identity(link):
    return link


def merge(files_in, file_out, merge_function, remove_merged_files=False):
    offset = 0
    with open(file_out, 'w') as output:
        writer = csv.writer(output, delimiter='\t', quoting=csv.QUOTE_NONE,
                            quotechar='', escapechar='\\', lineterminator='\n')
        record_id = 0
        for file in sorted(files_in):
            print('Merging {} into {}...'.format(file, file_out))
            with open(file) as file_in:
                reader = csv.reader(file_in, delimiter='\t', quoting=csv.QUOTE_NONE)
                for line in reader:
                    record_id, row = merge_function(line, offset)
                    if row:
                        writer.writerow(row)
                offset = record_id
            if remove_merged_files:
                os.remove(file)
                print('Removed {}'.format(file))


def docs_file(line, offset):
    print(line)
    idn, sent = line
    idn = int(idn)
    record_id = offset + idn
    row = (record_id, sent)
    return record_id, row


def words_file(line, offset, converter_func):
    wikilink, is_entity, idn = line[:3]
    rest = line[3:]
    idn = int(idn)
    if int(is_entity) == 1:
        converted_link = converter_func(wikilink)
    else:
        converted_link = wikilink
    record_id = offset + idn
    if converted_link:
        row = tuple([converted_link, is_entity, record_id] + rest)
    else:
        row = ''
    return record_id, row


def start(file_overwrite, file_type, results_path, words_file_converter,
          suffix="-wikipedia", remove_merged_files=False,
          wordsfile_name='wordsfile_', docsfile_name='docsfile_'):
    timestamp = datetime.date.today().isoformat()
    if file_overwrite:
        remove_merged_files = False
        if file_type == 'docsfile':
            merge([file_overwrite],
                  os.path.join(results_path, 'docsfile-' + timestamp + '.tsv'),
                  docs_file, remove_merged_files)
        else:
            merge([file_overwrite],
                  os.path.join(results_path, 'wordsfile-' + timestamp + suffix + '.tsv'),
                  words_file_converter, remove_merged_files)
    else:
        docs_files = list()
        words_files = list()
        for file in os.listdir(results_path):
            if re.match(wordsfile_name, file):
                words_files.append(os.path.join(results_path, file))
            elif re.match(docsfile_name, file):
                docs_files.append(os.path.join(results_path, file))
        merge(docs_files, os.path.join(results_path, 'docsfile-' + timestamp + '.tsv'),
              docs_file)
        merge(words_files, os.path.join(results_path, 'wordsfile-' + timestamp + suffix + '.tsv'),
              words_file_converter)


def single_map(mapping):
    def convert(link):
        assert isinstance(link, str)
        link = link.replace('<', '').replace('>', '')
        try:
            result = mapping[link]
        except KeyError:
            return ''
        return '<' + result + '>'
    return convert


def double_map(first_mapping, second_mapping):
    def convert(link):
        assert (isinstance(link, str))
        link = link.replace('<', '').replace('>', '')
        try:
            first_result = first_mapping[link]
        except KeyError:
            return ''
        try:
            second_result = second_mapping[first_result]
        except KeyError:
            return ''
        return '<' + second_result + '>'
    return convert


def load_freebase_wikipedia_mapping(freebase_map, reverse=False):
    mapping = dict()
    with open(freebase_map) as map_file:
        for line in map_file:
            freebase, _, wiki = line.split('\t')
            prefixed_freebase = 'http://rdf.freebase.com/ns/' + freebase
            encoded_symbols = re.findall(r'\$[0-9A-F]{4}', wiki)
            wiki = wiki.replace('\"', '')
            wiki = wiki.replace('\n', '')
            for symbol in encoded_symbols:
                wiki = wiki.replace(symbol, chr(int(symbol[1:], base=16)))
            wiki = wiki_format(wiki)
            if reverse:
                mapping[wiki] = prefixed_freebase
            else:
                mapping[prefixed_freebase] = wiki
    return mapping


def load_wikidata_wikipedia_mapping(wikidata_map, reverse=False):
    mapping = dict()
    with open(wikidata_map) as map_file:
        for line in map_file:
            wikidata, wiki = line.split('\t')
            prefixed_wikidata = 'http://www.wikidata.org/entity/' + wikidata
            wikiurl = wiki_format(wiki)
            if reverse:
                mapping[wikiurl] = prefixed_wikidata
            else:
                mapping[prefixed_wikidata] = wikiurl
    return mapping


def main():
    suffix = "-wikipedia"

    # The input file type (one of 'wikipedia', 'wikidata', 'freebase')
    input_type = os.getenv('INPUT_TYPE', '')

    # The input file type (one of 'wikipedia', 'wikidata', 'freebase')
    output_type = os.getenv('OUTPUT_TYPE', '')

    # The input file
    input_file = os.getenv('INPUT_FILE', '')

    # The wordsfile and docsfile name prefixes
    wordsfile_name = os.getenv('WORDSFILE_NAME', 'wordsfile_[0-9]+.txt')
    docsfile_name = os.getenv('DOCSFILE_NAME', 'docsfile_[0-9]+.txt')

    # The type of the input file (one of docsfile', 'wordsfile')
    input_file_type = os.getenv('INPUT_FILE_TYPE', '')

    # The type of the input file (one of docsfile', 'wordsfile')
    results_path = os.getenv('RESULTS_PATH', '')

    # The type of the input file (one of docsfile', 'wordsfile')
    remove_merged_files = os.getenv('REMOVE_MERGED_FILES', 'False')
    if remove_merged_files.lower() == 'true':
        remove_merged_files = True
    else:
        remove_merged_files = False

    # Freebase to Wikipedia mapping
    freebase_map = os.path.join('/mappings', os.getenv('FREEBASE_MAP', ''))

    # Wikidata to Wikipedia mapping
    wikidata_map = os.path.join('/mappings', os.getenv('WIKIDATA_MAP', ''))

    in_format = input_type.lower()
    out_format = output_type.lower()
    if in_format == out_format:
        print('0', in_format, '=', out_format)

        def words_file_converter(*args):
            return words_file(*args, identity)
    elif in_format == 'wikipedia':
        if out_format == 'wikidata':
            wikipedia_wikidata_mapping = load_wikidata_wikipedia_mapping(wikidata_map, True)

            def words_file_converter(*args):
                return words_file(*args, single_map(wikipedia_wikidata_mapping))
            suffix = "-wikidata"
            print('1', in_format, '->', out_format)
        else:  # Freebase
            wikipedia_freebase_mapping = load_freebase_wikipedia_mapping(freebase_map, True)

            def words_file_converter(*args):
                return words_file(*args, single_map(wikipedia_freebase_mapping))
            suffix = "-freebase"
            print('2', in_format, '->', out_format)
    elif in_format == 'wikidata':
        if out_format == 'wikipedia':
            wikidata_wikipedia_mapping = load_wikidata_wikipedia_mapping(wikidata_map)

            def words_file_converter(*args):
                return words_file(*args, single_map(wikidata_wikipedia_mapping))
            suffix = "-wikipedia"
            print('3', in_format, '->', out_format)
        else:  # Freebase
            wikidata_wikipedia_mapping = load_wikidata_wikipedia_mapping(wikidata_map)
            wikipedia_freebase_mapping = load_freebase_wikipedia_mapping(freebase_map, True)

            def words_file_converter(*args):
                return words_file(*args, double_map(wikidata_wikipedia_mapping, wikipedia_freebase_mapping))
            suffix = "-freebase"
            print('4', in_format, '->', out_format)
    else:  # Freebase
        freebase_wikipedia_mapping = load_freebase_wikipedia_mapping(freebase_map)
        if out_format == 'wikipedia':
            def words_file_converter(*args):
                return words_file(*args, single_map(freebase_wikipedia_mapping))
            suffix = "-wikipedia"
            print('5', in_format, '->', out_format)
        else:  # Wikidata
            wikipedia_wikidata_mapping = load_wikidata_wikipedia_mapping(wikidata_map, True)

            def words_file_converter(*args):
                return words_file(*args, converter_func=double_map(freebase_wikipedia_mapping, wikipedia_wikidata_mapping))
            suffix = "-wikidata"
            print('6', in_format, '->', out_format)

    start(input_file, input_file_type, results_path, words_file_converter, suffix,
          remove_merged_files, wordsfile_name=wordsfile_name, docsfile_name=docsfile_name)


if __name__ == '__main__':
    main()
