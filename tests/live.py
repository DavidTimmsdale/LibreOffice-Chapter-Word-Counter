import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import chaptercounter as cc
from connection import connect
ctx, desktop = connect()
doc=desktop.loadComponentFromURL('private:factory/swriter','_blank',0,())
styles=doc.StyleFamilies.getByName('ParagraphStyles')
styles.insertByName('Chapter',doc.createInstance('com.sun.star.style.ParagraphStyle'))
doc.Text.String='Preface words\rFirst chapter\rone two three\rfour five\rSecond chapter\rsix seven eight nine'
p=doc.Text.createTextCursor();p.gotoStart(False);p.gotoNextParagraph(False);p.ParaStyleName='Chapter';p.gotoNextParagraph(False);p.gotoNextParagraph(False);p.gotoNextParagraph(False);p.ParaStyleName='Chapter'
v=doc.CurrentController

def at(paragraph,offset=0,select_from=None):
 c=doc.Text.createTextCursor();c.gotoStart(False)
 for _ in range(paragraph):c.gotoNextParagraph(False)
 c.goRight(offset,False)
 if select_from is not None:c.gotoRange(select_from,True)
 v.select(c)
 time.sleep(.08)
 return c

def status(d=doc):
 a=d.CurrentController.Frame.LayoutManager.getElement(cc.RESOURCE).getRealInterface().getAccessibleContext()
 return a.getAccessibleChild(3).getAccessibleContext().getText()

def check(label,expected):
 actual=cc.chapter_counts(doc,v);assert actual==expected,(label,actual,expected)
 expected_text='Chapter: %s / %s'%expected if expected is not None else 'Chapter: — / —'
 actual_text=status();assert actual_text==expected_text,(label,actual_text,expected_text)
 print('PASS',label,actual_text)
try:
 at(0,3);check('before first heading',None)
 at(1,2);check('inside heading',(0,5))
 at(2,0);check('chapter start',(0,5))
 at(2,7);check('cursor midway',(2,5))
 at(3,9);check('chapter end',(5,5))
 at(5,4);check('second chapter',(1,4))
 beginning=at(2,0).Start
 at(5,9,beginning);check('backward selection spanning chapters',(2,4))
 at(2,7)
 edit=doc.Text.createTextCursor();edit.gotoEnd(False);edit.String=' ten'
 time.sleep(.1);check('edit outside active chapter',(2,5))
 at(5,99);check('final chapter edit',(5,5))
 c=at(2,0);c.String='new ';at(2,4);check('insert in current chapter',(1,6))
 c=doc.Text.createTextCursorByRange(c.Start);c.goRight(4,True);c.String='';at(2,0);check('delete in current chapter',(0,5))
 other=desktop.loadComponentFromURL('private:factory/swriter','_blank',0,())
 other.Text.String='Unrelated document';time.sleep(.1)
 assert status(other)=='Chapter: — / —';assert status()=='Chapter: 0 / 5';print('PASS independent document views')
 other.close(True)
 at(3,9);check('after closing other document',(5,5))
 at(2,0)
 edit=doc.Text.createTextCursorByRange(v.ViewCursor.End);edit.String='fresh '
 time.sleep(.1);check('modify listener without moving selection',(1,6))
 # Changing paragraph styles must change chapter boundaries immediately.
 heading=doc.Text.createTextCursor();heading.gotoStart(False);heading.gotoNextParagraph(False);heading.ParaStyleName='Standard'
 time.sleep(.1);check('remove chapter style',None)
 heading.ParaStyleName='Chapter';time.sleep(.1);check('restore chapter style',(1,6))
 # Read-only computation must preserve the manuscript state and selection.
 before=doc.Text.String; modified=doc.isModified(); selected=v.ViewCursor.String
 for _ in range(5):cc.chapter_counts(doc,v)
 assert doc.Text.String==before and doc.isModified()==modified and v.ViewCursor.String==selected
 print('PASS counting does not alter text, modified state, or selection')
finally:
 doc.close(True)
