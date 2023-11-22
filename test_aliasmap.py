""" Johanna Götz """

import pytest
from create_aliasmap_multi import *


BAUMERT = False


@pytest.fixture
def aliasmap_db():
    return Database('/test_output/aliasmap_test.db', read_only=True)


@pytest.fixture
def links_db():
    return Database('/test_output/links_db_test.db', read_only=True)


@pytest.fixture
def page_category_db():
    return Database('/test_output/page_category_db_test.db', read_only=True)


@pytest.fixture
def infobox_category():
    with open('/test_output/infobox_category_test.tsv', 'r', encoding='UTF-8') as this_file:
        infobox_category_content = this_file.readlines()
    return infobox_category_content


def test_aliasmap(aliasmap_db):
    count = aliasmap_db.query(
        """SELECT COUNT(*) FROM `aliasmap`;"""
    )
    assert count[0][0] == 4478

    result_1 = aliasmap_db.query(
        """SELECT * FROM `aliasmap` WHERE `lnrm` = 'lnrm__abcdefgh';"""
    )
    assert len(result_1) == 0

    result_2 = aliasmap_db.query(
        """SELECT * FROM `aliasmap` WHERE `lnrm` = 'lnrm__fearofthedark' ORDER BY `wikilink`;"""
    )
    assert len(result_2) == 3
    assert result_2[0] == ('lnrm__fearofthedark', 'Fear_of_the_Dark_(Iron_Maiden_album)', 6, pytest.approx(0.66666, 0.0001))
    assert result_2[1] == ('lnrm__fearofthedark', 'Fear_of_the_Dark_(song)', 2, pytest.approx(0.22222, 0.0001))
    assert result_2[2] == ('lnrm__fearofthedark', 'Fear_of_the_dark', 1, pytest.approx(0.11111, 0.0001))

    result_3 = aliasmap_db.query(
        """SELECT * FROM `aliasmap` WHERE `wikilink` = 'Fear_of_the_Dark_(song)' ORDER BY `lnrm`;"""
    )
    assert len(result_3) == 4
    assert result_3[0] == ('lnrm__fearofthedark', 'Fear_of_the_Dark_(song)', 2, pytest.approx(0.22222, 0.0001))
    # This comes from the infobox
    assert result_3[1] == ('lnrm__fearofthedarklivein1992', 'Fear_of_the_Dark_(song)', 1, 1.0)
    # This comes from a link and from a page title
    assert result_3[2] == ('lnrm__fearofthedarksong', 'Fear_of_the_Dark_(song)', 2, 1.0)
    assert result_3[3] == ('lnrm__titletrack', 'Fear_of_the_Dark_(song)', 1, 0.5)

    result_4 = aliasmap_db.query(
        """SELECT * FROM `aliasmap` WHERE `wikilink` = 'Fear_of_the_dark' ORDER BY `lnrm`;"""
    )
    assert len(result_4) == 1
    assert result_4[0] == ('lnrm__fearofthedark', 'Fear_of_the_dark', 1, pytest.approx(0.11111, 0.0001))

    result_5 = aliasmap_db.query(
        """SELECT * FROM `aliasmap` WHERE `lnrm` = 'lnrm__acappella' ORDER BY `wikilink`;"""
    )
    assert len(result_5) == 1
    assert result_5[0] == ('lnrm__acappella', 'A_cappella', 2, 1.0)

    result_6 = aliasmap_db.query(
        """SELECT * FROM `aliasmap` WHERE `wikilink` = 'A_cappella' ORDER BY `lnrm`;"""
    )
    assert len(result_6) == 1
    assert result_6[0] == ('lnrm__acappella', 'A_cappella', 2, 1.0)

    result_7 = aliasmap_db.query(
        """SELECT * FROM `aliasmap` WHERE `lnrm` = 'lnrm__german'  ORDER BY `wikilink`;"""
    )
    assert len(result_7) == 4
    assert result_7[0] == ('lnrm__german', 'German_Reich', 1, pytest.approx(0.11111, 0.0001))
    assert result_7[1] == ('lnrm__german', 'German_language', 5, pytest.approx(0.55555, 0.0001))
    assert result_7[2] == ('lnrm__german', 'Germans', 2, pytest.approx(0.22222, 0.0001))
    assert result_7[3] == ('lnrm__german', 'Media_Control_Charts', 1, pytest.approx(0.11111, 0.0001))

    result_8 = aliasmap_db.query(
        """SELECT * FROM `aliasmap` WHERE `wikilink` = 'German_language' ORDER BY `lnrm`;"""
    )
    assert len(result_8) == 1
    assert result_8[0] == ('lnrm__german', 'German_language', 5, pytest.approx(0.55555, 0.0001))

    result_9 = aliasmap_db.query(
        """SELECT * FROM `aliasmap` WHERE `wikilink` = 'Germans' ORDER BY `lnrm`;"""
    )
    assert len(result_9) == 2
    assert result_9[0] == ('lnrm__german', 'Germans', 2, pytest.approx(0.22222, 0.0001))
    assert result_9[1] == ('lnrm__germans', 'Germans', 1, 1.0)


def test_redirects(aliasmap_db):
    count = aliasmap_db.query(
        """SELECT COUNT(*) FROM `redirects`;"""
    )
    assert count[0][0] == 5
    count = aliasmap_db.query(
        """SELECT COUNT(*) FROM `redirects` WHERE `target` <> '__DISAMBIGUATION__';"""
    )
    assert count[0][0] == 2
    result_1 = aliasmap_db.query(
        """SELECT * FROM `redirects` WHERE `wikilink` = 'Heavy_metal_(disambiguation)' ORDER BY `target`;"""
    )
    assert len(result_1) == 1
    assert result_1 == [('Heavy_metal_(disambiguation)', 'Heavy_metal')]
    result_2 = aliasmap_db.query(
        """SELECT * FROM `redirects` WHERE `wikilink` = 'Metal_music' ORDER BY `target`;"""
    )
    assert len(result_2) == 1
    assert result_2 == [('Metal_music', 'Heavy_metal_music')]
    result_3 = aliasmap_db.query(
        """SELECT * FROM `redirects` WHERE `wikilink` = 'Black Sabbath' ORDER BY `target`;"""
    )
    assert len(result_3) == 0
    assert result_3 == []
    result_4 = aliasmap_db.query(
        """SELECT * FROM `redirects` WHERE `target` = '__DISAMBIGUATION__' ORDER BY `wikilink`;"""
    )
    assert len(result_4) == 3
    assert result_4[0] == ('Fear_of_the_Dark', '__DISAMBIGUATION__')
    assert result_4[1] == ('Heavy_metal', '__DISAMBIGUATION__')
    assert result_4[2] == ('Metal_(disambiguation)', '__DISAMBIGUATION__')


def test_article_pages(aliasmap_db):
    count = aliasmap_db.query(
        """SELECT COUNT(*) FROM `article_pages`;"""
    )
    assert count[0][0] == 22
    result_1 = aliasmap_db.query(
        """SELECT * FROM `article_pages`;"""
    )
    assert len(result_1) == 22
    assert result_1[0] == ('Germany',)
    assert result_1[1] == ('German_Empire',)
    assert result_1[2] == ('Palace_of_Versailles',)
    assert result_1[3] == ('Metal_(disambiguation)',)
    assert result_1[4] == ('Heavy_metal_(disambiguation)',)
    assert result_1[5] == ('Heavy_metal',)
    assert result_1[6] == ('Metal_music',)
    assert result_1[7] == ('Heavy_metal_music',)
    assert result_1[8] == ('Iron_Maiden',)
    assert result_1[9] == ('Steve_Harris_(musician)',)
    assert result_1[10] == ('Fear_of_the_Dark_(song)',)
    assert result_1[11] == ('Afraid_to_Shoot_Strangers',)
    assert result_1[12] == ('Power_metal',)
    assert result_1[13] == ('Fear_of_the_Dark',)
    assert result_1[14] == ('Nightwish',)
    assert result_1[15] == ('Metal:_A_Headbanger\'s_Journey',)
    assert result_1[16] == ('Metal_Evolution',)
    assert result_1[17] == ('Deathgasm',)
    assert result_1[18] == ('Arachnophobia_(film)',)
    assert result_1[19] == ('Coraline',)
    assert result_1[20] == ('And_Then_There_Were_None',)
    assert result_1[21] == ('Real_Humans',)


def test_links(links_db):
    count = links_db.query(
        """SELECT COUNT(*) FROM `links`;"""
    )
    assert count[0][0] == 4993

    result_1 = links_db.query(
        """SELECT * FROM `links` WHERE `wikilink` = 'Real_Humans' ORDER BY ROWID;"""
    )
    assert len(result_1) == 43
    assert result_1[0] == ('Real_Humans', 'Drama')
    assert result_1[1] == ('Real_Humans', 'Science_fiction')
    assert result_1[2] == ('Real_Humans', 'Sveriges_Television')
    assert result_1[3] == ('Real_Humans', 'Matador_Film_AB')
    assert result_1[4] == ('Real_Humans', 'Shine_Group')
    assert result_1[5] == ('Real_Humans', 'Humans_(TV_series)')
    assert result_1[6] == ('Real_Humans', 'Swedish_television')
    assert result_1[7] == ('Real_Humans', 'Android_(robot)')
    assert result_1[8] == ('Real_Humans', 'Robot')
    assert result_1[9] == ('Real_Humans', 'SVT1')
    assert result_1[10] == ('Real_Humans', 'Harald_Hamrell')
    assert result_1[11] == ('Real_Humans', 'Resumé.se')
    assert result_1[12] == ('Real_Humans', 'YouTube')
    assert result_1[13] == ('Real_Humans', 'Pac-Man_(character)')
    assert result_1[14] == ('Real_Humans', 'Three_Laws_of_Robotics')
    assert result_1[15] == ('Real_Humans', 'Marie_Robertson')
    assert result_1[16] == ('Real_Humans', 'Leif_Andrée')
    assert result_1[17] == ('Real_Humans', 'Kåre_Hedebrant')
    assert result_1[18] == ('Real_Humans', 'Sten_Elfström')
    assert result_1[19] == ('Real_Humans', 'Lisette_Pagler')
    assert result_1[20] == ('Real_Humans', 'Andreas_Wilson')
    assert result_1[21] == ('Real_Humans', 'Flashback_(narrative)')
    assert result_1[22] == ('Real_Humans', 'Eva_Röse')
    assert result_1[23] == ('Real_Humans', 'André_Sjöberg')
    assert result_1[24] == ('Real_Humans', 'Josephine_Alhanko')
    assert result_1[25] == ('Real_Humans', 'Johannes_Bah_Kuhnke')
    assert result_1[26] == ('Real_Humans', 'Thomas_W._Gabrielsson')
    assert result_1[27] == ('Real_Humans', 'Måns_Nathanaelson')
    assert result_1[28] == ('Real_Humans', 'Ellen_Mattsson')
    assert result_1[29] == ('Real_Humans', 'Shebly_Niavarani')
    assert result_1[30] == ('Real_Humans', 'Karin_Bertling')
    assert result_1[31] == ('Real_Humans', 'Jonas_Malmsjö')
    assert result_1[32] == ('Real_Humans', 'Io9')
    assert result_1[33] == ('Real_Humans', 'The_Australian')
    assert result_1[34] == ('Real_Humans', 'Kudos_Film_&_Television')
    assert result_1[35] == ('Real_Humans', 'Shine_Limited')
    assert result_1[36] == ('Real_Humans', 'Channel_4')
    assert result_1[37] == ('Real_Humans', 'UK')
    assert result_1[38] == ('Real_Humans', 'AMC_(TV_channel)')
    assert result_1[39] == ('Real_Humans', 'US')
    assert result_1[40] == ('Real_Humans', 'Canada')
    assert result_1[41] == ('Real_Humans', 'ABC_(Australian_TV_channel)')
    assert result_1[42] == ('Real_Humans', 'Australia')

    result_2 = links_db.query(
        """SELECT * FROM `links` WHERE `wikilink` = 'Pizza';"""
    )
    assert len(result_2) == 0


def test_categories(page_category_db):
    count = page_category_db.query(
        """SELECT COUNT(*) FROM `categories`;"""
    )
    assert count[0][0] == 20
    result_1 = page_category_db.query(
        """SELECT * FROM `categories` WHERE `wikilink` = 'And_Then_There_Were_None';"""
    )
    assert len(result_1) == 1
    assert result_1[0] == ('And_Then_There_Were_None', '["1939 British novels", "Novels by Agatha Christie", "Works originally published in The Saturday Evening Post", "Novels first published in serial form", "Novels set in the 1930s", "Novels set in Devon", "British novels adapted into films", "Collins Crime Club books", "Novels set on islands", "British novels adapted into plays", "Novels adapted into video games", "Novels adapted into television programs", "Novels adapted into radio programs"]')
    result_2 = page_category_db.query(
        """SELECT * FROM `categories` WHERE `wikilink` = 'Palace_of_Versailles';"""
    )
    assert len(result_2) == 1
    assert result_2[0] == ('Palace_of_Versailles', '["Palace of Versailles", "Art museums and galleries in France", "Baroque architecture at Versailles", "Baroque palaces", "Buildings and structures completed in 1672", "Buildings and structures completed in 1684", "Ch\\u00e2teaux in France", "French formal gardens", "Gardens in Yvelines", "Landscape design history of France", "Palaces in France", "French Parliament", "Reportedly haunted locations in France", "Royal residences in France", "Seats of national legislatures", "World Heritage Sites in France", "Ch\\u00e2teaux in Yvelines", "Tourist attractions in Yvelines", "Museums in Yvelines", "1684 establishments in France", "Venues of the 2024 Summer Olympics", "Olympic equestrian venues", "Olympic modern pentathlon venues"]')
    result_3 = page_category_db.query(
        """SELECT * FROM `categories` WHERE `wikilink` = 'Pizza';"""
    )
    assert len(result_3) == 0
    result_4 = page_category_db.query(
        """SELECT * FROM `categories` WHERE `wikilink` = 'Heavy_metal_(disambiguation)';"""
    )
    assert len(result_4) == 0


def test_infobox_category(infobox_category):
    assert len(infobox_category) == 17
    assert infobox_category[0] == 'Germany	["country"]\n'
    assert infobox_category[1] == 'German_Empire	["former country"]\n'
    assert infobox_category[2] == 'Palace_of_Versailles	["historic building"]\n'
    assert infobox_category[3] == 'Heavy_metal_music	["music genre"]\n'
    assert infobox_category[4] == 'Iron_Maiden	["musical artist"]\n'
    assert infobox_category[5] == 'Steve_Harris_(musician)	["musical artist"]\n'
    assert infobox_category[6] == 'Fear_of_the_Dark_(song)	["song"]\n'
    assert infobox_category[7] == 'Afraid_to_Shoot_Strangers	["song"]\n'
    assert infobox_category[8] == 'Power_metal	["music genre"]\n'
    assert infobox_category[9] == 'Nightwish	["musical artist"]\n'
    assert infobox_category[10] == 'Metal:_A_Headbanger\'s_Journey	["film"]\n'
    assert infobox_category[11] == 'Metal_Evolution	["television"]\n'
    assert infobox_category[12] == 'Deathgasm	["film"]\n'
    assert infobox_category[13] == 'Arachnophobia_(film)	["film", "album"]\n'
    assert infobox_category[14] == 'Coraline	["book"]\n'
    assert infobox_category[15] == 'And_Then_There_Were_None	["book"]\n'
    assert infobox_category[16] == 'Real_Humans	["television"]\n'


if __name__ == "__main__":
    pytest.main(sys.argv)
