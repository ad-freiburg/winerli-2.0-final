import pytest
import sys
from wiki_parsing import *


def test_lnrm_repr():
    assert lnrm_repr('') == 'lnrm__'
    assert lnrm_repr('Germany') == 'lnrm__germany'
    assert lnrm_repr('Iron Maiden') == 'lnrm__ironmaiden'
    assert lnrm_repr('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n ') == 'lnrm__'
    assert lnrm_repr('Fear of the Dark (Iron Maiden album)') == 'lnrm__fearofthedarkironmaidenalbum'
    assert lnrm_repr('"Fear of the Dark" (song)') == 'lnrm__fearofthedarksong'
    assert lnrm_repr('Cat\'s eye') == 'lnrm__catseye'


def test_lnrm_repr_baumert():
    assert lnrm_repr('', baumert=True) == 'lnrm__'
    assert lnrm_repr('Germany', baumert=True) == 'lnrm__germany'
    assert lnrm_repr('Iron Maiden', baumert=True) == 'lnrm__ironmaiden'
    assert lnrm_repr('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n ', baumert=True) == 'lnrm__"$%&\'*+/:;<=>@^`|~'
    assert lnrm_repr('Fear of the Dark (Iron Maiden album)', baumert=True) == 'lnrm__fearofthedarkironmaidenalbum'
    assert lnrm_repr('"Fear of the Dark" (song)', baumert=True) == 'lnrm__"fearofthedark"song'
    assert lnrm_repr('Cat\'s eye', baumert=True) == "lnrm__cat'seye"


def test_wiki_format():
    assert wiki_format('Germany') == 'Germany'
    assert wiki_format('germany') == 'Germany'
    assert wiki_format('Fear of the Dark (Iron Maiden album)') == 'Fear_of_the_Dark_(Iron_Maiden_album)'
    assert wiki_format('fear of the dark') == 'Fear_of_the_dark'
    assert wiki_format('bLA bLUB') == 'BLA_bLUB'
    assert wiki_format('BLA bLUB') == 'BLA_bLUB'
    assert wiki_format('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n ') == '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    assert wiki_format('Cat\'s eye') == 'Cat\'s_eye'


def test_parse_index():
    index_file = '/input/testindex.txt.bz2'
    parsed_index = parse_index(index_file)
    assert len(parsed_index) == 20
    assert parsed_index[0] == (599, 654485, 654485 - 599)
    assert parsed_index[1] == (654485, 2105081, 2105081 - 654485)
    assert parsed_index[2] == (2105081, 3596750, 3596750 - 2105081)
    assert parsed_index[-2] == (17561854, 18223852, 18223852 - 17561854)
    assert parsed_index[-1] == (18223852, None, -1)


if __name__ == "__main__":
    pytest.main(sys.argv)
