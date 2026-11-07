"""Boundary and performance integration tests; disposable profile only."""
import sys, time, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import chaptercounter as cc
from connection import connect
ctx, desktop = connect()
doc = desktop.loadComponentFromURL('private:factory/swriter', '_blank', 0, ())
v = doc.CurrentController

def cursor(paragraph, offset=0):
    c = doc.Text.createTextCursor(); c.gotoStart(False)
    for _ in range(paragraph): c.gotoNextParagraph(False)
    c.goRight(offset, False)
    return c

def check(paragraph, offset, expected):
    v.select(cursor(paragraph, offset))
    actual = cc.chapter_counts(doc, v)
    assert actual == expected, (actual, expected)
    if actual: assert 0 <= actual[0] <= actual[1]
try:
    doc.Text.String = 'one two\rthree'
    check(1, 2, None)
    styles = doc.StyleFamilies.getByName('ParagraphStyles')
    styles.insertByName('Chapter', doc.createInstance('com.sun.star.style.ParagraphStyle'))
    doc.Text.String = 'Heading A\rone two\rHeading B\rHeading C\rthree four'
    for n in (0,2,3): cursor(n).ParaStyleName = 'Chapter'
    for args in [(0,0,(0,2)),(0,5,(0,2)),(1,0,(0,2)),(1,7,(2,2)),(2,0,(0,0)),(2,5,(0,0)),(3,0,(0,2)),(4,10,(2,2))]: check(*args)
    for backward in (False, True):
        c=cursor(4,5) if backward else cursor(1,0)
        c.gotoRange(cursor(1,0) if backward else cursor(4,5),True)
        v.select(c)
        assert cc.chapter_counts(doc,v)==(1,2)
    print('PASS missing style, exact boundaries, consecutive empty chapter, forward/backward cross-chapter selection, progress bounds')
    for size in (10000,30000):
        doc.Text.String='Heading\r'+' '.join(['word']*size)
        cursor(0).ParaStyleName='Chapter'
        cursor(1).ParaStyleName='Standard'
        c=doc.Text.createTextCursor();c.gotoEnd(False);v.select(c)
        times=[]
        for _ in range(7):
            start=time.perf_counter(); result=cc.chapter_counts(doc,v);times.append((time.perf_counter()-start)*1000)
            assert result==(size,size),result
        print('BENCHMARK %d words: median %.2f ms; max %.2f ms; 7 synchronous calls'%(size,statistics.median(times),max(times)))
finally:
    doc.close(True)
