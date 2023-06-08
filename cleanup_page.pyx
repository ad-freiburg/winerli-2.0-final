# cython: language_level=3

""" Johanna Götz """

import os
import re
import sys
import logging
from pprint import pprint


logging.addLevelName(100, 'PROHIBIT_LOGGING')
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(stream=sys.stdout, level=LOGLEVEL)


cpdef listprint(list l):
    cdef str el
    print('[')
    for el in l:
        print('\'', str(el.replace('\n', '\\n')), '\'', ',', sep='')
    print(']')


cdef class PageCleaner:
    cdef str string
    cdef int length
    cdef object jump_regex
    cdef object heading_regex
    cdef object cell_split_regex
    cdef object newline_regex
    cdef object template_split_regex
    cdef object template_key_value_pair_regex
    cdef object template_key_value_pair_optional_key_regex
    cdef object list_point_regex
    cdef object infobox_only_value_regex
    cdef object list_split_regex
    cdef object special_link
    cdef object split_no_links
    cdef object outfile

    def __init__(self, str string):
        self.string = string
        self.length = int(len(string))
        # The order of the parts is important here!
        self.jump_regex = re.compile(
            r'''(?:
              (?P<HTML_COMMENT>\<!--(?:[\s\S])*?--\>)   # html comments
            | (?P<TEMPLATE>{{)  # template start
            | (?P<TEMPLATE_END>}})   # template end
            | (?P<LINK>\[\[)  # link-like start
            | (?P<LINK_END>\]\])  # link-like end
            | (?P<BOLD_ITALIC>\'{2,})   #bold/italic
            | (?P<HEADING>(?:(?<=\n)|^)\s*([=]+))   # headings
            | (?P<RULE>(?:(?<=\n)|^)\s*[-]{4})   # rules
            | (?P<TABLE_START>(?:(?<=\n)|^)\s*\:*\s*(?:\{\|.*|\{\{[^|{}]*?table\}\}))   # table start
            | (?P<TABLE_END>(?:(?<=\n)|^)\s*\|\})   # table end
            | (?P<TABLE_CAPTION>(?:(?<=\n)|^)\s*\|\+\s*)   # table caption
            | (?P<TABLE_ROW>(?:(?<=\n)|^)\s*\|\-.*)   # table row
            | (?P<TABLE_HEADER>(?:(?<=\n)|^)\s*!\s*)   # table header
            | (?P<TABLE_CELLS>(?:(?<=\n)|^)\s*\|(?![+\-}]))   # table cells
            | (?P<LIST_ITEM>(?:(?<=\n)|^)\s*[*#;:]+\s*)   # list bullets
            | (?P<HTML_REMOVE_REF_1>\<ref[^<>]*?/\>)   # other html tags
            | (?P<HTML_REMOVE_REF_2>\<ref(?:[\s\S])*?\>[\s\S]*?\</ref\>)   # tags to remove
            | (?P<NEWLINE>\n)   # newline
            | (?P<HTML_NEWLINE>\<(?:br|BR|wbr|WBR)[^<]*?/?\>)   # html newline
            | (?P<HTML_GALLERY_START>\<gallery(?:[\s\S])*?\>)   # gallery begin
            | (?P<HTML_GALLERY_END>\</gallery\>)   # gallery end
            | (?:\<(?P<HTML_FORMAT_START>abbr|blockquote|caption|center|del|defn
                                         |dt|dd|div|em|h[1-6]|ins|i|li|mark|p|q
                                         |small|samp|strong|sub|sup|s|td|th
                                         |time|u)\s?.*?\>)   # html-based formatting
            | (?:\</(?P<HTML_FORMAT_END>abbr|blockquote|caption|center|del|defn
                                        |dt|dd|div|em|h[1-6]|ins|i|li|mark|p|q
                                        |small|samp|strong|sub|sup|s|td|th
                                        |time|u).*?\>)   # html-based formatting
            | (?P<HTML_TAG_1>\<[^<>]+?/\>)   # other html tags
            | (?:\</(?P<HTML_REMOVE_END>[^<>/]+?)(?:\s[^<>]*)?\>)   # html tags that should be removed entirely
            | (?:\<(?P<HTML_REMOVE_START>[^<>/]+?)(?:\s[^<>]*)?\>)   # html tags that should be removed entirely
            | (?P<REPLACE_NBSP>&nbsp;)   # replace &nbsp; entities by a space
            | (?P<REMOVE_TOC>__.*?TOC.*?__)   # remove table of contents stuff
            )''',
            re.VERBOSE
        )
        self.heading_regex = re.compile(r'(?:^|\n)\n*\s*(=+)\s*(.+?)\s*\1[^=]*$')
        self.cell_split_regex = re.compile(r'(?:\|(?![^[{]*\]))')
        self.newline_regex = re.compile(r'[\r\n]')
        self.template_split_regex = re.compile(r'(?:\|(?![^[]*\]))')
        self.template_key_value_pair_regex = re.compile(r'^\s*?(\w+?)\s*?=\s*?([^\s].*)\s*$', re.DOTALL)
        self.template_key_value_pair_optional_key_regex = re.compile(r'(?:^\s*?(\w+?)\s*?=|^\s*?)\s*?([^\s].*)\s*$', re.DOTALL)
        self.list_point_regex = re.compile(r'^\s*?.*?[a-zA-Z].*?=')  # these can have positional arguments (numeric), so deal with those because they contain content
        self.infobox_only_value_regex = re.compile(r'^\s*?[\w\s-]+?=\s*?([^\s].*)\s*$', re.DOTALL)
        self.list_split_regex = re.compile('\n+\s*?[*#]')
        # Regex to detect special links and also interlanguage links
        self.special_link = re.compile(r'^[:]?([Ff]ile|[Ii]mage|[Ww]ikt|[Ww]ikipedia|WP|[Mm]edia|[Ww]ikisource|[Ss]pecies|[Cc]ommons|[Hh]elp|[Tt]alk|[a-z]{2}):')
        self.split_no_links = re.compile(r'\|(?![^[][^[]*]])')


    cpdef join(self, str s, list l):
        return s.join(l)


    # Split rows of table cells/headers or captions into single cells
    # and extract the content
    cpdef split_cells(self, str cell_string, str state_name):
        cdef str result
        cdef list temp_cells
        cdef list temp_element
        cdef list temp_list

        result = ''
        temp_cells = []
        if state_name == 'TABLE_CELLS':
            temp_cells = cell_string.split('||')
        elif state_name == 'TABLE_HEADER':
            temp_cells = cell_string.split('!!')
        if state_name == 'TABLE_CELLS' or state_name == 'TABLE_HEADER':
            # Split the row into cells and separate the styling part
            temp_list = [self.cell_split_regex.split(e.strip('\r\n ')) for e in temp_cells]
            # A table (header) cell can contain formatting information
            # In this case, everything before the first pipe char in the cell will be taken as that
            # and thus get ignored
            for temp_element in temp_list:
                if len(temp_element) > 1:
                    result += self.join('', temp_element[1:]).strip('\r\n ') + '\n'
                else:
                    result += temp_element[0].strip('\r\n ') + '\n'
        # Handle table captions
        elif state_name == 'TABLE_CAPTION':
            temp_cells = self.newline_regex.split(cell_string.strip('\r\n '))
            temp_list = [e.strip('\r\n ') for e in temp_cells]
            result += ' '.join(temp_list) + '\n'
        return result


    # Strip the templates but keep the content if possible
    cpdef strip_templates(self):
         # Integrate this later maybe
        self.string = re.sub('<(.+?)>.*?</\1>', '', self.string)
        pos = -1
        return self.parse_templates()


    # Strip the templates but keep the content if possible
    cpdef parse_templates(self):
        cdef str self_string = self.string
        cdef list template_stack
        cdef list state_stack
        cdef int open_templates
        cdef int open_links
        cdef int pos
        cdef object jump_match
        cdef int match_length
        cdef str template_name
        cdef str str_element
        cdef list match_list
        cdef str list_elem_str
        cdef dict content_dict
        cdef int counter
        cdef str current_state
        cdef int new_pos
        cdef str last_matched_group
        cdef str stack_element

        state_stack = []
        state_stack.append('START')
        template_stack = []
        template_stack.append([])
        open_templates = 0
        open_links = 0
        pos = 0
        while pos < self.length:
            jump_match = self.jump_regex.search(self_string, pos)
            # No match to be found anymore
            if jump_match is None:
                # Add the rest of the string and stop
                template_stack[-1].append(self_string[pos:])
                break
            new_pos = jump_match.start()
            match_length = int(len(jump_match.group(0)))
            last_matched_group = jump_match.lastgroup
            template_stack[-1].append(self_string[pos:new_pos])
            pos = new_pos
            current_state = state_stack[-1]

            logging.info('Parse templates: Last matched group: " ' + last_matched_group + ' "; state: " ' \
                + repr(current_state) + ' "; state stack: " ' + repr(state_stack) + ' "; template stack: "' \
                + repr([self.join('', e).encode('utf-8') for e in template_stack]) + ' "')

            # The line might be a headline of some sort
            if last_matched_group == 'HEADING':
                state_stack.append('HEADING')
                logging.debug('Parse templates: Heading: ' + repr(jump_match))
                template_stack.append([jump_match.group(0)])
                pos = pos + match_length
                continue
            # Italic/bold formatting starts with at least two apostrophes
            elif last_matched_group == 'BOLD_ITALIC':
                pos = pos + match_length
                continue
            # Remove list and indent starting chars
            elif last_matched_group == 'LIST_ITEM':
                pos = pos + match_length
                continue
            # A horizontal line is indicated by 4 hyphens
            elif last_matched_group == 'RULE':
                pos = pos + match_length
                continue
            # Start of a table
            elif last_matched_group == 'TABLE_START':
                pos = pos + match_length
                logging.debug('Parse templates: ~ table started:')
                # It's possible that the table is contained in a table cell
                # Check for this and if it is, process the content up to this point
                if current_state == 'TABLE_CELLS' or \
                    current_state == 'TABLE_HEADER' or \
                    current_state == 'TABLE_CAPTION':
                    stack_element = self.join('', template_stack.pop())
                    template_stack[-1].append(self.split_cells(stack_element, current_state))
                    # The cell might continue, so add a new empty element
                    template_stack.append([])
                state_stack.append('TABLE_START')
                template_stack.append([])
            # End of a table
            elif last_matched_group == 'TABLE_END':
                pos = pos + match_length
                # Deal with the last cells and stuff
                if current_state == 'TABLE_CELLS' or \
                    current_state == 'TABLE_HEADER' or \
                    current_state == 'TABLE_CAPTION':
                    stack_element = self.join('', template_stack.pop())
                    state_stack.pop()
                    template_stack[-1].append(self.split_cells(stack_element, current_state))
                if state_stack[-1] == 'TABLE_START':
                    logging.debug('Parse templates: ~ table ended.')
                    # Remove table start state
                    state_stack.pop()
                    stack_element = self.join('', template_stack.pop())
                    template_stack[-1].append(stack_element)
            # Some table-related thing matched
            elif last_matched_group == 'TABLE_ROW' or \
                last_matched_group == 'TABLE_CELLS' or \
                last_matched_group == 'TABLE_HEADER' or \
                last_matched_group == 'TABLE_CAPTION':
                # Table stuff can only occur inside of tables
                if current_state[0:5] == 'TABLE':
                    pos = pos + match_length
                    logging.debug('Parse templates: ~~ a table row or table cells start here...')
                    # Deal with the cells so far
                    if current_state == 'TABLE_CELLS' or \
                        current_state == 'TABLE_HEADER' or \
                        current_state == 'TABLE_CAPTION':
                        stack_element = self.join('', template_stack.pop())
                        state_stack.pop()
                        template_stack[-1].append(self.split_cells(stack_element, current_state))
                    # Table cells
                    if last_matched_group == 'TABLE_CELLS':
                        state_stack.append('TABLE_CELLS')
                        template_stack.append([]),
                        logging.debug('Parse templates: ~~ table cells started...')
                    # Table header
                    elif last_matched_group == 'TABLE_HEADER':
                        state_stack.append('TABLE_HEADER')
                        template_stack.append([])
                        logging.debug('Parse templates: ~~ table header started...')
                    # Table caption
                    elif last_matched_group == 'TABLE_CAPTION':
                        state_stack.append('TABLE_CAPTION')
                        template_stack.append([])
                        logging.debug('Parse templates: ~~ table caption started...')
                    # Table row
                    elif last_matched_group == 'TABLE_ROW':
                        logging.debug('Parse templates: ~~ table row started...')
                # Not in a table, so treat it like a normal string
                else:
                    template_stack[-1].append(jump_match.group(0))
                    pos = pos + match_length
            # HTML gallery tag opened
            elif last_matched_group == 'HTML_GALLERY_START':
                state_stack.append('HTML_GALLERY_START')
                template_stack.append([])
                pos = pos + match_length
            # HTML gallery tag closed
            elif last_matched_group == 'HTML_GALLERY_END':
                if current_state == 'HTML_GALLERY_START':
                    state_stack.pop()
                    stack_element = self.join('', template_stack.pop())
                    logging.debug('Parse templates: Gallery stuff: ' + repr(stack_element))
                    # Split into lines
                    for str_element in stack_element.split('\n'):
                        # Split into the elements
                        template_elements = self.split_no_links.split(str_element)[1:]
                        for list_elem_str in template_elements:
                            match_list = self.template_key_value_pair_optional_key_regex.findall(list_elem_str)
                            # This is probably the caption
                            if len(match_list) > 0 and len(match_list[0][0]) == 0:
                                logging.debug('Parse templates: Gallery stuff: Caption: ' + repr(match_list[0][1]))
                                template_stack[-1].append(match_list[0][1])
                pos = pos + match_length
            # HTML formatting tag opened
            elif last_matched_group == 'HTML_FORMAT_START':
                state_stack.append('HTML_FORMAT_START_' + jump_match.group('HTML_FORMAT_START').upper())
                template_stack.append([])
                pos = pos + match_length
            # HTML formatting tag closed
            elif last_matched_group == 'HTML_FORMAT_END':
                if current_state == 'HTML_FORMAT_START_' + jump_match.group('HTML_FORMAT_END').upper():
                    state_stack.pop()
                    stack_element = self.join('', template_stack.pop())
                    logging.debug('Parse templates: HTML stuff: Tag: ' + jump_match.group('HTML_FORMAT_END').upper() \
                                     + '; Content: ' + repr(stack_element) + '; Last stack states: ' + repr(state_stack[-5:]) \
                                     + '; Last template contents: ' + repr(template_stack[-1]))
                    template_stack[-1].append(stack_element)
                pos = pos + match_length
            # HTML tag to be removed opened
            elif last_matched_group == 'HTML_REMOVE_START':
                state_stack.append('HTML_REMOVE_START_' + jump_match.group('HTML_REMOVE_START').upper())
                template_stack.append([])
                pos = pos + match_length
            # HTML tag to be removed closed
            elif last_matched_group == 'HTML_REMOVE_END':
                if current_state == 'HTML_REMOVE_START_' + jump_match.group('HTML_REMOVE_END').upper():
                    state_stack.pop()
                    template_stack.pop()
                pos = pos + match_length
            # HTML newlines
            elif last_matched_group == 'HTML_NEWLINE':
                template_stack[-1].append('\n')
                pos = pos + match_length
            # Replace &nbsp; by a space
            elif last_matched_group == 'REPLACE_NBSP':
                template_stack[-1].append(' ')
                pos = pos + match_length
            # Template opened
            elif last_matched_group == 'LINK':
                state_stack.append('LINK')
                template_stack.append([])
                open_links += 1
                pos += 2
                logging.debug('Parse templates: ~~ a link begins here...')
            # Link closed
            elif last_matched_group == 'LINK_END' and open_links > 0:
                pos += 2
                open_links -= 1
                # Remove the state for the link
                state_stack.pop()
                stack_element = self.join('', template_stack.pop())
                logging.debug('Parse templates: Link parsing: Content: ' + repr(stack_element))
                match_list = self.split_no_links.split(stack_element)
                # We have a special link where we only keep the link text
                if self.special_link.search(match_list[0]) is not None:
                    # If we have a true last element and it's not part of a key-value pair,
                    # add it as text
                    if len(match_list) > 1 and '=' not in match_list[-1]:
                        template_stack[-1].append('\n' + match_list[-1] + ' \n')
                        logging.debug('Parse templates: Link parsing: Link text: ' + repr(match_list[-1]) + '; Last template contents: ' + repr(template_stack[-1]))
                # We have a normal wikilink
                else:
                    template_stack[-1].append('[[%s]]' % stack_element)
                    logging.debug('Parse templates: Link parsing: Actual link: ' + '[[%s]]' % stack_element)
            # Template opened
            elif last_matched_group == 'TEMPLATE':
                state_stack.append('TEMPLATE')
                template_stack.append([])
                open_templates += 1
                pos += 2
                logging.debug('Parse templates: ~~ a template begins here...')
            # Template closed
            elif last_matched_group == 'TEMPLATE_END' and open_templates > 0:
                pos += 2
                open_templates -= 1
                # Remove the state for the template
                state_stack.pop()
                stack_element = self.join('', template_stack.pop())
                template_elements = [e.strip('\r\n ') for e in self.template_split_regex.split(stack_element)]
                template_name = template_elements[0].lower()
                # Replace space characters by a regular space
                if template_name in ['space', '&nbsp', 'nbs', 'nbsp', 'nbsp;', \
                                     'spcs', 'fs', 'fsp', 'sp', 'hsp', 'hair space', \
                                     'hairsp', 'px1', 'nb5', 'nb10', 'spaces', 'indent', \
                                     'nnbsp', '8239', 'ns', 'quad', 'thinsp', 'in5', 'pad', \
                                     'px2']:
                    template_stack[-1].append(' ')
                # Replace hyphen characters by a regular hyphen
                elif template_name in ['nbhyph', 'nbh']:
                    template_stack[-1].append('-')
                # Replace dash characters by two regular hyphens
                elif template_name in ['ndash', 'en dash', 'nsndns', '--', \
                                       'emdash', 'mdash', 'em dash']:
                    template_stack[-1].append('--')
                # Replace the spaced dash character by two regular hyphens in spaces
                elif template_name in ['snd', 'spnd', 'sndash', 'spndash', \
                                       'snds', 'spndsp', 'sndashs', 'spndashsp']:
                    template_stack[-1].append(' -- ')
                # Replace the circa template
                elif template_name == 'circa':
                    template_stack[-1].append('c. ')
                # Replace the floruit template
                elif template_name in ['fl', 'fl.']:
                    template_stack[-1].append('fl. ')
                # Replace solar mass template
                elif template_name == 'solar mass':
                    template_stack[-1].append('M')
                # Replace music templates
                elif template_name == 'music':
                    if template_elements[1] == 'time':
                        template_stack[-1].append(template_elements[2] + '/' + template_elements[3])
                    elif template_elements[1] == 'scale':
                        template_stack[-1].append(template_elements[2])
                    else:
                        template_stack[-1].append(template_elements[1])
                # Templates that should be removed entirely
                # (likely incomplete due to the insane number of available templates)
                elif template_name in ['shy', 'okina', 'zwj', 'zwsp', '0ws', 'sic', \
                    'glossary', 'glossary end', 'startflatlist', 'endflatlist', \
                    'plainlist', 'endplainlist', 'flowlist', 'endflowlist', \
                    'featured article', 'clear', 'nom', 'won', 'kos', 'loc']:
                    pass
                # Language template
                elif template_name in ['lang', 'transl']:
                    logging.debug('Parse templates: Language template: %s', repr(template_elements))
                    if len(template_elements) > 3 and template_elements[2] in ['DIN', 'ISO', 'ALA']:
                        template_stack[-1].append(template_elements[3])
                    elif len(template_elements) > 2:
                        template_stack[-1].append(template_elements[2])
                # Handle text in other languages
                elif template_name[0:5] == 'lang-':
                    # Extract the pairs of term/content and the corresponding values
                    #content_dict = dict(map(lambda e: self.template_key_value_pair_optional_key_regex.findall(e)[0], template_elements[1:]))
                    content_dict = dict([self.template_key_value_pair_optional_key_regex.findall(e)[0] for e in template_elements[1:] if len(e.strip()) > 0])
                    logging.debug('Parse templates: ' + repr(content_dict))
                    # Get the content parts only - the order is important!
                    for list_elem_str in ['text', '1', '', 'lit', 'translation']:
                        str_element = content_dict.get(list_elem_str, '')
                        if len(str_element) < 1:
                            continue
                        else:
                            if list_elem_str != 'lit' and list_elem_str != 'translation':
                                template_stack[-1].append(str_element)
                            # Add the literal translation
                            else:
                                template_stack[-1].append(', \'' + str_element + '\'')
                # Replace the reign template
                elif template_name == 'reign':
                    template_stack[-1].append('r. ')
                    for str_element in template_elements[1:]:
                        template_stack[-1].append('str_element' + '-')
                # Add the percentage values (calculated)
                elif template_name in ['percentage', 'percent', 'pct']:
                    content_dict = dict()
                    counter = 1
                    for str_element in template_elements[1:]:
                        # Extract the pairs of term/content and the corresponding values
                        match_list = self.template_key_value_pair_optional_key_regex.findall(str_element)
                        if len(match_list) > 0 and len(match_list[0]) > 0:
                            if len(match_list[0][0]) == 0:
                                content_dict[str(counter)] = match_list[0][1]
                                counter += 1
                            else:
                                content_dict[match_list[0][0]] = match_list[0][1]
                    # In case there are parser functions or other things instead of numbers,
                    # just try to see if this actually works
                    try:
                        template_stack[-1].append(
                            str(round(int(content_dict.get('1', '0').replace(',', '')) / int(content_dict.get('2', '100').replace(',', '')) * 100,
                                int(content_dict.get('3', 0)))) + '%'
                        )
                    except:
                        pass
                # Unbulleted lists and similar lists
                elif template_name in ['ubl', 'ubt', 'ublist', 'unbullet', \
                    'unbulleted list', 'blist', 'bulleted', 'ulist', \
                    'unordered list', 'bulleted list', 'ordered list', \
                    'colored list', 'hlist', 'cslist']:
                    # Find the real bullet point contents
                    # (= not style etc. which are given as pairs with "=")
                    for str_element in template_elements[1:]:
                        if self.list_point_regex.match(str_element) is None:
                            template_stack[-1].append(str_element + '\n')
                            #logging.warning(template_stack[-1])
                # Flat lists and similar lists
                elif template_name in ['flatlist', 'cmn', 'collist', \
                    'col-list', 'columns-list', 'plainlist', 'flowlist']:
                    # Find the real bullet point contents
                    # (= not style etc. which are given as pairs with "=")
                    for str_element in template_elements[1:]:
                        if self.list_point_regex.match(str_element) is None:
                            match_list = self.list_split_regex.split(str_element)
                            for list_elem_str in match_list:
                                template_stack[-1].append(list_elem_str.strip('\r\n ') + '\n')
                                #logging.warning(template_stack[-1])
                # Infoboxes and similar
                elif template_name[0:7] == 'infobox' or template_name[-3:] == 'box':
                    logging.warning('Parse templates: FOUND INFOBOX!' + '\n' + repr(template_elements))
                    # Find the real bullet point contents
                    for str_element in template_elements[1:]:
                        # Extract key-value pairs
                        match_list = self.infobox_only_value_regex.findall(str_element)
                        logging.warning('Parse templates: ' + repr(str_element))
                        logging.warning('Parse templates: ' + repr(match_list))
                        if len(match_list) > 0:
                            template_stack[-1].append(match_list[0].strip('\r\n ') + '\n\n')
                # Glossary stuff
                # A term in a glossary
                elif template_name == 'term':
                    content_dict = dict()
                    for str_element in template_elements[1:]:
                        # Extract the pairs of term/content and the corresponding values
                        match_list = self.template_key_value_pair_regex.findall(str_element)
                        # Get the content part only
                        if len(match_list) > 0:
                            if match_list[0][0] == '1' or match_list[0][0] == 'term':
                                content_dict['term'] = match_list[0][1]
                            elif match_list[0][0] == '2' or match_list[0][0] == 'content':
                                content_dict['content'] = match_list[0][1]
                    # The content is the preferred text
                    if len(content_dict.get('content', '')) > 0:
                        template_stack[-1].append(content_dict['content'] + '\n')
                    else:
                        template_stack[-1].append(content_dict.get('term', '') + '\n')
                # A definition in a glossary
                elif template_name == 'defn':
                    for str_element in template_elements[1:]:
                        # Extract the pairs of term/content and the corresponding values
                        match_list = self.template_key_value_pair_regex.findall(str_element)
                        if len(match_list) > 0:
                            # Get the content part only
                            if match_list[0][0] == '1' or match_list[0][0] == 'defn':
                                template_stack[-1].append(match_list[0][1] + '\n')
                            elif match_list[0][0] == '2' or match_list[0][0] == 'content':
                                template_stack[-1].append(match_list[0][1] + '\n')
                # Some other weird glossary thing...
                elif template_name == 'ghat':
                    template_stack[-1].append(template_elements[1])
                # Another weird glossary thing...
                elif template_name.endswith('gloss'):
                    if len(template_elements) > 2:
                        template_stack[-1].append(template_elements[2])
                    elif len(template_elements) > 1:
                        template_stack[-1].append(template_elements[1])
                # Quotes and glossary block quotes
                elif template_name in ['quote', 'gquote', 'gbq']:
                    logging.debug('Parse templates: ' + stack_element)
                    # Extract the pairs of term/content and the corresponding values
                    content_dict = dict()
                    counter = 1
                    for str_element in template_elements[1:]:
                        # Extract the pairs of term/content and the corresponding values
                        match_list = self.template_key_value_pair_optional_key_regex.findall(str_element)
                        # Check if there even is a match
                        if len(match_list) > 0:
                            if len(match_list[0][0]) == 0:
                                content_dict[str(counter)] = match_list[0][1]
                                counter += 1
                            else:
                                content_dict[match_list[0][0]] = match_list[0][1]
                    # Get the content parts only - the order is important!
                    for list_elem_str in ['text', '1', 'character', '5', 'author', '2', \
                        'title', '3', 'source', '4']:
                        str_element = content_dict.get(list_elem_str, '')
                        if len(str_element) < 1:
                            continue
                        else:
                            template_stack[-1].append(str_element + '\n')
                # The short description
                elif template_name == 'short description':
                    # Extract the pairs of term/content and the corresponding values
                    content_dict = dict([self.template_key_value_pair_optional_key_regex.findall(e)[0] for e in template_elements[1:] if len(e.strip()) > 0])
                    logging.debug('Parse templates: ' + repr(content_dict))
                    # Get the content parts only - the order is important!
                    for list_elem_str in ['1', '']:
                        str_element = content_dict.get(list_elem_str, '')
                        if len(str_element) < 1:
                            continue
                        else:
                            template_stack[-1].append(str_element + '.\n')
                # Skip protection templates
                elif template_name[0:2] == 'pp':
                    pass
                # Templates without any arguments that stay the way they are
                elif len(template_elements) == 1:
                    logging.debug('Parse templates: Name of template of length 1: %s', template_name)
                    if len(template_name) > 5 or template_name.startswith('s-'):
                        #logging.critical('Parse templates: Remove template of length 1: %s', template_name)
                        pass
                    else:
                        template_stack[-1].append(template_name)
                        logging.debug('Parse templates: ' + repr(repr(template_elements).encode('unicode_escape')))
                        logging.debug('Keep template of length 1: %s', template_name)
                # Other templates that do take arguments
                elif len(template_elements) > 1:
                    logging.debug('Parse templates: Template of length > 1: %s', repr(template_elements))
                    if template_name == 'chem':
                        template_stack[-1].append(self.join('', template_elements[1:]))
                    # Also handle this somewhere: https://en.wikipedia.org/wiki/Template:Resize
                    elif template_name in ['small', 'smaller', 'midsize', \
                        'larger', 'big', 'large', 'huge', 'nobold', \
                        'nocaps', 'noitalic', 'nowrap']:
                        template_stack[-1].append(template_elements[1])
                    else:
                        logging.debug('Parse templates: ' + repr(repr(template_elements).encode('unicode_escape')))
            # Normal char
            elif last_matched_group == 'NEWLINE':
                if current_state == 'TEMPLATE':
                    pass
                # Extract the heading's actual content
                elif current_state == 'HEADING':
                    stack_element = self.join('', template_stack.pop())
                    state_stack.pop()
                    try:
                        template_stack[-1].append(self.heading_regex.findall(stack_element.strip())[0][1])
                    except:
                        pass
                elif current_state[0:5] == 'TABLE':
                    # If apparently a table started but a line starts with something that can't belong to the table,
                    # the suspected table wasn't a table
                    if current_state == 'TABLE_START' and self_string[pos + 1].strip('\r\n ') not in ['|', '!']:
                        logging.warning('Parse templates: ' + repr(self_string[pos + 1]))
                        stack_element = self.join('', template_stack.pop())
                        template_stack[-1].append(stack_element)
                        state_stack.pop()
                else:
                    # If we had a text before, remove this
                    # If the text continues in the next line, it'll be added again anyway
                    # in the condition for the NEWLINE state above
                    if current_state == 'TEXT':
                        state_stack.pop()
                # Add current character
                # Prevent multiple newlines
                logging.debug('Parse templates: ' + repr(self.join('', template_stack[-1]).encode('utf-8')))
                if not self.join('', template_stack[-1][-2:]) == '\n\n':
                    template_stack[-1].append('\n')
                pos += 1
            else:
                pos = pos + match_length
                logging.debug('Parse templates: ~~~ ' + last_matched_group)
            logging.info('Parse templates: state stack: ' + repr(state_stack))
            logging.info('=' * 50)
        return self.join('', template_stack[-1])
