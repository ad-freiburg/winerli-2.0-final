""" Johanna Götz """

import pytest
import sys
from parse_info import InfoboxLinkParser


def test__trim_string():
    ilp = InfoboxLinkParser('')
    assert ilp._trim_string('') == ''
    assert ilp._trim_string('\r') == ''
    assert ilp._trim_string('\n') == ''
    assert ilp._trim_string('\t') == ''
    assert ilp._trim_string('\r\ntest\t') == 'test'


def test__parse_link_1():
    # Parse a single link
    s = """[[Fear of the Dark (song)|Fear of the Dark]]"""
    ilp = InfoboxLinkParser(s)
    ilp._parse_link()
    result = ilp.get_links()
    assert result == [('Fear of the Dark (song)', 'Fear of the Dark')]


def test__parse_link_2():
    # Parse a single link
    s = """[[Iron Maiden]]"""
    ilp = InfoboxLinkParser(s)
    ilp._parse_link()
    result = ilp.get_links()
    assert result == [('Iron Maiden', 'Iron Maiden')]


def test__parse_link_3():
    # Parse a single link
    s = """"""
    ilp = InfoboxLinkParser(s)
    ilp._parse_link()
    result = ilp.get_links()
    assert result == []


def test_parse_1():
    # Several links inside of a string
    s = """
    '''''Arachnophobia''''' is a 1990 American [[black comedy]] [[horror film]]
    directed by [[Frank Marshall (producer)|Frank Marshall]]
    """
    ilp = InfoboxLinkParser(s)
    ilp.parse()
    result = ilp.get_links()
    assert result == [('black comedy', 'black comedy'),
                      ('horror film', 'horror film'),
                      ('Frank Marshall (producer)', 'Frank Marshall')]


def test_parse_2():
    # The image will be ignored but the links in the description will be extracted
    s = """
    [[Image:Kai Hansen.jpg|180px|thumb|[[Kai Hansen]] of [[Gamma Ray (band)|Gamma Ray]],
    ex-[[Helloween]] during a show in Barcelona, Spain.
    Hansen is widely regarded as the "godfather of power metal".]]
    """
    ilp = InfoboxLinkParser(s)
    ilp.parse()
    result = ilp.get_links()
    assert result == [('Kai Hansen', 'Kai Hansen'),
                      ('Gamma Ray (band)', 'Gamma Ray'),
                      ('Helloween', 'Helloween')]


def test_parse_3():
    # The image will be ignored but the links in the description will be extracted
    s = """
    {{Infobox book
    | name     = Coraline
    | title_orig  =
    | translator  =
    | image     = Coraline.jpg
    | caption = Front cover by Dave McKean
    | author    = [[Neil Gaiman]]
    | illustrator  = [[Dave McKean]]
    | cover_artist = Dave Mckean
    | country    = United Kingdom
    | language   = English
    | series    =
    | subject    =
    | genre     = [[Dark fantasy]]
    | publisher   = [[Bloomsbury]] (UK)&lt;br /&gt;[[Harper Collins]] (US)
    | release_date = 24 February 2002
    | english_release_date =
    | media_type  = Print, [[e-book]], [[audiobook]]
    | pages     = 163
    | dewey = 813
    | isbn     =0-06-113937-8
    | oclc= 71822484
    | congress = PZ7.G1273 Co 2002
    | preceded_by  =
    | followed_by  =
    }}
    """
    ilp = InfoboxLinkParser(s)
    ilp.parse()
    result_links = ilp.get_links()
    result_infoboxes = ilp.get_infoboxes()
    assert result_links == [('Neil Gaiman', 'Neil Gaiman'),
                            ('Dave McKean', 'Dave McKean'),
                            ('Dark fantasy', 'Dark fantasy'),
                            ('Bloomsbury', 'Bloomsbury'),
                            ('Harper Collins', 'Harper Collins'),
                            ('e-book', 'e-book'),
                            ('audiobook', 'audiobook')]
    assert result_infoboxes == [('book',
                                {'name': 'Coraline',
                                 'title_orig': '',
                                 'translator': '',
                                 'image': 'Coraline.jpg',
                                 'caption': 'Front cover by Dave McKean',
                                 'author': 'Neil Gaiman',
                                 'illustrator': 'Dave McKean',
                                 'cover_artist': 'Dave Mckean',
                                 'country': 'United Kingdom',
                                 'language': 'English',
                                 'series': '',
                                 'subject': '',
                                 'genre': 'Dark fantasy',
                                 'publisher': 'Bloomsbury (UK)&lt;br /&gt;Harper Collins (US)',
                                 'release_date': '24 February 2002',
                                 'english_release_date': '',
                                 'media_type': 'Print, e-book, audiobook',
                                 'pages': '163',
                                 'dewey': '813',
                                 'isbn': '0-06-113937-8',
                                 'oclc': '71822484',
                                 'congress': 'PZ7.G1273 Co 2002',
                                 'preceded_by': '',
                                 'followed_by': ''}
                                 )]


def test_parse_4():
    # The image will be ignored but the links in the description will be extracted
    s = """
    {{Short description|Order of flying mammals}}
    {{Use dmy dates|date=November 2020}}
    {{Use British English|date=November 2017}}
    {{Automatic taxobox
    |name = Bat
    |fossil_range = {{Fossil range|52|0|[[Eocene]]–[[Holocene|Present]]}}
    |image = <imagemap>
    File:Wikipedia-Bats-001-v01.jpg|300px
    rect 0 0 820 510 [[Common vampire bat]]
    rect 0 510 820 950 [[Greater horseshoe bat]]
    rect 0 950 820 1560 [[Greater short-nosed fruit bat]]
    rect 1520 0 820 510 [[Egyptian fruit bat]]
    rect 1520 510 820 950 [[Mexican free-tailed bat]]
    rect 1520 950 820 1560 [[Greater mouse-eared bat]]
    </imagemap>
    |taxon = Chiroptera
    |authority = [[Johann Friedrich Blumenbach|Blumenbach]], 1779
    |subdivision_ranks = Suborders
    |subdivision =
    (traditional):
    * [[Megachiroptera]]
    * [[Microchiroptera]]
    (present):
    * [[Yinpterochiroptera]]
    * [[Yangochiroptera]]
    |range_map = Bat range.png
    |range_map_caption = Worldwide distribution of bat species
    }}
    """
    ilp = InfoboxLinkParser(s)
    ilp.parse()
    result_links = ilp.get_links()
    result_infoboxes = ilp.get_infoboxes()
    assert result_links == [('Eocene', 'Eocene'),
                            ('Holocene', 'Present'),
                            ('Common vampire bat', 'Common vampire bat'),
                            ('Greater horseshoe bat', 'Greater horseshoe bat'),
                            ('Greater short-nosed fruit bat', 'Greater short-nosed fruit bat'),
                            ('Egyptian fruit bat', 'Egyptian fruit bat'),
                            ('Mexican free-tailed bat', 'Mexican free-tailed bat'),
                            ('Greater mouse-eared bat', 'Greater mouse-eared bat'),
                            ('Johann Friedrich Blumenbach', 'Blumenbach'),
                            ('Megachiroptera', 'Megachiroptera'),
                            ('Microchiroptera', 'Microchiroptera'),
                            ('Yinpterochiroptera', 'Yinpterochiroptera'),
                            ('Yangochiroptera', 'Yangochiroptera')]
    assert result_infoboxes == [('',
                                {'authority': 'Blumenbach, 1779',
                                 'fossil_range': '{{Fossil range|52|0|Eocene–Present}}',
                                 'image': '<imagemap>\n' +
                                          '    File:Wikipedia-Bats-001-v01.jpg|300px\n' +
                                          '    rect 0 0 820 510 Common vampire bat\n' +
                                          '    rect 0 510 820 950 Greater horseshoe bat\n' +
                                          '    rect 0 950 820 1560 Greater short-nosed fruit bat\n' +
                                          '    rect 1520 0 820 510 Egyptian fruit bat\n' +
                                          '    rect 1520 510 820 950 Mexican free-tailed bat\n' +
                                          '    rect 1520 950 820 1560 Greater mouse-eared bat\n' +
                                          '    </imagemap>',
                                 'name': 'Bat',
                                 'range_map': 'Bat range.png',
                                 'range_map_caption': 'Worldwide distribution of bat species',
                                 'subdivision': '(traditional):\n' +
                                                '    * Megachiroptera\n' +
                                                '    * Microchiroptera\n' +
                                                '    (present):\n' +
                                                '    * Yinpterochiroptera\n' +
                                                '    * Yangochiroptera',
                                 'subdivision_ranks': 'Suborders',
                                 'taxon': 'Chiroptera'}
                                 )]


def test_parse_5():
    # The image will be ignored but the links in the description will be extracted
    s = """
    {{Infobox galaxy
    |name=Milky Way
    |ra={{RA|17|45|40.0409}}
    |dec={{DEC|−29|0|28.118}}
    |constellation name=[[Sagittarius (constellation)|Sagittarius]]
    |dist_ly={{convert|7.86|-|8.32|kpc|kly|order=flip|abbr=on}}
             <ref name="boehle2016"/><ref name="Gillessen2016"/>
    |image=[[File:ESO-VLT-Laser-phot-33a-07.jpg|300px]]
    |mass={{val|0.8|-|1.5|e=12|u=}}<ref name="McMillan2011"/>
            <ref name="McMillan2016"/>
            <ref name="Kafle2012"/>
            <ref name="Kafle2014"/>
    |type=Sb, Sbc, or SB(rs)bc<ref name=ssr100_1_129/><ref>
          {{cite web |first1=Hartmut |last1=Frommert |first2=Christine
            |last2=Kronberg |date=August 26, 2005
            |url=http://messier.seds.org/more/mw_type.html
            |title=Classification of the Milky Way Galaxy
            |access-date=May 30, 2015 |work=SEDS |url-status=live
            |archive-url=https://web.archive.org/web/20150531031937/http://messier.seds.org/more/mw_type.html
            |archive-date=May 31, 2015}}</ref><br />
          ([[barred spiral galaxy]])
    |stars={{nowrap|100–400 billion}}
    |size=[[Stellar disk]]: 185 ± 15 kly <ref name="nbcnews1" /><ref>
          {{Cite web|url=https://www.space.com/41047-milky-way-galaxy-size-bigger-than-thought.html
            |title=It Would Take 200,000 Years at Light Speed to Cross the Milky Way
            |first=Elizabeth Howell 02|last=July 2018|website=Space.com}}</ref><br>
          [[Dark matter halo]]: {{convert|1.9|±|0.4|Mly|kpc|abbr=on|lk=on}}
          <ref name="croswell2020" /><ref name="dearson2020" />}}
    """
    ilp = InfoboxLinkParser(s)
    ilp.parse()
    result_links = ilp.get_links()
    result_infoboxes = ilp.get_infoboxes()
    assert result_links == [('Sagittarius (constellation)', 'Sagittarius'),
                            ('File:ESO-VLT-Laser-phot-33a-07.jpg', '300px'),
                            ('barred spiral galaxy', 'barred spiral galaxy'),
                            ('Stellar disk', 'Stellar disk'),
                            ('Dark matter halo', 'Dark matter halo')]
    assert result_infoboxes == [('galaxy',
                                {'name': 'Milky Way',
                                 'ra': '{{RA|17|45|40.0409}}',
                                 'dec': '{{DEC|−29|0|28.118}}',
                                 'constellation name': 'Sagittarius',
                                 'dist_ly': '{{convert|7.86|-|8.32|kpc|kly|order=flip|abbr=on}}\n' +
                                            '             <ref name="boehle2016"/><ref ' +
                                            'name="Gillessen2016"/>',
                                 'image': '300px',
                                 'mass': '{{val|0.8|-|1.5|e=12|u=}}<ref name="McMillan2011"/>\n' +
                                         '            <ref name="McMillan2016"/>\n' +
                                         '            <ref name="Kafle2012"/>\n' +
                                         '            <ref name="Kafle2014"/>',
                                 'type': 'Sb, Sbc, or SB(rs)bc<ref name=ssr100_1_129/><ref>\n'
                                         '          {{cite web |first1=Hartmut |last1=Frommert |first2=Christine\n'
                                         '            |last2=Kronberg |date=August 26, 2005\n'
                                         '            |url=http://messier.seds.org/more/mw_type.html\n'
                                         '            |title=Classification of the Milky Way Galaxy\n'
                                         '            |access-date=May 30, 2015 |work=SEDS |url-status=live\n'
                                         '            |archive-url=https://web.archive.org/web/20150531031937/http://messier.seds.org/more/mw_type.html\n'
                                         '            |archive-date=May 31, 2015}}</ref><br />\n'
                                         '          (barred spiral galaxy)',
                                 'stars': '{{nowrap|100–400 billion}}',
                                 'size': 'Stellar disk: 185 ± 15 kly <ref name="nbcnews1" /><ref>\n'
                                         '          {{Cite web|url=https://www.space.com/41047-milky-way-galaxy-size-bigger-than-thought.html\n'
                                         '            |title=It Would Take 200,000 Years at Light Speed to Cross the Milky Way\n'
                                         '            |first=Elizabeth Howell 02|last=July 2018|website=Space.com}}</ref><br>\n'
                                         '          Dark matter halo: {{convert|1.9|±|0.4|Mly|kpc|abbr=on|lk=on}}\n'
                                         '          <ref name="croswell2020" /><ref name="dearson2020" />'
                                 }
                                 )]


def test_parse_6():
    # Comments inside of infoboxes in separate lines
    s = """
    {{Infobox book

    | name         = Blade Runner 3: Replicant Night
    | author       = [[K. W. Jeter]]
    | language     = English
    | country      = United States
    | genre        = [[Science fiction]]

    | publisher    = [[Bantam Spectra|Spectra]]
    | isbn         = 0-553-09983-3
    | <!-- See Wikipedia:WikiProject_Novels or Wikipedia:WikiProject_Books -->
    | title_orig   =

    | translator   =

    | image        = Blade Runner 3 Replicant Night KW Jeter cover.jpeg
    | caption =Cover of the first edition

    | cover_artist =

    | series       = ''[[Blade Runner (franchise)|Blade Runner]]''
    | subject      =

    | release_date = October 1, 1996
    | media_type   = Print ([[Hardcover]], [[Paperback]])
    | pages        = 321
    | dewey= 813/.54 20
    | congress= PS3560.E85 B59 1996
    | oclc= 34669233
    | preceded_by  = [[Blade Runner 2: The Edge of Human|The Edge of Human]]
    | followed_by  = [[Blade Runner 4: Eye and Talon|Eye and Talon]]
    }}
    """
    ilp = InfoboxLinkParser(s)
    ilp.parse()
    result_links = ilp.get_links()
    result_infoboxes = ilp.get_infoboxes()
    # The links themselves will have a link text that got stripped of some basic templates
    assert result_links == [('K. W. Jeter', 'K. W. Jeter'),
                            ('Science fiction', 'Science fiction'),
                            ('Bantam Spectra', 'Spectra'),
                            ('Blade Runner (franchise)', 'Blade Runner'),
                            ('Hardcover', 'Hardcover'),
                            ('Paperback', 'Paperback'),
                            ('Blade Runner 2: The Edge of Human', 'The Edge of Human'),
                            ('Blade Runner 4: Eye and Talon', 'Eye and Talon')]
    # Inside of infoboxes link texts will undergo some basic template stripping
    assert result_infoboxes == [('book',
                                 {'name': 'Blade Runner 3: Replicant Night',
                                  'author': 'K. W. Jeter',
                                  'language': 'English',
                                  'country': 'United States',
                                  'genre': 'Science fiction',
                                  'publisher': 'Spectra',
                                  'isbn': '0-553-09983-3',
                                  'title_orig': '',
                                  'translator': '',
                                  'image': 'Blade Runner 3 Replicant Night KW Jeter cover.jpeg',
                                  'caption': 'Cover of the first edition',
                                  'cover_artist': '',
                                  'series': '\'\'Blade Runner\'\'',
                                  'subject': '',
                                  'release_date': 'October 1, 1996',
                                  'media_type': 'Print (Hardcover, Paperback)',
                                  'pages': '321',
                                  'dewey': '813/.54 20',
                                  'congress': 'PS3560.E85 B59 1996',
                                  'oclc': '34669233',
                                  'preceded_by': 'The Edge of Human',
                                  'followed_by': 'Eye and Talon'
                                  }
                                 )]


def test_parse_7():
    # Templates inside of link texts in infoboxes which will be stripped
    s = """
    {{Infobox Bilateral relations|Danish-Fijian|Denmark|Fiji}}
    """
    ilp = InfoboxLinkParser(s)
    ilp.parse()
    result_links = ilp.get_links()
    result_infoboxes = ilp.get_infoboxes()
    # The links themselves will have a link text that got stripped of some basic templates
    assert result_links == []
    # Inside of infoboxes link texts will undergo some basic template stripping
    assert result_infoboxes == [('bilateral relations', {})]


def test_parse_8():
    # Templates inside of link texts in infoboxes which will be stripped
    s = """
    {{Infobox Bilateral relations|Ecuadorian–American|Ecuador|USA|map = Ecuador USA Locator 2.svg}}
    """
    ilp = InfoboxLinkParser(s)
    ilp.parse()
    result_links = ilp.get_links()
    result_infoboxes = ilp.get_infoboxes()
    # The links themselves will have a link text that got stripped of some basic templates
    assert result_links == []
    # Inside of infoboxes link texts will undergo some basic template stripping
    assert result_infoboxes == [('bilateral relations',
                                {'map': 'Ecuador USA Locator 2.svg'}
                                 )]


def test_parse_9():
    # Templates inside of link texts in infoboxes which will be stripped
    s = """
    {{Infobox bilateral relations|Canadian–American|Canada|USA|filetype=svg|
    mission1 = [[Embassy of Canada, Washington, D.C.|Canadian Embassy, Washington, D.C.]]|
    mission2 = [[Embassy of the United States, Ottawa|United States Embassy, Ottawa]]|
    envoytitle1 = [[List of Canadian ambassadors to the United States|Ambassador]]}}
    """
    ilp = InfoboxLinkParser(s)
    ilp.parse()
    result_links = ilp.get_links()
    result_infoboxes = ilp.get_infoboxes()
    # The links themselves will have a link text that got stripped of some basic templates
    assert result_links == [('Embassy of Canada, Washington, D.C.', 'Canadian Embassy, Washington, D.C.'),
                            ('Embassy of the United States, Ottawa', 'United States Embassy, Ottawa'),
                            ('List of Canadian ambassadors to the United States', 'Ambassador')]
    # Inside of infoboxes link texts will undergo some basic template stripping
    assert result_infoboxes == [('bilateral relations',
                                {'filetype': 'svg',
                                 'mission1': 'Canadian Embassy, Washington, D.C.',
                                 'mission2': 'United States Embassy, Ottawa',
                                 'envoytitle1': 'Ambassador'}
                                 )]


def test_parse_10():
    # Templates inside of link texts in infoboxes which will be stripped
    s = """
    {{Infobox testtest
    |test_entry = Bla bla [[Test link|This is a test{{nbhyph}}link]]
    |2nd_test_entry = Here's another test link: [[This is a wikilink|{{lang|de|Link zum Testen}}]]
    }}
    """
    ilp = InfoboxLinkParser(s)
    ilp.parse()
    result_links = ilp.get_links()
    result_infoboxes = ilp.get_infoboxes()
    # The links themselves will have a link text that got stripped of some basic templates
    assert result_links == [('Test link', 'This is a test-link'),
                            ('This is a wikilink', 'Link zum Testen')]
    # Inside of infoboxes link texts will undergo some basic template stripping
    assert result_infoboxes == [('testtest',
                                 {'test_entry': 'Bla bla This is a test-link',
                                  '2nd_test_entry': 'Here\'s another test link: Link zum Testen'}
                                 )]


def test_strip_templates():
    ilp = InfoboxLinkParser('')
    assert ilp.strip_templates('') == ''
    assert ilp.strip_templates('{{nbsp}}') == ' '
    assert ilp.strip_templates('{{nbhyph}}') == '-'
    assert ilp.strip_templates('{{emdash}}') == '--'
    assert ilp.strip_templates('{{solar mass}}') == 'M'
    assert ilp.strip_templates('50 {{solar mass}}') == '50 M'
    assert ilp.strip_templates('{{lang|de|Bla}}') == 'Bla'
    assert ilp.strip_templates('{{lang|de|DIN|Bla}}') == 'Bla'
    assert ilp.strip_templates('{{smaller|Bla}}') == 'Bla'
    assert ilp.strip_templates('Blub {{smaller|Bla}}') == 'Blub Bla'
    assert ilp.strip_templates(
        '''Blub {{smaller|Bla}} {{nbsp}} {{nowrap|Blub}}'''
    ) == 'Blub Bla   Blub'
    assert ilp.strip_templates('{{music|time|3|4}}') == '3/4'
    assert ilp.strip_templates('{{music|scale|Bla}}') == 'Bla'
    assert ilp.strip_templates('{{pi}}') == 'pi'
    assert ilp.strip_templates('{{okina}}') == ''
    assert ilp.strip_templates('{{okina}}{{shy}}{{won}}') == ''
    assert ilp.strip_templates('{{chem|A|B|C|D}}') == 'ABCD'


if __name__ == "__main__":
    pytest.main(sys.argv)
