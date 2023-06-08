import pytest
from recognizer import *


BAUMERT = False


@pytest.fixture
def wordsfile_1():
    with open('/input/wordsfile_test_1_0.txt', 'r', encoding='UTF-8') as this_file:
        wordsfile_content = this_file.readlines()
    return wordsfile_content
   

@pytest.fixture
def docsfile_1():
    with open('/input/docsfile_test_1_0.txt', 'r', encoding='UTF-8') as this_file:
        docsfile_content = this_file.readlines()
    return docsfile_content


@pytest.fixture
def wordsfile_2():
    with open('/input/wordsfile_test_2_0.txt', 'r', encoding='UTF-8') as this_file:
        wordsfile_content = this_file.readlines()
    return wordsfile_content
   

@pytest.fixture
def docsfile_2():
    with open('/input/docsfile_test_2_0.txt', 'r', encoding='UTF-8') as this_file:
        docsfile_content = this_file.readlines()
    return docsfile_content


@pytest.fixture
def wordsfile_3():
    with open('/input/wordsfile_test_3_0.txt', 'r', encoding='UTF-8') as this_file:
        wordsfile_content = this_file.readlines()
    return wordsfile_content
   

@pytest.fixture
def docsfile_3():
    with open('/input/docsfile_test_3_0.txt', 'r', encoding='UTF-8') as this_file:
        docsfile_content = this_file.readlines()
    return docsfile_content


@pytest.fixture
def wordsfile_4():
    with open('/input/wordsfile_test_4_0.txt', 'r', encoding='UTF-8') as this_file:
        wordsfile_content = this_file.readlines()
    return wordsfile_content
   

@pytest.fixture
def docsfile_4():
    with open('/input/docsfile_test_4_0.txt', 'r', encoding='UTF-8') as this_file:
        docsfile_content = this_file.readlines()
    return docsfile_content

@pytest.fixture
def wordsfile_5():
    with open('/input/wordsfile_test_5_0.txt', 'r', encoding='UTF-8') as this_file:
        wordsfile_content = this_file.readlines()
    return wordsfile_content
   

@pytest.fixture
def docsfile_5():
    with open('/input/docsfile_test_5_0.txt', 'r', encoding='UTF-8') as this_file:
        docsfile_content = this_file.readlines()
    return docsfile_content


def test_docsfile(docsfile_1, docsfile_2, docsfile_3, docsfile_4, docsfile_5):
    assert len(docsfile_1) == 166
    assert docsfile_1[0] == '1	Ratio of how much light is reflected back from a body.\n'
    assert docsfile_1[1] == '2	The percentage of diffusely reflected sunlight relative to various surface conditions Albedo (; ) is the measure of the diffuse reflection of solar radiation out of the total solar radiation and measured on a scale from 0, corresponding to a black body that absorbs all incident radiation, to 1, corresponding to a body that reflects all incident radiation.\n'
    assert docsfile_1[32] == '33	Asterix comics usually start with the following introduction:  The year is 50 BC.\n'
    assert docsfile_1[33] == '34	Gaul is entirely occupied by the Romans.\n'
    assert docsfile_1[34] == '35	Well, not entirely...\n'
    assert docsfile_1[35] == '36	One small village of indomitable Gauls still holds out against the invaders.\n'
    assert docsfile_1[73] == '74	There are frozen pizzas with raw ingredients and self-rising crusts.\n'
    assert docsfile_1[145] == '146	Frei means \\"free\\", and Burg, like the modern English word \\"borough\\", was used in those days for an incorporated city or town, usually one with some degree of autonomy.\n'
    assert docsfile_1[165] == '166	It is said that if one accidentally falls or steps into a Bächle, they will marry a Freiburger, or \'Bobbele\'.\n'
    # Both files should be the same
    assert len(docsfile_1) == len(docsfile_2) == len(docsfile_3) == len(docsfile_4) == len(docsfile_5)
    for i in range(len(docsfile_1)):
        assert docsfile_1[i] == docsfile_2[i] == docsfile_3[i] == docsfile_4[i] == docsfile_5[i]


# Note: The scoring factors for the tests were chosen arbitrarily to showcase a variety of possibilies
# Scoring factors: (1.5, 1.5, 1.5, 2.5) including adjectives
def test_wordsfile_1(wordsfile_1):
    assert len(wordsfile_1) == 5885
    assert wordsfile_1[0] == 'Ratio	0	1	1	1\n'
    assert wordsfile_1[1] == '<Ratio>	1	1	0.8187702265372169	0.8187702265372169\n'
    assert wordsfile_1[15] == 'The	0	2	1	1\n'
    assert wordsfile_1[16] == 'percentage	0	2	1	1\n'
    assert wordsfile_1[17] == '<Percentage>	1	2	0.8340807174887892	0.8340807174887892\n'
    assert wordsfile_1[18] == 'of	0	2	1	1\n'
    assert wordsfile_1[19] == 'diffusely	0	2	1	1\n'
    assert wordsfile_1[20] == '<Diffuse_reflection>	1	2	1.0	None\n'
    assert wordsfile_1[21] == 'reflected	0	2	1	1\n'
    assert wordsfile_1[22] == '<Diffuse_reflection>	1	2	1.0	None\n'
    assert wordsfile_1[23] == 'sunlight	0	2	1	1\n'
    assert wordsfile_1[24] == '<Sunlight>	1	2	1.0	None\n'
    assert wordsfile_1[983] == 'fight	0	25	1	1\n'
    assert wordsfile_1[984] == 'the	0	25	1	1\n'
    assert wordsfile_1[985] == 'Roman	0	25	1	1\n'
    assert wordsfile_1[986] == '<Roman_Republic>	1	25	1.0	None\n'
    assert wordsfile_1[987] == 'Republic	0	25	1	1\n'
    assert wordsfile_1[988] == '<Roman_Republic>	1	25	1.0	None\n'
    assert wordsfile_1[989] == 'with	0	25	1	1\n'
    assert wordsfile_1[990] == 'the	0	25	1	1\n'
    assert wordsfile_1[991] == 'aid	0	25	1	1\n'
    assert wordsfile_1[992] == '<Aid>	1	25	0.5528169014084507	0.5528169014084507\n'
    assert wordsfile_1[993] == 'of	0	25	1	1\n'
    assert wordsfile_1[994] == 'a	0	25	1	1\n'
    assert wordsfile_1[995] == 'magic	0	25	1	1\n'
    assert wordsfile_1[996] == '<Potion>	1	25	0.4444444444444444	1.1111111111111112\n'
    assert wordsfile_1[997] == 'potion	0	25	1	1\n'
    assert wordsfile_1[998] == '<Potion>	1	25	0.4444444444444444	1.1111111111111112\n'
    assert wordsfile_1[3428] == 'King	0	99	1	1\n'
    assert wordsfile_1[3429] == '<Latinus>	1	99	1.0	1.6071428571428572\n'
    assert wordsfile_1[3430] == 'Latinus	0	99	1	1\n'
    assert wordsfile_1[3431] == '<Latinus>	1	99	1.0	1.6071428571428572\n'
    assert wordsfile_1[3432] == 'agreed	0	99	1	1\n'
    assert wordsfile_1[3433] == 'that	0	99	1	1\n'
    assert wordsfile_1[3434] == 'Lavinia	0	99	1	1\n'
    assert wordsfile_1[3435] == '<Lavinia>	1	99	0.5416666666666666	1.421875\n'
    assert wordsfile_1[3436] == 'marry	0	99	1	1\n'
    assert wordsfile_1[3437] == 'Aeneas	0	99	1	1\n'
    assert wordsfile_1[3438] == '<Aeneas>	1	99	0.9737670514165793	2.1909758656873035\n'
    assert wordsfile_1[4246] == 'A.U.C.	0	124	1	1\n'
    assert wordsfile_1[4247] == '<Ab_urbe_condita>	1	124	0.17412935323383086	0.4664179104477612\n'
    assert wordsfile_1[4248] == 'or	0	124	1	1\n'
    assert wordsfile_1[4249] == 'Ab	0	124	1	1\n'
    assert wordsfile_1[4250] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_1[4251] == 'Urbe	0	124	1	1\n'
    assert wordsfile_1[4252] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_1[4253] == 'Condita	0	124	1	1\n'
    assert wordsfile_1[4254] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_1[5866] == 'if	0	166	1	1\n'
    assert wordsfile_1[5867] == 'one	0	166	1	1\n'
    assert wordsfile_1[5868] == 'accidentally	0	166	1	1\n'
    assert wordsfile_1[5869] == 'falls	0	166	1	1\n'
    assert wordsfile_1[5870] == 'or	0	166	1	1\n'
    # The following example shows an error my SpaCy where the verb "steps" was misclassified as a noun
    assert wordsfile_1[5871] == 'steps	0	166	1	1\n'
    assert wordsfile_1[5872] == '<Steps_(pop_group)>	1	166	0.8714810281517748	0.8714810281517748\n'
    assert wordsfile_1[5873] == 'into	0	166	1	1\n'
    assert wordsfile_1[5874] == 'a	0	166	1	1\n'
    assert wordsfile_1[5875] == 'Bächle	0	166	1	1\n'
    assert wordsfile_1[5876] == '<Freiburg_Bächle>	1	166	1.0	3.75\n'
    assert wordsfile_1[5877] == 'they	0	166	1	1\n'
    assert wordsfile_1[5878] == 'will	0	166	1	1\n'
    assert wordsfile_1[5879] == 'marry	0	166	1	1\n'
    assert wordsfile_1[5880] == 'a	0	166	1	1\n'
    assert wordsfile_1[5881] == 'Freiburger	0	166	1	1\n'
    assert wordsfile_1[5882] == '<Freiburg_im_Breisgau>	1	166	0.5	1.875\n'
    assert wordsfile_1[5883] == 'or	0	166	1	1\n'
    assert wordsfile_1[5884] == 'Bobbele	0	166	1	1\n'


# Scoring factors: (1.0, 1.0, 1.0, 4.0) including adjectives
def test_wordsfile_2(wordsfile_2):
    assert len(wordsfile_2) == 5883
    assert wordsfile_2[0] == 'Ratio	0	1	1	1\n'
    assert wordsfile_2[1] == '<Ratio>	1	1	0.8187702265372169	0.8187702265372169\n'
    assert wordsfile_2[15] == 'The	0	2	1	1\n'
    assert wordsfile_2[16] == 'percentage	0	2	1	1\n'
    assert wordsfile_2[17] == '<Percentage>	1	2	0.8340807174887892	0.8340807174887892\n'
    assert wordsfile_2[18] == 'of	0	2	1	1\n'
    assert wordsfile_2[19] == 'diffusely	0	2	1	1\n'
    assert wordsfile_2[20] == '<Diffuse_reflection>	1	2	1.0	None\n'
    assert wordsfile_2[21] == 'reflected	0	2	1	1\n'
    assert wordsfile_2[22] == '<Diffuse_reflection>	1	2	1.0	None\n'
    assert wordsfile_2[23] == 'sunlight	0	2	1	1\n'
    assert wordsfile_2[24] == '<Sunlight>	1	2	1.0	None\n'
    assert wordsfile_2[983] == 'fight	0	25	1	1\n'
    assert wordsfile_2[984] == 'the	0	25	1	1\n'
    assert wordsfile_2[985] == 'Roman	0	25	1	1\n'
    assert wordsfile_2[986] == '<Roman_Republic>	1	25	1.0	None\n'
    assert wordsfile_2[987] == 'Republic	0	25	1	1\n'
    assert wordsfile_2[988] == '<Roman_Republic>	1	25	1.0	None\n'
    assert wordsfile_2[989] == 'with	0	25	1	1\n'
    assert wordsfile_2[990] == 'the	0	25	1	1\n'
    assert wordsfile_2[991] == 'aid	0	25	1	1\n'
    assert wordsfile_2[992] == '<Aid>	1	25	0.5528169014084507	0.5528169014084507\n'
    assert wordsfile_2[993] == 'of	0	25	1	1\n'
    assert wordsfile_2[994] == 'a	0	25	1	1\n'
    assert wordsfile_2[995] == 'magic	0	25	1	1\n'
    assert wordsfile_2[996] == '<Potion>	1	25	0.4444444444444444	1.7777777777777777\n'
    assert wordsfile_2[997] == 'potion	0	25	1	1\n'
    assert wordsfile_2[998] == '<Potion>	1	25	0.4444444444444444	1.7777777777777777\n'
    assert wordsfile_2[3427] == 'King	0	99	1	1\n'
    assert wordsfile_2[3428] == '<Latinus>	1	99	1.0	1.0\n'
    assert wordsfile_2[3429] == 'Latinus	0	99	1	1\n'
    assert wordsfile_2[3430] == '<Latinus>	1	99	1.0	1.0\n'
    assert wordsfile_2[3431] == 'agreed	0	99	1	1\n'
    assert wordsfile_2[3432] == 'that	0	99	1	1\n'
    assert wordsfile_2[3433] == 'Lavinia	0	99	1	1\n'
    assert wordsfile_2[3434] == '<Lavinia>	1	99	0.5416666666666666	0.5416666666666666\n'
    assert wordsfile_2[3435] == 'marry	0	99	1	1\n'
    assert wordsfile_2[3436] == 'Aeneas	0	99	1	1\n'
    assert wordsfile_2[3437] == '<Aeneas>	1	99	0.9737670514165793	0.9737670514165793\n'
    # For the tests with other scoring factors, not only the score is different,
    # but also the assigned entity
    assert wordsfile_2[4244] == 'A.U.C.	0	124	1	1\n'
    assert wordsfile_2[4245] == '<Ab_urbe_condita>	1	124	0.17412935323383086	0.6965174129353234\n'
    assert wordsfile_2[4246] == 'or	0	124	1	1\n'
    assert wordsfile_2[4247] == 'Ab	0	124	1	1\n'
    assert wordsfile_2[4248] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_2[4249] == 'Urbe	0	124	1	1\n'
    assert wordsfile_2[4250] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_2[4251] == 'Condita	0	124	1	1\n'
    assert wordsfile_2[4252] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_2[5864] == 'if	0	166	1	1\n'
    assert wordsfile_2[5865] == 'one	0	166	1	1\n'
    assert wordsfile_2[5866] == 'accidentally	0	166	1	1\n'
    assert wordsfile_2[5867] == 'falls	0	166	1	1\n'
    assert wordsfile_2[5868] == 'or	0	166	1	1\n'
    # The following example shows an error my SpaCy where the verb "steps" was misclassified as a noun
    assert wordsfile_2[5869] == 'steps	0	166	1	1\n'
    assert wordsfile_2[5870] == '<Steps_(pop_group)>	1	166	0.8714810281517748	0.8714810281517748\n'
    assert wordsfile_2[5871] == 'into	0	166	1	1\n'
    assert wordsfile_2[5872] == 'a	0	166	1	1\n'
    assert wordsfile_2[5873] == 'Bächle	0	166	1	1\n'
    assert wordsfile_2[5874] == '<Freiburg_Bächle>	1	166	1.0	4.0\n'
    assert wordsfile_2[5875] == 'they	0	166	1	1\n'
    assert wordsfile_2[5876] == 'will	0	166	1	1\n'
    assert wordsfile_2[5877] == 'marry	0	166	1	1\n'
    assert wordsfile_2[5878] == 'a	0	166	1	1\n'
    assert wordsfile_2[5879] == 'Freiburger	0	166	1	1\n'
    assert wordsfile_2[5880] == '<Freiburg_im_Breisgau>	1	166	0.5	2.0\n'
    assert wordsfile_2[5881] == 'or	0	166	1	1\n'
    assert wordsfile_2[5882] == 'Bobbele	0	166	1	1\n'


# Scoring factors: (0.0, 0.0, 0.0, 0.0) including adjectives
def test_wordsfile_3(wordsfile_3):
    assert len(wordsfile_3) == 5881
    assert wordsfile_3[0] == 'Ratio	0	1	1	1\n'
    assert wordsfile_3[1] == '<Ratio>	1	1	0.8187702265372169	0.8187702265372169\n'
    assert wordsfile_3[15] == 'The	0	2	1	1\n'
    assert wordsfile_3[16] == 'percentage	0	2	1	1\n'
    assert wordsfile_3[17] == '<Percentage>	1	2	0.8340807174887892	0.8340807174887892\n'
    assert wordsfile_3[18] == 'of	0	2	1	1\n'
    assert wordsfile_3[19] == 'diffusely	0	2	1	1\n'
    assert wordsfile_3[20] == '<Diffuse_reflection>	1	2	1.0	None\n'
    assert wordsfile_3[21] == 'reflected	0	2	1	1\n'
    assert wordsfile_3[22] == '<Diffuse_reflection>	1	2	1.0	None\n'
    assert wordsfile_3[23] == 'sunlight	0	2	1	1\n'
    assert wordsfile_3[24] == '<Sunlight>	1	2	1.0	None\n'
    assert wordsfile_3[982] == 'fight	0	25	1	1\n'
    assert wordsfile_3[983] == 'the	0	25	1	1\n'
    assert wordsfile_3[984] == 'Roman	0	25	1	1\n'
    assert wordsfile_3[985] == '<Roman_Republic>	1	25	1.0	None\n'
    assert wordsfile_3[986] == 'Republic	0	25	1	1\n'
    assert wordsfile_3[987] == '<Roman_Republic>	1	25	1.0	None\n'
    assert wordsfile_3[988] == 'with	0	25	1	1\n'
    assert wordsfile_3[989] == 'the	0	25	1	1\n'
    assert wordsfile_3[990] == 'aid	0	25	1	1\n'
    assert wordsfile_3[991] == '<Aid>	1	25	0.5528169014084507	0.5528169014084507\n'
    assert wordsfile_3[992] == 'of	0	25	1	1\n'
    assert wordsfile_3[993] == 'a	0	25	1	1\n'
    assert wordsfile_3[994] == 'magic	0	25	1	1\n'
    assert wordsfile_3[995] == '<Magic_Potion_(album)>	1	25	0.5	0.5\n'
    assert wordsfile_3[996] == 'potion	0	25	1	1\n'
    assert wordsfile_3[997] == '<Magic_Potion_(album)>	1	25	0.5	0.5\n'
    assert wordsfile_3[3426] == 'King	0	99	1	1\n'
    assert wordsfile_3[3427] == '<Latinus>	1	99	1.0	1.0\n'
    assert wordsfile_3[3428] == 'Latinus	0	99	1	1\n'
    assert wordsfile_3[3429] == '<Latinus>	1	99	1.0	1.0\n'
    assert wordsfile_3[3430] == 'agreed	0	99	1	1\n'
    assert wordsfile_3[3431] == 'that	0	99	1	1\n'
    assert wordsfile_3[3432] == 'Lavinia	0	99	1	1\n'
    assert wordsfile_3[3433] == '<Lavinia>	1	99	0.5416666666666666	0.5416666666666666\n'
    assert wordsfile_3[3434] == 'marry	0	99	1	1\n'
    assert wordsfile_3[3435] == 'Aeneas	0	99	1	1\n'
    assert wordsfile_3[3436] == '<Aeneas>	1	99	0.9737670514165793	0.9737670514165793\n'
    # For the tests with other scoring factors, not only the score is different,
    # but also the assigned entity
    assert wordsfile_3[4243] == 'A.U.C.	0	124	1	1\n'
    assert wordsfile_3[4244] == '<United_Self-Defense_Forces_of_Colombia>	1	124	0.43781094527363185	0.43781094527363185\n'
    assert wordsfile_3[4245] == 'or	0	124	1	1\n'
    assert wordsfile_3[4246] == 'Ab	0	124	1	1\n'
    assert wordsfile_3[4247] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_3[4248] == 'Urbe	0	124	1	1\n'
    assert wordsfile_3[4249] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_3[4250] == 'Condita	0	124	1	1\n'
    assert wordsfile_3[4251] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_3[5862] == 'if	0	166	1	1\n'
    assert wordsfile_3[5863] == 'one	0	166	1	1\n'
    assert wordsfile_3[5864] == 'accidentally	0	166	1	1\n'
    assert wordsfile_3[5865] == 'falls	0	166	1	1\n'
    assert wordsfile_3[5866] == 'or	0	166	1	1\n'
    # The following example shows an error my SpaCy where the verb "steps" was misclassified as a noun
    assert wordsfile_3[5867] == 'steps	0	166	1	1\n'
    assert wordsfile_3[5868] == '<Steps_(pop_group)>	1	166	0.8714810281517748	0.8714810281517748\n'
    assert wordsfile_3[5869] == 'into	0	166	1	1\n'
    assert wordsfile_3[5870] == 'a	0	166	1	1\n'
    assert wordsfile_3[5871] == 'Bächle	0	166	1	1\n'
    assert wordsfile_3[5872] == '<Freiburg_Bächle>	1	166	1.0	1.0\n'
    assert wordsfile_3[5873] == 'they	0	166	1	1\n'
    assert wordsfile_3[5874] == 'will	0	166	1	1\n'
    assert wordsfile_3[5875] == 'marry	0	166	1	1\n'
    assert wordsfile_3[5876] == 'a	0	166	1	1\n'
    assert wordsfile_3[5877] == 'Freiburger	0	166	1	1\n'
    assert wordsfile_3[5878] == '<Freiburg_im_Breisgau>	1	166	0.5	0.5\n'
    assert wordsfile_3[5879] == 'or	0	166	1	1\n'
    assert wordsfile_3[5880] == 'Bobbele	0	166	1	1\n'


# Scoring factors: (1.5, 1.5, 1.5, 2.5) not including adjectives
def test_wordsfile_4(wordsfile_4):
    assert len(wordsfile_4) == 5616
    assert wordsfile_4[0] == 'Ratio	0	1	1	1\n'
    assert wordsfile_4[1] == '<Ratio>	1	1	0.8187702265372169	0.8187702265372169\n'
    assert wordsfile_4[14] == 'The	0	2	1	1\n'
    assert wordsfile_4[15] == 'percentage	0	2	1	1\n'
    assert wordsfile_4[16] == '<Percentage>	1	2	0.8340807174887892	0.8340807174887892\n'
    assert wordsfile_4[17] == 'of	0	2	1	1\n'
    assert wordsfile_4[18] == 'diffusely	0	2	1	1\n'
    assert wordsfile_4[19] == '<Diffuse_reflection>	1	2	1.0	None\n'
    assert wordsfile_4[20] == 'reflected	0	2	1	1\n'
    assert wordsfile_4[21] == '<Diffuse_reflection>	1	2	1.0	None\n'
    assert wordsfile_4[22] == 'sunlight	0	2	1	1\n'
    assert wordsfile_4[23] == '<Sunlight>	1	2	1.0	None\n'
    assert wordsfile_4[921] == 'fight	0	25	1	1\n'
    assert wordsfile_4[922] == 'the	0	25	1	1\n'
    assert wordsfile_4[923] == 'Roman	0	25	1	1\n'
    assert wordsfile_4[924] == '<Roman_Republic>	1	25	1.0	None\n'
    assert wordsfile_4[925] == 'Republic	0	25	1	1\n'
    assert wordsfile_4[926] == '<Roman_Republic>	1	25	1.0	None\n'
    assert wordsfile_4[927] == 'with	0	25	1	1\n'
    assert wordsfile_4[928] == 'the	0	25	1	1\n'
    assert wordsfile_4[929] == 'aid	0	25	1	1\n'
    assert wordsfile_4[930] == '<Aid>	1	25	0.5528169014084507	0.5528169014084507\n'
    assert wordsfile_4[931] == 'of	0	25	1	1\n'
    assert wordsfile_4[932] == 'a	0	25	1	1\n'
    assert wordsfile_4[933] == 'magic	0	25	1	1\n'
    assert wordsfile_4[934] == 'potion	0	25	1	1\n'
    assert wordsfile_4[935] == '<Potion>	1	25	0.9634146341463414	2.4085365853658534\n'
    assert wordsfile_4[3252] == 'King	0	99	1	1\n'
    assert wordsfile_4[3253] == '<Latinus>	1	99	1.0	1.6071428571428572\n'
    assert wordsfile_4[3254] == 'Latinus	0	99	1	1\n'
    assert wordsfile_4[3255] == '<Latinus>	1	99	1.0	1.6071428571428572\n'
    assert wordsfile_4[3256] == 'agreed	0	99	1	1\n'
    assert wordsfile_4[3257] == 'that	0	99	1	1\n'
    assert wordsfile_4[3258] == 'Lavinia	0	99	1	1\n'
    assert wordsfile_4[3259] == '<Lavinia>	1	99	0.5416666666666666	1.421875\n'
    assert wordsfile_4[3260] == 'marry	0	99	1	1\n'
    assert wordsfile_4[3261] == 'Aeneas	0	99	1	1\n'
    assert wordsfile_4[3262] == '<Aeneas>	1	99	0.9737670514165793	2.1909758656873035\n'
    # For the tests with other scoring factors, not only the score is different,
    # but also the assigned entity
    assert wordsfile_4[4049] == 'A.U.C.	0	124	1	1\n'
    assert wordsfile_4[4050] == '<Ab_urbe_condita>	1	124	0.17412935323383086	0.4664179104477612\n'
    assert wordsfile_4[4051] == 'or	0	124	1	1\n'
    assert wordsfile_4[4052] == 'Ab	0	124	1	1\n'
    assert wordsfile_4[4053] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_4[4054] == 'Urbe	0	124	1	1\n'
    assert wordsfile_4[4055] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_4[4056] == 'Condita	0	124	1	1\n'
    assert wordsfile_4[4057] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_4[5597] == 'if	0	166	1	1\n'
    assert wordsfile_4[5598] == 'one	0	166	1	1\n'
    assert wordsfile_4[5599] == 'accidentally	0	166	1	1\n'
    assert wordsfile_4[5600] == 'falls	0	166	1	1\n'
    assert wordsfile_4[5601] == 'or	0	166	1	1\n'
    # The following example shows an error my SpaCy where the verb "steps" was misclassified as a noun
    assert wordsfile_4[5602] == 'steps	0	166	1	1\n'
    assert wordsfile_4[5603] == '<Steps_(pop_group)>	1	166	0.8714810281517748	0.8714810281517748\n'
    assert wordsfile_4[5604] == 'into	0	166	1	1\n'
    assert wordsfile_4[5605] == 'a	0	166	1	1\n'
    assert wordsfile_4[5606] == 'Bächle	0	166	1	1\n'
    assert wordsfile_4[5607] == '<Freiburg_Bächle>	1	166	1.0	3.75\n'
    assert wordsfile_4[5608] == 'they	0	166	1	1\n'
    assert wordsfile_4[5609] == 'will	0	166	1	1\n'
    assert wordsfile_4[5610] == 'marry	0	166	1	1\n'
    assert wordsfile_4[5611] == 'a	0	166	1	1\n'
    assert wordsfile_4[5612] == 'Freiburger	0	166	1	1\n'
    assert wordsfile_4[5613] == '<Freiburg_im_Breisgau>	1	166	0.5	1.875\n'
    assert wordsfile_4[5614] == 'or	0	166	1	1\n'
    assert wordsfile_4[5615] == 'Bobbele	0	166	1	1\n'


# Scoring factors: (1.5, 1.5, 1.5, 4) not including adjectives
def test_wordsfile_5(wordsfile_5):
    assert len(wordsfile_5) == 5616
    assert wordsfile_5[0] == 'Ratio	0	1	1	1\n'
    assert wordsfile_5[1] == '<Ratio>	1	1	0.8187702265372169	0.8187702265372169\n'
    assert wordsfile_5[14] == 'The	0	2	1	1\n'
    assert wordsfile_5[15] == 'percentage	0	2	1	1\n'
    assert wordsfile_5[16] == '<Percentage>	1	2	0.8340807174887892	0.8340807174887892\n'
    assert wordsfile_5[17] == 'of	0	2	1	1\n'
    assert wordsfile_5[18] == 'diffusely	0	2	1	1\n'
    assert wordsfile_5[19] == '<Diffuse_reflection>	1	2	1.0	None\n'
    assert wordsfile_5[20] == 'reflected	0	2	1	1\n'
    assert wordsfile_5[21] == '<Diffuse_reflection>	1	2	1.0	None\n'
    assert wordsfile_5[22] == 'sunlight	0	2	1	1\n'
    assert wordsfile_5[23] == '<Sunlight>	1	2	1.0	None\n'
    assert wordsfile_5[921] == 'fight	0	25	1	1\n'
    assert wordsfile_5[922] == 'the	0	25	1	1\n'
    assert wordsfile_5[923] == 'Roman	0	25	1	1\n'
    assert wordsfile_5[924] == '<Roman_Republic>	1	25	1.0	None\n'
    assert wordsfile_5[925] == 'Republic	0	25	1	1\n'
    assert wordsfile_5[926] == '<Roman_Republic>	1	25	1.0	None\n'
    assert wordsfile_5[927] == 'with	0	25	1	1\n'
    assert wordsfile_5[928] == 'the	0	25	1	1\n'
    assert wordsfile_5[929] == 'aid	0	25	1	1\n'
    assert wordsfile_5[930] == '<Aid>	1	25	0.5528169014084507	0.5528169014084507\n'
    assert wordsfile_5[931] == 'of	0	25	1	1\n'
    assert wordsfile_5[932] == 'a	0	25	1	1\n'
    assert wordsfile_5[933] == 'magic	0	25	1	1\n'
    assert wordsfile_5[934] == 'potion	0	25	1	1\n'
    assert wordsfile_5[935] == '<Potion>	1	25	0.9634146341463414	3.8536585365853657\n'
    assert wordsfile_5[3252] == 'King	0	99	1	1\n'
    assert wordsfile_5[3253] == '<Latinus>	1	99	1.0	1.6071428571428572\n'
    assert wordsfile_5[3254] == 'Latinus	0	99	1	1\n'
    assert wordsfile_5[3255] == '<Latinus>	1	99	1.0	1.6071428571428572\n'
    assert wordsfile_5[3256] == 'agreed	0	99	1	1\n'
    assert wordsfile_5[3257] == 'that	0	99	1	1\n'
    assert wordsfile_5[3258] == 'Lavinia	0	99	1	1\n'
    assert wordsfile_5[3259] == '<Lavinia>	1	99	0.5416666666666666	1.421875\n'
    assert wordsfile_5[3260] == 'marry	0	99	1	1\n'
    assert wordsfile_5[3261] == 'Aeneas	0	99	1	1\n'
    assert wordsfile_5[3262] == '<Aeneas>	1	99	0.9737670514165793	2.1909758656873035\n'
    # For the tests with other scoring factors, not only the score is different,
    # but also the assigned entity
    assert wordsfile_5[4049] == 'A.U.C.	0	124	1	1\n'
    assert wordsfile_5[4050] == '<Ab_urbe_condita>	1	124	0.17412935323383086	0.746268656716418\n'
    assert wordsfile_5[4051] == 'or	0	124	1	1\n'
    assert wordsfile_5[4052] == 'Ab	0	124	1	1\n'
    assert wordsfile_5[4053] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_5[4054] == 'Urbe	0	124	1	1\n'
    assert wordsfile_5[4055] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_5[4056] == 'Condita	0	124	1	1\n'
    assert wordsfile_5[4057] == '<Ab_urbe_condita>	1	124	1.0	None\n'
    assert wordsfile_5[5597] == 'if	0	166	1	1\n'
    assert wordsfile_5[5598] == 'one	0	166	1	1\n'
    assert wordsfile_5[5599] == 'accidentally	0	166	1	1\n'
    assert wordsfile_5[5600] == 'falls	0	166	1	1\n'
    assert wordsfile_5[5601] == 'or	0	166	1	1\n'
    # The following example shows an error my SpaCy where the verb "steps" was misclassified as a noun
    assert wordsfile_5[5602] == 'steps	0	166	1	1\n'
    assert wordsfile_5[5603] == '<Steps_(pop_group)>	1	166	0.8714810281517748	0.8714810281517748\n'
    assert wordsfile_5[5604] == 'into	0	166	1	1\n'
    assert wordsfile_5[5605] == 'a	0	166	1	1\n'
    assert wordsfile_5[5606] == 'Bächle	0	166	1	1\n'
    assert wordsfile_5[5607] == '<Freiburg_Bächle>	1	166	1.0	6.0\n'
    assert wordsfile_5[5608] == 'they	0	166	1	1\n'
    assert wordsfile_5[5609] == 'will	0	166	1	1\n'
    assert wordsfile_5[5610] == 'marry	0	166	1	1\n'
    assert wordsfile_5[5611] == 'a	0	166	1	1\n'
    assert wordsfile_5[5612] == 'Freiburger	0	166	1	1\n'
    assert wordsfile_5[5613] == '<Freiburg_im_Breisgau>	1	166	0.5	3.0\n'
    assert wordsfile_5[5614] == 'or	0	166	1	1\n'
    assert wordsfile_5[5615] == 'Bobbele	0	166	1	1\n'


def test_find_filter_links():
    s = """Preparation
Pizza is sold fresh or [[Frozen food|frozen]], and whole or in [[pizza by the slice|portion-size slices]]. Methods have been developed to overcome challenges such as preventing the sauce from combining with the dough, and producing a crust that can be frozen and reheated without becoming rigid. There are frozen pizzas with raw ingredients and self-rising crusts.

Another form of pizza is available from [[take and bake pizzeria]]s. This pizza is assembled in the store, then sold unbaked to customers to bake in their own [[Conventional ovens|ovens]]. Some grocery stores sell fresh dough along with sauce and basic ingredients, to assemble at home before baking in an oven.

Baking
In restaurants, pizza can be baked in an oven with fire bricks above the heat source, an electric deck oven, a [[conveyor belt]] oven, or, in traditional style in a wood or coal-fired [[masonry oven|brick oven]]. The pizza is slid into the oven on a long paddle, called a [[peel (tool)|peel]], and baked directly on hot bricks, a screen (a round metal grate, typically aluminum), or whatever the oven surface is. Before use, a peel is typically  sprinkled with cornmeal to allow the pizza to easily slide on and off it. When made at home, a pizza can be baked on a [[pizza stone]] in a regular oven to reproduce some of the heating effect of a brick oven. Cooking directly on a metal surface results in too rapid heat transfer to the crust, burning it. Some home chefs use a wood-fired pizza oven, usually installed outdoors. As in restaurants, these are often dome-shaped, as pizza ovens have been for centuries, in order to achieve even heat distribution. Another variation is grilled pizza, in which the pizza is baked directly on a barbecue grill. [[Greek pizza]], like [[deep dish pizza|deep dish]] [[Chicago-style pizza|Chicago]] and [[Sicilian pizza|Sicilian]] style pizza, is baked in a pan rather than directly on the bricks of the pizza oven.

[[Category:Pizza| ]]
[[Category:Argentine cuisine]]
[[Category:Cheese dishes]]
[[Category:Flatbread dishes]]
[[Category:Italian cuisine]]
[[Category:Italian inventions]]
[[Category:Italian-American cuisine]]
[[Category:Mediterranean cuisine]]
[[Category:Popular culture]]
[[Category:World cuisine]]
[[Category:Snack foods]]
[[Category:Types of food]]
[[Category:Convenience foods]]
[[Category:National dishes]]
[[Category:Food combinations]]
[[Category:Neapolitan cuisine]]
"""
    text, link_dict, category_links = find_filter_links(s)
    assert text == 'Preparation\nPizza is sold fresh or frozen, and whole or in portion-size slices. Methods have been developed to overcome challenges such as preventing the sauce from combining with the dough, and producing a crust that can be frozen and reheated without becoming rigid. There are frozen pizzas with raw ingredients and self-rising crusts.\n\nAnother form of pizza is available from take and bake pizzerias. This pizza is assembled in the store, then sold unbaked to customers to bake in their own ovens. Some grocery stores sell fresh dough along with sauce and basic ingredients, to assemble at home before baking in an oven.\n\nBaking\nIn restaurants, pizza can be baked in an oven with fire bricks above the heat source, an electric deck oven, a conveyor belt oven, or, in traditional style in a wood or coal-fired brick oven. The pizza is slid into the oven on a long paddle, called a peel, and baked directly on hot bricks, a screen (a round metal grate, typically aluminum), or whatever the oven surface is. Before use, a peel is typically  sprinkled with cornmeal to allow the pizza to easily slide on and off it. When made at home, a pizza can be baked on a pizza stone in a regular oven to reproduce some of the heating effect of a brick oven. Cooking directly on a metal surface results in too rapid heat transfer to the crust, burning it. Some home chefs use a wood-fired pizza oven, usually installed outdoors. As in restaurants, these are often dome-shaped, as pizza ovens have been for centuries, in order to achieve even heat distribution. Another variation is grilled pizza, in which the pizza is baked directly on a barbecue grill. Greek pizza, like deep dish Chicago and Sicilian style pizza, is baked in a pan rather than directly on the bricks of the pizza oven.'
    assert link_dict == {35: {'wikilink': 'Frozen food', 'linktext': 'frozen'}, 59: {'wikilink': 'pizza by the slice', 'linktext': 'portion-size slices'}, 379: {'wikilink': 'take and bake pizzeria', 'linktext': 'take and bake pizzeria'}, 494: {'wikilink': 'Conventional ovens', 'linktext': 'ovens'}, 743: {'wikilink': 'conveyor belt', 'linktext': 'conveyor belt'}, 812: {'wikilink': 'masonry oven', 'linktext': 'brick oven'}, 883: {'wikilink': 'peel (tool)', 'linktext': 'peel'}, 1160: {'wikilink': 'pizza stone', 'linktext': 'pizza stone'}, 1643: {'wikilink': 'Greek pizza', 'linktext': 'Greek pizza'}, 1661: {'wikilink': 'deep dish pizza', 'linktext': 'deep dish'}, 1671: {'wikilink': 'Chicago-style pizza', 'linktext': 'Chicago'}, 1683: {'wikilink': 'Sicilian pizza', 'linktext': 'Sicilian'}}
    assert category_links == [{'wikilink': 'Category:Pizza', 'linktext': ' '}, {'wikilink': 'Category:Argentine cuisine', 'linktext': 'Category:Argentine cuisine'}, {'wikilink': 'Category:Cheese dishes', 'linktext': 'Category:Cheese dishes'}, {'wikilink': 'Category:Flatbread dishes', 'linktext': 'Category:Flatbread dishes'}, {'wikilink': 'Category:Italian cuisine', 'linktext': 'Category:Italian cuisine'}, {'wikilink': 'Category:Italian inventions', 'linktext': 'Category:Italian inventions'}, {'wikilink': 'Category:Italian-American cuisine', 'linktext': 'Category:Italian-American cuisine'}, {'wikilink': 'Category:Mediterranean cuisine', 'linktext': 'Category:Mediterranean cuisine'}, {'wikilink': 'Category:Popular culture', 'linktext': 'Category:Popular culture'}, {'wikilink': 'Category:World cuisine', 'linktext': 'Category:World cuisine'}, {'wikilink': 'Category:Snack foods', 'linktext': 'Category:Snack foods'}, {'wikilink': 'Category:Types of food', 'linktext': 'Category:Types of food'}, {'wikilink': 'Category:Convenience foods', 'linktext': 'Category:Convenience foods'}, {'wikilink': 'Category:National dishes', 'linktext': 'Category:National dishes'}, {'wikilink': 'Category:Food combinations', 'linktext': 'Category:Food combinations'}, {'wikilink': 'Category:Neapolitan cuisine', 'linktext': 'Category:Neapolitan cuisine'}]
    s_2 = ''
    text_2, link_dict_2, category_links_2 = find_filter_links(s_2)
    assert text_2 == ''
    assert link_dict_2 == dict()
    assert category_links_2 == []
    s_3 = """Preparation
Pizza is sold fresh or frozen, and whole or in portion-size slices. Methods have been developed to overcome challenges such as preventing the sauce from combining with the dough, and producing a crust that can be frozen and reheated without becoming rigid. There are frozen pizzas with raw ingredients and self-rising crusts.

Another form of pizza is available from take and bake pizzerias.
    """
    text_3, link_dict_3, category_links_3 = find_filter_links(s_3)
    assert text_3 == 'Preparation\nPizza is sold fresh or frozen, and whole or in portion-size slices. Methods have been developed to overcome challenges such as preventing the sauce from combining with the dough, and producing a crust that can be frozen and reheated without becoming rigid. There are frozen pizzas with raw ingredients and self-rising crusts.\n\nAnother form of pizza is available from take and bake pizzerias.'
    assert link_dict_3 == dict()
    assert category_links_3 == []


def test_load_infobox_category_data():
    infobox_cat_db_1 = dict()
    load_infobox_category_data(infobox_cat_db_1, '/input/infobox_category_test.tsv', cleanup=False)
    assert infobox_cat_db_1 == {'Germany': ['country'], 'German_Empire': ['former country'], 'Palace_of_Versailles': ['historic building'], 'Heavy_metal_music': ['music genre'], 'Iron_Maiden': ['musical artist'], 'Steve_Harris_(musician)': ['musical artist'], 'Fear_of_the_Dark_(song)': ['song'], 'Afraid_to_Shoot_Strangers': ['song'], 'Power_metal': ['music genre'], 'Nightwish': ['musical artist'], "Metal:_A_Headbanger's_Journey": ['film'], 'Metal_Evolution': ['television'], 'Deathgasm': ['film'], 'Arachnophobia_(film)': ['film', 'album'], 'Coraline': ['book'], 'And_Then_There_Were_None': ['book'], 'Real_Humans': ['television']}
    infobox_cat_db_2 = dict()
    load_infobox_category_data(infobox_cat_db_2, '/input/infobox_category_test.tsv', cleanup=True)
    assert infobox_cat_db_2 == {'Germany': ['country'], 'German_Empire': ['former country'], 'Palace_of_Versailles': ['historic building'], 'Heavy_metal_music': ['music genre'], 'Iron_Maiden': ['musical artist'], 'Steve_Harris_(musician)': ['musical artist'], 'Fear_of_the_Dark_(song)': ['song'], 'Afraid_to_Shoot_Strangers': ['song'], 'Power_metal': ['music genre'], 'Nightwish': ['musical artist'], "Metal:_A_Headbanger's_Journey": ['film'], 'Metal_Evolution': ['television'], 'Deathgasm': ['film'], 'Arachnophobia_(film)': ['film', 'album'], 'Coraline': ['book'], 'And_Then_There_Were_None': ['book'], 'Real_Humans': ['television']}


def test_load_gender_data():
    gender_data = dict()
    load_gender_data(gender_data, '/input/gender_data_test.tsv')
    assert gender_data == {'Adeline_Kerrar': 'female', 'Aidan_John_Lindsay-MacDougall': 'male', 'Alberto_Villoldo': 'male', 'Alexander_Haddow': 'male', 'Alfred_Lenel': 'male', 'Al_Satterfield': 'male', 'Andoni_Arrizabalaga': 'male', 'Andrew_R_Coggan': 'male', 'Anna-Greta_Söderlund': 'female', 'Annick_Perrot-Bishop': 'female', 'Antonio_Giuseppe_Carcassona': 'male', 'Arnaldo_Rodrigues_D’Almeida': 'male', 'A_soldier': 'male', 'Badr_Shafi’i': 'male', 'Béla_Horányi': 'male', 'Bernhard_Palme': 'male', 'Blanka_Baderová': 'female', 'Brian_Maracle': 'male', 'Canan_Cetin': 'female', 'Carmelo_Caruana': 'male', 'Cees_Bremmer': 'male', 'Charles_Manfred_Thompson': 'male', 'Chen_Yin': 'male', 'Christie_Williamson': 'male', 'Clarence_George_Scott_Pigou': 'male', 'Cora_van_der_Kooij': 'female', 'Dallas_Abbott': 'female', 'Danny_Pierce': 'male', 'David_L._Callies': 'male', 'Deniz_Gönenç_Sümer': 'male', 'Dionisio_Mazzuoli': 'male', 'Doris_Meister': 'female', 'Eddy_Van_Straelen': 'male', 'Edward_Lewis_Goodwin': 'male', 'Eliav_Varda': 'male', 'Ellen_Brogren': 'female', 'Emma_Greco': 'female', 'Erik_Liljeroth': 'male', 'Eudes_de_La_Roche,_Seigneur_de_Châtillon_et_de_Nolay': 'male', 'Faisal_Qureshi': 'male', 'Fernand_Millaud': 'male', 'Francesco_Roselli': 'male', 'François-Xavier_Vogt': 'male', 'Fred_C._Brown': 'male', 'Fritz_Langheld': 'male', 'Gastón_Otreras': 'male', 'George_Newton': 'male', 'Gérard_Weber': 'male', 'Gino_Mattiello': 'male', 'Gong_Yu': 'male', 'Guillaume_Bouic': 'male', 'Hà_Anh_Tuấn': 'male', 'Hanspeter_Schild': 'male', 'Heather_D_Gibbs': 'female', 'Helen_Thompson': 'female', 'Henryk_Łubieński': 'male', 'He_Zhanao': 'male', 'Huang_Can': 'male', 'Ian_Richard_Baldock': 'male', 'Ingvild_Fossgard_Sandøy': 'female', 'István_Holló': 'male', 'Jaco_Ishulutaq': 'male', 'James_Galea': 'male', 'Jane_Friedman': 'female', 'Jaroslava_Škudrnová': 'female', 'Jean_Laquintinie': 'male', 'Jens_Toller_Rosenheim': 'male', 'Jim_Nance_McCord': 'male', 'Joe_Bailey_Cheaney': 'male', 'Johann_Gottfried_Immanuel_Berger': 'male', 'Johndale_Solem': 'male', 'John_M._Donaldson': 'male', 'Jolanta_Brodzicka': 'female', 'Josef_Emmerich_Lintz': 'male', 'Joseph_H_Gardella': 'male', 'J._Palmer': 'male', 'Julia_Tsiampali': 'female', 'Kalle_Manninen': 'male', 'Karl_Reinhold_von_Glasenapp': 'male', 'Kazimierz_Iwanicki': 'male', 'Khordong_Terchen_Nuden_Dorje': 'male', 'Konstantīns_Ovčiņņikovs': 'male', 'Laila_S._Espíndola': 'female', 'Lea_Ma': 'female', 'Lesley_Cohen': 'female', 'Lindsay_Hoyle': 'male', 'Li_Xiling': 'male', 'Louis_Matry': 'male', 'Luigi_de_Justinis': 'male', 'Maciej_Korpysz': 'male', 'Mantse_Aryeequaye': 'male', "Mareille_van_'t_Geloof": 'female', 'Maria_Ferreira_Santa_Bárbara': 'female', 'Marie_Larsson': 'female', 'Marko_Djukanović': 'male', 'Martin_Stemmler': 'male', 'Mascha_Smitt': 'female', 'Mauricio_Muñoz': 'male', 'Meredith_Bengoch_ap_Howell': 'male', 'Michael_S_Parmacek': 'male', 'Mike_Knox': 'male', 'Mitch_Sowards': 'male', 'M._P._Ahammed': 'male', 'Narve_Hoff': 'male', 'Nick_Miller': 'male', 'Ning_Rong': 'male', 'Oleg_Gulin': 'male', 'Osmundo_Evangelista_Rebouças': 'male', 'Paolo_Tiralongo': 'male', 'Paul_Dearlove': 'male', 'Peder_Arvidsson_Ribbing': 'male', 'Peter_Hebolt': 'male', 'Philipp_Christoph_Herwart': 'male', 'Pietro_Pancrazi': 'male', 'Quinton_Alston': 'male', 'Ranva_Marie_Jensen': 'female', 'Renato_Vugrinec': 'male', 'Richard_Mansfield': 'male', 'Robert_Darcy': 'male', 'Robert_Trewick_Bone': 'male', 'Ronald_Francis_Drake': 'male', 'Rudolf_Stolzmann': 'male', 'Sally_Rubin': 'female', 'Sara_Del_Rey': 'female', 'Sebastian_Wredenberg': 'male', 'Shaunzinski_Gortman': 'female', 'Sigmund_Baar': 'male', 'Sir_William_Lambton': 'male', 'Stanisław_Kadyi': 'male', 'Steven_Gellman': 'male', 'Suzanne_Duval': 'female', 'Tang_Yue': 'male', 'Theodore_Harding_Rand': 'male', 'Thomas_Lesley,_of_Felton': 'male', 'Tiril_Wishman_Eeg-Henriksen': 'female', 'Torquatus': 'male', 'Unknown_child_Buxton': 'male', 'Vasile_Lascu': 'male', 'Vilém_Neugröschl': 'male', 'Volodymyr_Eismont': 'male', 'Wang_Shi(Liupeng_Mu)': 'female', 'Wilfried_Passow': 'male', 'William_Greenleaf_Eliot': 'male', 'Willi_Wottreng': 'male', 'Xiang_Shi(Wife_of_Wu_Jun)': 'female', 'Yaroslava_Rurikovna': 'female', 'Yūko_Nihei': 'female', 'Zhang_Jian': 'male', 'Zhuang_Shi(Wife_of_Chenjiuguan)': 'female'}
    

if __name__ == "__main__":
    pytest.main(sys.argv)
