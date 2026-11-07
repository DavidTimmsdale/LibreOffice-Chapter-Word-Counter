import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import chaptercounter as cc
from connection import connect
ctx, desktop = connect()
class Model:
 def __init__(self): self.listeners=[]
 def supportsService(self,name):return name==cc.MODULE
 def addModifyListener(self,x):self.listeners.append(x)
 def removeModifyListener(self,x):self.listeners.remove(x)
class View:
 def __init__(self):self.model=Model();self.listeners=[]
 def getModel(self):return self.model
 def addSelectionChangeListener(self,x):self.listeners.append(x)
 def removeSelectionChangeListener(self,x):self.listeners.remove(x)
class Frame:
 def __init__(self):self.view=View();self.listeners=[]
 def getController(self):return self.view
 def addFrameActionListener(self,x):self.listeners.append(x)
 def removeFrameActionListener(self,x):self.listeners.remove(x)
f=Frame();item=SimpleNamespace(Text='');c=cc.StatusController(ctx);c.static=True
c.initialize([SimpleNamespace(Name='Frame',Value=f),SimpleNamespace(Name='StatusbarItem',Value=item)])
c.update();assert item.Text=='Chapter: — / —'
old=f.view;assert old.listeners==[c] and old.model.listeners==[c]
f.view=View();c.frameAction(None)
assert not old.listeners and not old.model.listeners
assert f.view.listeners==[c] and f.view.model.listeners==[c]
assert c.mouseButtonDown(None) is False and c.mouseButtonUp(None) is False and c.mouseMove(None) is False
# Rebinding to an unsupported model must clear the previous chapter count.
c.static=False; item.Text='Chapter: 3 / 4'
previous=f.view
f.view=View()
f.view.model.supportsService=lambda name: False
c.update(); assert item.Text=='Chapter: — / —'
assert not previous.listeners and not previous.model.listeners
c.dispose();c.dispose();c.update()
assert not f.listeners and not f.view.listeners and not f.view.model.listeners
print('PASS static controller alone, view rebinding, all listener removals, idempotent disposal, mouse pass-through')
for text,expected in [('one two\nthree',3),("don't well-known",2),('one—two–three',3),('',0),('one\u00a0two',2)]:
 assert cc.word_count(text)==expected,(text,expected)
assert cc.word_count('one/two','/')==2
print('PASS documented word rules')
