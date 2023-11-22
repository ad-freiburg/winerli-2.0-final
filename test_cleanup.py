""" Johanna Götz """

import pytest
import sys
from cleanup_page import PageCleaner


def test_strip_templates_empty():
    pc = PageCleaner('')
    assert pc.strip_templates() == ''


def test_strip_templates_link():
    # Links won't be stripped
    pc = PageCleaner('[[Fear of the Dark (song)|Fear of the Dark]]')
    assert pc.strip_templates() == '[[Fear of the Dark (song)|Fear of the Dark]]'


def test_strip_heading():
    # Strip bold/italic formatting
    pc = PageCleaner("""
    '''''Arachnophobia''''' is a 1990 American [[black comedy]] [[horror film]]
    directed by [[Frank Marshall (producer)|Frank Marshall]]
    """)
    assert pc.strip_templates() == """
    Arachnophobia is a 1990 American [[black comedy]] [[horror film]]
    directed by [[Frank Marshall (producer)|Frank Marshall]]
    """


def test_strip_bolditalic():
    # Strip bold/italic formatting
    pc = PageCleaner("""
    '''''Arachnophobia''''' is a 1990 American [[black comedy]] [[horror film]]
    directed by [[Frank Marshall (producer)|Frank Marshall]]
    """)
    assert pc.strip_templates() == """
    Arachnophobia is a 1990 American [[black comedy]] [[horror film]]
    directed by [[Frank Marshall (producer)|Frank Marshall]]
    """


def test_strip_templates_image():
    # The image will be ignored but the links in the description will be extracted
    pc = PageCleaner("""
    [[Image:Kai Hansen.jpg|180px|thumb|[[Kai Hansen]] of [[Gamma Ray (band)|Gamma Ray]],
    ex-[[Helloween]] during a show in Barcelona, Spain.
    Hansen is widely regarded as the "godfather of power metal".]]
    """)
    assert pc.strip_templates() == """
    
[[Kai Hansen]] of [[Gamma Ray (band)|Gamma Ray]],
    ex-[[Helloween]] during a show in Barcelona, Spain.
    Hansen is widely regarded as the "godfather of power metal". 

    """


def test_strip_short_description():
    # The image will be ignored but the links in the description will be extracted
    pc = PageCleaner("""
    {{Short description|Ratio of how much light is reflected back from a body}}
    """)
    assert pc.strip_templates() == """
    Ratio of how much light is reflected back from a body.

    """


def test_strip_templates_html():
    # The image will be ignored but the links in the description will be extracted
    pc = PageCleaner("""
    <h1>Headline</h1>
    <blockquote>Test test <caption>Bla bla</caption></blockquote>
    <small>Small text</small> <strong>bold text</strong>
    <sup>super</sup> <sub>sub</sub>
    <div>
    <center>centered</center>
    <abbr>abbreviation</abbr>
    <del>deleted</del>
    </div>
    """)
    assert pc.strip_templates() == """
    Headline
    Test test Bla bla
    Small text bold text
    super sub
    
    centered
    abbreviation
    deleted
    
    """


def test_strip_templates_mixed_1():
    pc = PageCleaner("""
    '''Konrad Zuse''' ({{IPA-de|'k?n?at 'tsu?z?|lang}}; 22 June 1910 – 18 December 1995) was a German [[civil engineer]], inventor and [[computer pioneer]]. His greatest achievement was the world's first programmable computer; the functional program-controlled [[Turing completeness|Turing-complete]] [[Z3 (computer)|Z3]] became operational in May 1941. Thanks to this machine and its predecessors, Zuse has often been regarded as the inventor of the modern computer.<ref>[http://ed-thelen.org/comp-hist/Zuse_Z1_and_Z3.pdf PDF] Raúl Rojas: Konrad Zuse’s Legacy: The Architecture of the Z1 and Z3</ref><ref>[http://www.inf.fu-berlin.de/~rojas/1997/Universal_Computer.pdf] [http://citeseerx.ist.psu.edu/viewdoc/download;?doi=10.1.1.37.665&rep=rep1&type=pdf] Raúl Rojas: How to make Zuse's Z3 a universal computer.</ref><ref>[http://www.rtd-net.de/Zuse.html RTD Net]: "From various sides Konrad Zuse was awarded with the title "Inventor of the computer"."</ref><ref>[http://www.german-way.com/famous-konrad-zuse.html GermanWay]: "(...)German inventor of the computer"</ref><ref>[http://www.monstersandcritics.com/tech/features/article_1566782.php/Z-like-Zuse-German-inventor-of-the-computer Monsters & Critics] {{webarchive |url=https://web.archive.org/web/20130522022610/http://www.monstersandcritics.com/tech/features/article_1566782.php/Z-like-Zuse-German-inventor-of-the-computer |date=May 22, 2013 }}: "he [Zuse] built the world's first computer in Berlin"</ref><ref>[http://inventors.about.com/library/weekly/aa050298.htm About.com]: "Konrad Zuse earned the semiofficial title of 'inventor of the modern computer{{'"}}</ref>

Zuse was also noted for the S2 computing machine, considered the first [[process control]] computer. He founded one of the earliest computer businesses in 1941, producing the [[Z4 (computer)|Z4]], which became the world's first commercial computer. From 1943<ref>''Inception of a universal theory of computation with special consideration of the propositional calculus and its application to relay circuits'' (Zuse, Konrad, (1943) "Ansätze einer Theorie des allgemeinen Rechnens unter besonderer Berücksichtigung des Aussagenkalküls und dessen Anwendung auf Relaisschaltungen"), unpublished manuscript, Zuse Papers 045/018.</ref> to 1945<ref>A book on the subject: [http://www.zib.de/zuse/English_Version/Inhalt/Texte/Chrono/40er/Pdf/0233.pdf (full text of the 1945 manuscript)] {{webarchive|url=https://web.archive.org/web/20120210150041/http://www.zib.de/zuse/English_Version/Inhalt/Texte/Chrono/40er/Pdf/0233.pdf |date=2012-02-10 }}</ref> he designed the first [[high-level programming language]], [[Plankalkül]].<ref name="HZ2010-11-18"/> In 1969, Zuse suggested the concept of a [[digital physics|computation-based universe]] in his book ''Rechnender Raum'' (''[[Calculating Space]]'').

Much of his early work was financed by his family and commerce, but after 1939 he was given resources by the [[Nazi Germany|Nazi German]] government.<ref name="books.google.com">[https://books.google.com/books?id=gayW7Z-B_e8C&pg=PA82&dq=zuse,+nazi&lr=&cd=24#v=onepage&q=zuse%2C%20nazi&f=false "Weapons Grade: How Modern Warfare Gave Birth To Our High-Tech World"], David Hambling. Carroll & Graf Publishers, 2006. {{ISBN|0-7867-1769-6}}, {{ISBN|978-0-7867-1769-9}}. Retrieved March 14, 2010.</ref> Due to [[World War II]], Zuse's work went largely unnoticed in the [[United Kingdom]] and the [[United States]]. Possibly his first documented influence on a US company was [[IBM]]'s option on his patents in 1946.

There is a replica of the Z3, as well as the original Z4, in the [[Deutsches Museum]] in [[Munich]]. The [[Deutsches Technikmuseum Berlin|Deutsches Technikmuseum]] in [[Berlin]] has an exhibition devoted to Zuse, displaying twelve of his machines, including a replica of the [[Z1 (computer)|Z1]] and several of Zuse's paintings.
    """)
    assert pc.strip_templates() == """
    Konrad Zuse (; 22 June 1910 – 18 December 1995) was a German [[civil engineer]], inventor and [[computer pioneer]]. His greatest achievement was the world's first programmable computer; the functional program-controlled [[Turing completeness|Turing-complete]] [[Z3 (computer)|Z3]] became operational in May 1941. Thanks to this machine and its predecessors, Zuse has often been regarded as the inventor of the modern computer.

Zuse was also noted for the S2 computing machine, considered the first [[process control]] computer. He founded one of the earliest computer businesses in 1941, producing the [[Z4 (computer)|Z4]], which became the world's first commercial computer. From 1943 to 1945 he designed the first [[high-level programming language]], [[Plankalkül]]. In 1969, Zuse suggested the concept of a [[digital physics|computation-based universe]] in his book Rechnender Raum ([[Calculating Space]]).

Much of his early work was financed by his family and commerce, but after 1939 he was given resources by the [[Nazi Germany|Nazi German]] government. Due to [[World War II]], Zuse's work went largely unnoticed in the [[United Kingdom]] and the [[United States]]. Possibly his first documented influence on a US company was [[IBM]]'s option on his patents in 1946.

There is a replica of the Z3, as well as the original Z4, in the [[Deutsches Museum]] in [[Munich]]. The [[Deutsches Technikmuseum Berlin|Deutsches Technikmuseum]] in [[Berlin]] has an exhibition devoted to Zuse, displaying twelve of his machines, including a replica of the [[Z1 (computer)|Z1]] and several of Zuse's paintings.
    """


def test_strip_templates_mixed_2():
    pc = PageCleaner("""
    {| class="wikitable"
|-
! Species !! Image !! IUCN Red List status and distribution
|- style="vertical-align: top;
|[[Domestic cat]] (''F. catus'') {{small|Linnaeus, 1758}}<ref name=Linnaeus/>
|[[File:Jammlich crop.jpg]]
|{{IUCN status|NE}}<br> Worldwide in association with humans or [[feral]]<ref>{{Cite book |title=A Natural History of Domesticated Mammals |last=Clutton-Brock |first=J. |publisher=Cambridge University Press |location=Cambridge, England |date=1999 |isbn=978-0-521-63495-3 |edition=Second |pages=133–140 |chapter=Cats |oclc=39786571 |orig-year=1987 |chapter-url= https://books.google.com/books?id=cgL-EbbB8a0C&pg=PA133}}</ref>
|- style="vertical-align: top;
||[[European wildcat]] (''F. silvestris'') {{small|Schreber, 1777}}<ref>{{cite book |last=Schreber |first=J. C. D. |date=1778 |chapter=Die wilde Kaze |trans-chapter=The wild Cat |pages=397–402 |title=Die Säugthiere in Abbildungen nach der Natur mit Beschreibungen (Dritter Theil) |publisher=Expedition des Schreber'schen Säugthier- und des Esper'schen Schmetterlingswerkes |location=Erlangen |chapter-url=http://digi.ub.uni-heidelberg.de/diglit/schreber1875textbd3/0095?page_query=397&navmode=struct&action=pagesearch&sid=cc4bffe3d0372c2d2c5c1ddb03aed21d}}</ref>
diverged {{font color|#882277|1.62 to 0.59 Mya}}<br>
|[[File:European_Wildcat_Nationalpark_Bayerischer_Wald_03.jpg]]
|{{IUCN status|LC|3847}}<ref>{{cite iucn |title=''Felis silvestris'' |author=Yamaguchi, N. |author2=Kitchener, A. |author3=Driscoll, C. |author4=Nussberger, B. |name-list-style=amp |page=e.T60354712A50652361 |date=2015 |access-date=29 October 2018}}</ref>
[[File:EuropeanWildcat_distribution.jpg]]
|- style="vertical-align: top;
|[[African wildcat]] (''F. lybica'') {{small|[[Georg Forster|Forster]], 1780}}<ref>{{cite book |last1=Forster |first1=G. R. |year=1780 |title=Herrn von Büffons Naturgeschichte der vierfüssigen Thiere. Mit Vermehrungen, aus dem Französischen übersetzt. Sechster Band |trans-title=Mr. von Büffon‘s Natural History of Quadrupeds. With additions, translated from French. Volume 6 |location=Berlin |publisher=Joachim Pauli |chapter=LIII. Der Karakal |pages=299–319 |chapter-url=https://books.google.com/books?id=qohRAAAAYAAJ&pg=SL26-PA13}}</ref>
diverged {{font color|#882277|1.86 to 0.72 Mya}}<br>
|[[File:Parc des Felins Chat de Gordoni 28082013 2.jpg]]
|{{IUCN status|LC|3847|}}<ref>{{cite iucn |title=''Felis lybica'' |author=Ghoddousi, A. |author2=Belbachir, F. |author3=Durant, S.M. |author4=Herbst, M. |author5=Rosen, T. |name-list-style=amp |page=e.T131299383A154907281 |date=2022 }}</ref>
[[File:AfricanWildcat_distribution.jpg]]
|}
    """)
    assert pc.strip_templates() == """

Species
Image
IUCN Red List status and distribution

[[Domestic cat]] (F. catus) Linnaeus, 1758

Worldwide in association with humans or [[feral]]

[[European wildcat]] (F. silvestris) Schreber, 1777
diverged 1.62 to 0.59 Mya



[[African wildcat]] (F. lybica) [[Georg Forster|Forster]], 1780
diverged 1.86 to 0.72 Mya



    """


def test_strip_templates_mixed_3():
    pc = PageCleaner("""
    ====United Kingdom====
{{see also|Chief Mouser to the Cabinet Office}}
*[[File:Larry Chief Mouser.jpg|thumb|[[Larry (cat)|Larry]], the current Chief Mouser of No. 10]]'''[[Catmando]]''', joint leader of the [[Official Monster Raving Loony Party]] from 1999 to 2002
*'''[[Freya (cat)|Freya]]''', [[Chief Mouser to the Cabinet Office]] for a brief period in 2012–2014, performing the role jointly with [[Larry (cat)|Larry]]
*'''[[Gladstone (cat)|Gladstone]]''', Chief Mouser of [[HM Treasury]] at [[Whitehall]] in London since 2016
*'''[[Hamish McHamish]]''' (1999 – 11 September 2014), a long-haired ginger cat that was adopted by the citizens of the town of [[St Andrews]], [[Fife]], [[Scotland]] and has had a statue built in his honour. Something of a local feline celebrity with tourists and students, he became famous after the publication of a book titled "Hamish McHamish: Cool Cat About Town". In 2013, a bronze statue was crowd funded in his honour, unveiled in April 2014.
*'''[[Humphrey (cat)|Humphrey]]''', [[Chief Mouser to the Cabinet Office]] 1989–97, named for the character of [[Humphrey Appleby|Sir Humphrey Appleby]] in ''[[Yes Minister]]''.
*'''[[Larry (cat)|Larry]]''', [[Chief Mouser to the Cabinet Office]] since February 2011
*'''[[Palmerston (cat)|Palmerston]]''', Chief [[wiktionary:Mouser|Mouser]] of [[Foreign & Commonwealth Office]] since April 2016
*'''[[Peta (cat)|Peta]]''', [[Chief Mouser to the Cabinet Office]] beginning in 1964; serving under three Prime Ministers
*'''[[Peter (chief mouser)|Peter]]''', [[Chief Mouser to the Cabinet Office]] 1929–1946; serving under five prime ministers, and three monarchs.
*'''[[Simon (cat)|Simon]]''', ship's cat on [[HMS Amethyst (U16)|HMS ''Amethyst'']] in 1949, during the [[Yangtze Incident]].
*'''[[Sybil (cat)|Sybil]]''', [[Chief Mouser to the Cabinet Office]] for a brief period in 2007 to 2009.
*'''[[Wilberforce (cat)|Wilberforce]]''', [[Chief Mouser to the Cabinet Office]] under four British Prime Ministers.
    """)
    print(repr(pc.strip_templates()))
    assert pc.strip_templates() == """United Kingdom


[[Larry (cat)|Larry]], the current Chief Mouser of No. 10 
[[Catmando]], joint leader of the [[Official Monster Raving Loony Party]] from 1999 to 2002
[[Freya (cat)|Freya]], [[Chief Mouser to the Cabinet Office]] for a brief period in 2012–2014, performing the role jointly with [[Larry (cat)|Larry]]
[[Gladstone (cat)|Gladstone]], Chief Mouser of [[HM Treasury]] at [[Whitehall]] in London since 2016
[[Hamish McHamish]] (1999 – 11 September 2014), a long-haired ginger cat that was adopted by the citizens of the town of [[St Andrews]], [[Fife]], [[Scotland]] and has had a statue built in his honour. Something of a local feline celebrity with tourists and students, he became famous after the publication of a book titled "Hamish McHamish: Cool Cat About Town". In 2013, a bronze statue was crowd funded in his honour, unveiled in April 2014.
[[Humphrey (cat)|Humphrey]], [[Chief Mouser to the Cabinet Office]] 1989–97, named for the character of [[Humphrey Appleby|Sir Humphrey Appleby]] in [[Yes Minister]].
[[Larry (cat)|Larry]], [[Chief Mouser to the Cabinet Office]] since February 2011
[[Palmerston (cat)|Palmerston]], Chief [[wiktionary:Mouser|Mouser]] of [[Foreign & Commonwealth Office]] since April 2016
[[Peta (cat)|Peta]], [[Chief Mouser to the Cabinet Office]] beginning in 1964; serving under three Prime Ministers
[[Peter (chief mouser)|Peter]], [[Chief Mouser to the Cabinet Office]] 1929–1946; serving under five prime ministers, and three monarchs.
[[Simon (cat)|Simon]], ship\'s cat on [[HMS Amethyst (U16)|HMS Amethyst]] in 1949, during the [[Yangtze Incident]].
[[Sybil (cat)|Sybil]], [[Chief Mouser to the Cabinet Office]] for a brief period in 2007 to 2009.
[[Wilberforce (cat)|Wilberforce]], [[Chief Mouser to the Cabinet Office]] under four British Prime Ministers.
    """


if __name__ == "__main__":
    pytest.main(sys.argv)

