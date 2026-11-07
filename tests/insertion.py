"""Test insertion independently; use a disposable profile."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import chaptercounter as cc
from connection import connect
ctx, desktop = connect()
supplier = ctx.ServiceManager.createInstanceWithContext('com.sun.star.ui.ModuleUIConfigurationManagerSupplier', ctx)
manager = supplier.getUIConfigurationManager(cc.MODULE)
s = manager.getSettings(cc.RESOURCE, True)
for i in reversed(range(s.getCount())):
    if dict((p.Name, p.Value) for p in s.getByIndex(i))['CommandURL'] == cc.COMMAND:
        s.removeByIndex(i)
manager.replaceSettings(cc.RESOURCE, s)
assert cc.insert_item(ctx) is True
assert cc.insert_item(ctx) is False
s = manager.getSettings(cc.RESOURCE, False)
commands = [dict((p.Name, p.Value) for p in s.getByIndex(i))['CommandURL'] for i in range(s.getCount())]
assert commands.count(cc.COMMAND) == 1
assert commands.index(cc.COMMAND) == commands.index('.uno:StateWordCount') + 1
print('PASS independent insertion, placement and idempotence')
