import pytest
import sys
from pprint import pprint

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
    print('~', repr(pc.strip_templates()), '~')
    assert pc.strip_templates() == """
    Headline
    Test test Bla bla
    Small text bold text
    super sub
    
    centered
    abbreviation
    deleted
    
    """

def test_strip_templates_html_2():
    # The image will be ignored but the links in the description will be extracted
    pc = PageCleaner("""
    '''Konrad Zuse''' ({{IPA-de|'k?n?at 'tsu?z?|lang}}; 22 June 1910 – 18 December 1995) was a German [[civil engineer]], inventor and [[computer pioneer]]. His greatest achievement was the world's first programmable computer; the functional program-controlled [[Turing completeness|Turing-complete]] [[Z3 (computer)|Z3]] became operational in May 1941. Thanks to this machine and its predecessors, Zuse has often been regarded as the inventor of the modern computer.<ref>[http://ed-thelen.org/comp-hist/Zuse_Z1_and_Z3.pdf PDF] Raúl Rojas: Konrad Zuse’s Legacy: The Architecture of the Z1 and Z3</ref><ref>[http://www.inf.fu-berlin.de/~rojas/1997/Universal_Computer.pdf] [http://citeseerx.ist.psu.edu/viewdoc/download;?doi=10.1.1.37.665&rep=rep1&type=pdf] Raúl Rojas: How to make Zuse's Z3 a universal computer.</ref><ref>[http://www.rtd-net.de/Zuse.html RTD Net]: "From various sides Konrad Zuse was awarded with the title "Inventor of the computer"."</ref><ref>[http://www.german-way.com/famous-konrad-zuse.html GermanWay]: "(...)German inventor of the computer"</ref><ref>[http://www.monstersandcritics.com/tech/features/article_1566782.php/Z-like-Zuse-German-inventor-of-the-computer Monsters & Critics] {{webarchive |url=https://web.archive.org/web/20130522022610/http://www.monstersandcritics.com/tech/features/article_1566782.php/Z-like-Zuse-German-inventor-of-the-computer |date=May 22, 2013 }}: "he [Zuse] built the world's first computer in Berlin"</ref><ref>[http://inventors.about.com/library/weekly/aa050298.htm About.com]: "Konrad Zuse earned the semiofficial title of 'inventor of the modern computer{{'"}}</ref>

Zuse was also noted for the S2 computing machine, considered the first [[process control]] computer. He founded one of the earliest computer businesses in 1941, producing the [[Z4 (computer)|Z4]], which became the world's first commercial computer. From 1943<ref>''Inception of a universal theory of computation with special consideration of the propositional calculus and its application to relay circuits'' (Zuse, Konrad, (1943) "Ansätze einer Theorie des allgemeinen Rechnens unter besonderer Berücksichtigung des Aussagenkalküls und dessen Anwendung auf Relaisschaltungen"), unpublished manuscript, Zuse Papers 045/018.</ref> to 1945<ref>A book on the subject: [http://www.zib.de/zuse/English_Version/Inhalt/Texte/Chrono/40er/Pdf/0233.pdf (full text of the 1945 manuscript)] {{webarchive|url=https://web.archive.org/web/20120210150041/http://www.zib.de/zuse/English_Version/Inhalt/Texte/Chrono/40er/Pdf/0233.pdf |date=2012-02-10 }}</ref> he designed the first [[high-level programming language]], [[Plankalkül]].<ref name="HZ2010-11-18"/> In 1969, Zuse suggested the concept of a [[digital physics|computation-based universe]] in his book ''Rechnender Raum'' (''[[Calculating Space]]'').

Much of his early work was financed by his family and commerce, but after 1939 he was given resources by the [[Nazi Germany|Nazi German]] government.<ref name="books.google.com">[https://books.google.com/books?id=gayW7Z-B_e8C&pg=PA82&dq=zuse,+nazi&lr=&cd=24#v=onepage&q=zuse%2C%20nazi&f=false "Weapons Grade: How Modern Warfare Gave Birth To Our High-Tech World"], David Hambling. Carroll & Graf Publishers, 2006. {{ISBN|0-7867-1769-6}}, {{ISBN|978-0-7867-1769-9}}. Retrieved March 14, 2010.</ref> Due to [[World War II]], Zuse's work went largely unnoticed in the [[United Kingdom]] and the [[United States]]. Possibly his first documented influence on a US company was [[IBM]]'s option on his patents in 1946.

There is a replica of the Z3, as well as the original Z4, in the [[Deutsches Museum]] in [[Munich]]. The [[Deutsches Technikmuseum Berlin|Deutsches Technikmuseum]] in [[Berlin]] has an exhibition devoted to Zuse, displaying twelve of his machines, including a replica of the [[Z1 (computer)|Z1]] and several of Zuse's paintings.
    """)
    #print('~', repr(pc.strip_templates()), '~')
    assert pc.strip_templates() == """
    Konrad Zuse (; 22 June 1910 – 18 December 1995) was a German [[civil engineer]], inventor and [[computer pioneer]]. His greatest achievement was the world's first programmable computer; the functional program-controlled [[Turing completeness|Turing-complete]] [[Z3 (computer)|Z3]] became operational in May 1941. Thanks to this machine and its predecessors, Zuse has often been regarded as the inventor of the modern computer.

Zuse was also noted for the S2 computing machine, considered the first [[process control]] computer. He founded one of the earliest computer businesses in 1941, producing the [[Z4 (computer)|Z4]], which became the world's first commercial computer. From 1943 to 1945 he designed the first [[high-level programming language]], [[Plankalkül]]. In 1969, Zuse suggested the concept of a [[digital physics|computation-based universe]] in his book Rechnender Raum ([[Calculating Space]]).

Much of his early work was financed by his family and commerce, but after 1939 he was given resources by the [[Nazi Germany|Nazi German]] government. Due to [[World War II]], Zuse's work went largely unnoticed in the [[United Kingdom]] and the [[United States]]. Possibly his first documented influence on a US company was [[IBM]]'s option on his patents in 1946.

There is a replica of the Z3, as well as the original Z4, in the [[Deutsches Museum]] in [[Munich]]. The [[Deutsches Technikmuseum Berlin|Deutsches Technikmuseum]] in [[Berlin]] has an exhibition devoted to Zuse, displaying twelve of his machines, including a replica of the [[Z1 (computer)|Z1]] and several of Zuse's paintings.
    """


if __name__ == "__main__":
    pytest.main(sys.argv)
