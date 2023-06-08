""" Johanna Götz """

# cython: language_level=3

import os
import sys
import re
import logging
from pprint import pprint


logging.addLevelName(100, 'PROHIBIT_LOGGING')
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(stream=sys.stdout, level=LOGLEVEL)


cdef class InfoboxLinkParser:
    cdef str text
    cdef str infobox_template
    cdef object infobox_link_regex
    cdef object infobox_key_regex
    cdef object link_regex
    cdef str infobox_state
    cdef list current_key
    cdef list current_value
    cdef list infoboxes
    cdef list links
    cdef list link_stack
    cdef int char_pos
    cdef int curly_counter
    cdef int square_counter
    cdef bint only_parse_links

    def __init__(self, str text):
        self.text = text
        # Some infobox stuff
        self.infobox_template = '\{\{(infobox|[A-Za-z ]+?(taxobox|mycomorphbox|ichnobox))'
        self.infobox_link_regex = re.compile('(\[\[|' + self.infobox_template + ')', re.IGNORECASE)
        self.infobox_key_regex = re.compile('[\w\s\-\?]')
        self.link_regex = re.compile('(\[\[)')
        # The parsing states
        self.infobox_state = 'START'
        # Collect temp data
        self.current_key = []
        self.current_value = []
        # Each infobox is given as a tuple of infobox type and infobox content
        self.infoboxes = []
        # Each link is given as a tuple of link text and wikilink
        self.links = []
        self.link_stack = []
        # Go through all characters
        self.char_pos = 0
        # Most templates (including infoboxes) start with curly brackets
        self.curly_counter = 0
        # Some templates are in square brackets
        self.square_counter = 0
        # Don't parse infoboxes
        self.only_parse_links = False

    # Helper function for logging output
    cpdef _shorten_string(self, str string, int n = 15):
        if len(string) > 2 * n:
            return string[:n] + '...' + string[-n:]
        else:
            return string

    # Helper function for logging output
    cpdef _trim_string(self, str string):
        return string.strip('\r\n\t ')

    # Only parse links
    cpdef parse2(self):
        cdef object match

        match = self.link_regex.search(self.text, 0)
        while match is not None:
            self.char_pos = match.start()
            # Try parsing from here, there could be a link
            self._parse_link()
            match = self.link_regex.search(self.text, self.char_pos + 1)

    # Parse links and infoboxes
    cpdef parse(self):
        cdef object match
        cdef bint is_infobox

        match = self.infobox_link_regex.search(self.text, 0)
        while match is not None:
            self.char_pos = match.start()
            # Is it an infobox?
            is_infobox = (match.group(0) != '[[')
            if is_infobox:
                if not self.only_parse_links:
                    # Try parsing from here, there could be an infobox
                    logging.debug('Infobox type: ' + repr(match.group(0)))
                    self._parse_infobox(offset=len(match.group(0)))
            else:
                # Try parsing from here, there could be a link
                self._parse_link()
            match = self.infobox_link_regex.search(self.text, self.char_pos + 1)

    cpdef get_infoboxes(self):
        return self.infoboxes

    cpdef get_links(self):
        return self.links

    # Extract infoboxes
    # Should nested infoboxes occur, only the outermost one will be parsed
    # The rest will be treated like a regular string
    # Links will be parsed separately but in the infobox output they'll occur as strings
    cpdef _parse_infobox(self, int offset):
        cdef int template_name_end_pos
        cdef int old_curly_counter
        cdef int old_square_counter
        cdef dict current_infobox
        cdef list infobox_category
        cdef list previous_key
        cdef list previous_value
        cdef str current_char
        cdef str current_2chars
        cdef str cleaned_key
        cdef str cleaned_value

        # If there is a infobox template, set a new position and parse
        self.char_pos = self.char_pos + offset
        # An infobox starts with 2 curly brackets
        old_curly_counter = self.curly_counter
        self.curly_counter += 2
        # Keep the square counter
        old_square_counter = self.square_counter
        # Enter start state
        self.infobox_state = 'START'
        # Go through all characters until the infobox has ended
        current_infobox = dict()
        # The infobox's category
        infobox_category = []
        # The previous key and value
        previous_key = None
        previous_value = None
        while True:
            try:
                current_char = self.text[self.char_pos]
                current_2chars = self.text[self.char_pos:self.char_pos+2]
            except:
                break
            # Start parsing
            if self.infobox_state == 'START':
                # A key-value pair begins after the pipe char
                if current_char == '|':
                    # Reset key and value
                    self.current_key = []
                    self.current_value = []
                    self.infobox_state = 'KEY'
                # The content before the first pipe is the infobox category
                else:
                    # Some infoboxes don't contain any keys or values
                    if current_2chars == '}}':
                        break
                    # Ignore HTML comments
                    elif self.text[self.char_pos:self.char_pos+4] == '<!--':
                        self.char_pos = self.text.find('-->', self.char_pos) + 2
                    else:
                        infobox_category.append(current_char)
            # Add chars to the key until the value starts
            elif self.infobox_state == 'KEY':
                # Change from key to value when "=" occurs
                if current_char == '=' and (self.curly_counter - old_curly_counter == 2):
                    self.infobox_state = 'VALUE'
                    logging.debug('Key: ' + ''.join(self.current_key))
                # Still appending to the key
                elif self.infobox_key_regex.match(current_char):
                    self.current_key.append(current_char)
                # Ignore HTML comments
                elif self.text[self.char_pos:self.char_pos+4] == '<!--':
                    self.char_pos = self.text.find('-->', self.char_pos) + 2
                # If the number of still opened curly brackets is 2 and we see "}}",
                # we have reached the infobox's end
                elif current_2chars == '}}' and (self.curly_counter - old_curly_counter == 2):
                    self.curly_counter -= 2
                    break
                # Reset the key if we're in the key and encounter a pipe
                # This case can happen with "bilateral relations" infoboxes
                elif current_char == '|' and (self.curly_counter - old_curly_counter == 2):
                    self.current_key = []
                # There's a character that doesn't belong to a key
                else:
                    try:
                        if previous_value is not None:
                            # Set the value as the previous value + the current key
                            # because that is what we have read so far
                            self.current_value = previous_value + ['|'] + self.current_key
                            # Set the previous key and state
                            self.current_key = previous_key
                            self.infobox_state = 'VALUE'
                            # A link has started
                            if current_2chars == '[[':
                                self.current_value.append(self._parse_link())
                            else:
                                if current_2chars == '{{':
                                    self.curly_counter += 2
                                elif current_2chars == '}}':
                                    self.curly_counter -= 2
                                self.current_value.append(current_char)
                        # Append to key because when the next pipe appears,
                        # it'll be discarded anyway
                        else:
                            self.current_key.append(current_char)
                    except Exception as e:
                        logging.critical('Current char: "%s" ~~~ Match: %s' % (current_char, repr(self.infobox_key_regex.match(current_char))))
                        logging.critical('Infobox stuff: Current char: %s ~~~ Prev value: %s ~~~ Prev value joined: %s ~~~ Current key: %s ~~~ Current key joined: %s ~~~ Context: %s' % (repr(current_char), repr(previous_value), repr(''.join(previous_value)) if previous_value is not None else 'NONE', repr(self.current_key), repr(''.join(self.current_key)), repr(self.text[max(self.char_pos-300, 0):min(self.char_pos+300, len(self.text))])))
                        raise e
            # Add chars to the value until all stuff has been parsed
            # (including templates)
            elif self.infobox_state == 'VALUE':
                # Update the bracket counts
                if current_char == '{':
                    self.curly_counter += 1
                    # Add character
                    self.current_value.append(current_char)
                # If the number of still opened curly brackets is 2 and we see "}}",
                # we have reached the infobox's end and can add the key-value pair
                elif current_2chars == '}}' and (self.curly_counter - old_curly_counter == 2):
                    self.curly_counter -= 2
                    # If the number of still opened curly brackets is 0,
                    # we have reached the infobox's end and can add the key-value pair
                    logging.debug('Value: ' + ''.join(self.current_value))
                    # Add key-value pair to result
                    cleaned_key = self._trim_string(''.join(self.current_key))
                    cleaned_value = self._trim_string(''.join(self.current_value))
                    logging.info('Key: %s, Value: %s' % (cleaned_key, self._shorten_string(cleaned_value)))
                    current_infobox[cleaned_key] = cleaned_value
                    break
                elif current_char == '}':
                    self.curly_counter -= 1
                    # Add character
                    self.current_value.append(current_char)
                # A link starts here
                elif current_2chars == '[[':
                    self.current_value.append(self._parse_link())
                elif current_char == '[':
                    self.square_counter += 1
                    # Add character
                    self.current_value.append(current_char)
                elif current_char == ']':
                    self.square_counter -= 1
                    # Add character
                    self.current_value.append(current_char)
                # A new key-value pair will start,
                # so process the gathered data and add it to the result
                elif current_char == '|':
                    # If the number of still opened curly brackets is 2,
                    # all curly brackets except from the infobox itself have been closed
                    if self.curly_counter - old_curly_counter == 2 and self.square_counter == old_square_counter:
                        logging.debug('Value: ' + ''.join(self.current_value))
                        # Add key-value pair to result
                        cleaned_key = self._trim_string(''.join(self.current_key))
                        cleaned_value = self._trim_string(''.join(self.current_value))
                        logging.info('Key: %s, Value: %s' % (cleaned_key, self._shorten_string(cleaned_value)))
                        current_infobox[cleaned_key] = cleaned_value
                        previous_key = self.current_key
                        previous_value = self.current_value
                        self.infobox_state = 'KEY'
                        # Reset key and value
                        self.current_key = []
                        self.current_value = []
                    else:
                        # Add character
                        self.current_value.append(current_char)
                else:
                    # Add character
                    self.current_value.append(current_char)
            self.char_pos += 1
        # Add the infobox
        cleaned_category = self._trim_string(''.join(infobox_category).replace('\n', '')).lower()
        self.infoboxes.append((cleaned_category, current_infobox))

    # Extract links
    cpdef _parse_link(self):
        cdef tuple current_link
        cdef str current_char
        cdef str current_2chars
        cdef str char
        cdef str cleaned_wikilink
        cdef str cleaned_linktext
        cdef str link_content
        cdef list link_content_parts
        cdef str stripped_content

        # If this method was called, there was a square bracket template,
        # so set a new position and parse
        self.char_pos = self.char_pos + 2
        # A link starts with 2 square brackets
        self.square_counter += 2
        self.link_stack.append([])
        # Go through all characters until the infobox has ended
        current_link = ()
        while True:
            try:
                current_char = self.text[self.char_pos]
                current_2chars = self.text[self.char_pos:self.char_pos+2]
            except Exception as e:
                logging.warning(e)
                break
            # Update bracket counts
            if current_2chars == '[[':
                # A link-like template starts here, so parse
                return self._parse_link()
            elif current_2chars == ']]':
                self.char_pos += 1
                self.square_counter -= 2
                # If the number of still opened square brackets is 0,
                # we have reached the link's end and can add the data
                link_content = ''.join(self.link_stack.pop())
                link_content_parts = link_content.split('|', 1)
                # All these characters are invalid in wikilinks,
                # so if one of those occurs, it can't be a valid link
                for char in link_content_parts[0]:
                    if char in ['<', '>', '[', ']', '{', '}', '_']:
                        return link_content
                logging.info('Link content parts: %s' % repr(link_content_parts))
                # Strip templates
                stripped_content = None
                if len(link_content_parts) > 1:
                    stripped_content = self.strip_templates(link_content_parts[1])
                elif len(link_content_parts) > 0:
                    stripped_content = link_content_parts[0]
                # We've got something that seems to be a wikilink!
                if stripped_content is not None:
                    # Add data to result
                    # If the link uses an anchor to some part of the page,
                    # remove that and only keep the actual link
                    cleaned_wikilink = self._trim_string(link_content_parts[0]).split('#')[0]
                    cleaned_linktext = self._trim_string(stripped_content) if len(link_content_parts) == 2 else cleaned_wikilink
                    logging.info('Wikilink: "%s", Link text: "%s"' % (cleaned_wikilink, self._shorten_string(cleaned_linktext)))
                    current_link = (cleaned_wikilink, cleaned_linktext)
                    self.links.append(current_link)
                return stripped_content if stripped_content is not None else link_content
            # No special character encountered
            else:
                self.link_stack[-1].append(current_char)
                # Curly brackets are considered invalid in a link, stop
                if current_char == '{':
                    self.curly_counter += 1
                elif current_char == '}':
                    self.curly_counter -= 1
            self.char_pos += 1


    cpdef strip_templates(self, str string):
        cdef str prev_char
        cdef list template_stack
        cdef list stack_element
        cdef int open_templates
        cdef str template_name
        cdef int test
        cdef str char

        test = 0
        open_templates = 0
        template_stack = []
        template_stack.append('')
        prev_char = ''
        for char in string:
            # If at least one pipe is outside of a template here,
            # there must be something going on that is not a simple link
            if char == '|' and open_templates == 0:
                return None
            # Template opened
            elif char == '{':
                if prev_char == '{':
                    template_stack.append('')
                    open_templates += 1
                    prev_char = ''
                else:
                    prev_char = char
            # Template closed
            elif char == '}':
                if prev_char == '}' and open_templates > 0:
                    open_templates -= 1
                    test += 1
                    stack_element = template_stack.pop().split('|')
                    logging.debug('Stack element: %s' % repr(stack_element))
                    template_name = stack_element[0].strip('\r\n ').lower()
                    # Replace space characters by a regular space
                    if template_name in ['space', '&nbsp', 'nbs', 'nbsp', 'nbsp;', \
                                         'spcs', 'fs', 'fsp', 'sp', 'hsp', 'hair space', \
                                         'hairsp', 'px1', 'nb5', 'nb10', 'spaces', 'indent', \
                                         'nnbsp', '8239', 'ns', 'quad', 'thinsp', 'in5', 'pad', \
                                         'px2']:
                        template_stack[-1] += ' '
                    # Replace hyphen characters by a regular hypthen
                    elif template_name in ['nbhyph', 'nbh']:
                        template_stack[-1] += '-'
                    # Replace dash characters by two regular hyphens
                    elif template_name in ['ndash', 'en dash', 'nsndns', '--', \
                                        'emdash', 'mdash', 'em dash']:
                        template_stack[-1] += '--'
                    # Replace the spaced dash character by two regular hyphens in spaces
                    elif template_name in ['snd', 'spnd', 'sndash', 'spndash', \
                                        'snds', 'spndsp', 'sndashs', 'spndashsp']:
                        template_stack[-1] += ' -- '
                    # Replace the circa template
                    elif template_name == 'circa':
                        template_stack[-1] += 'c. '
                    # Replace the floruit template
                    elif template_name in ['fl', 'fl.']:
                        template_stack[-1] += 'fl. '
                    # ...
                    elif template_name == 'solar mass':
                        template_stack[-1] += 'M'
                    # ...
                    elif template_name == 'music':
                        if stack_element[1] == 'time':
                            template_stack[-1] += stack_element[2] + '/' + stack_element[3]
                        elif stack_element[1] == 'scale':
                            template_stack[-1] += stack_element[2]
                        else:
                            template_stack[-1] += stack_element[1]
                    # Templates that should be removed entirely
                    elif template_name in ['shy', 'okina', 'zwj', 'zwsp', '0ws', 'sic', \
                                           'glossary', 'glossary end', 'startflatlist', 'endflatlist', \
                                           'plainlist', 'endplainlist', 'flowlist', 'endflowlist', \
                                           'featured article', 'clear', 'nom', 'won', 'kos', 'loc']:
                        pass
                    # Language template
                    elif template_name in ['lang', 'transl']:
                        logging.debug('Language template: %s', repr(stack_element))
                        if stack_element[2] in ['DIN', 'ISO', 'ALA']:
                            template_stack[-1] += stack_element[3]
                        else:
                            template_stack[-1] += stack_element[2]
                    elif len(stack_element) == 1:
                        logging.debug('Name of template of length 1: %s', template_name)
                        # Templates that stay the way they are
                        template_stack[-1] += template_name
                    elif len(stack_element) > 1:
                        logging.debug('Template of length > 1: %s', repr(stack_element))
                        if template_name == 'chem':
                            template_stack[-1] += ''.join(stack_element[1:])
                        elif template_name in ['small', 'smaller', 'midsize', \
                                               'larger', 'big', 'large', 'huge', 'nobold', \
                                               'nocaps', 'noitalic', 'nowrap']:
                            template_stack[-1] += stack_element[1]
                        else:
                            # Keep the second argument
                            template_stack[-1] += stack_element[1]
                    prev_char = ''
                else:
                    prev_char = char
            # Normal char inside a template
            elif len(template_stack) > 0:
                template_stack[-1] += char
                prev_char = char
            else:
                prev_char = char
        if test > 0: logging.debug('Result: %s' % template_stack[-1])
        return template_stack[-1]
