"""Run against an isolated office started with CHAPTERCOUNTER_TEST_LABEL=1."""
import time
from connection import connect
ctx, desktop = connect()
doc = desktop.loadComponentFromURL('private:factory/swriter', '_blank', 0, ())
try:
    time.sleep(.1)
    supplier = ctx.ServiceManager.createInstanceWithContext('com.sun.star.ui.ModuleUIConfigurationManagerSupplier', ctx)
    manager = supplier.getUIConfigurationManager('com.sun.star.text.TextDocument')
    settings = manager.getSettings('private:resource/statusbar/statusbar', False)
    commands = [dict((p.Name, p.Value) for p in settings.getByIndex(i))['CommandURL'] for i in range(settings.getCount())]
    command = 'vnd.dtimmsdale.chaptercounter:statusbartest'
    assert commands.count(command) == 1
    assert commands.index(command) == commands.index('.uno:StateWordCount') + 1
    accessible = doc.CurrentController.Frame.LayoutManager.getElement('private:resource/statusbar/statusbar').getRealInterface().getAccessibleContext()
    label = accessible.getAccessibleChild(commands.index(command)).getAccessibleContext().getText()
    assert label == 'Chapter: — / —', label
    print('PASS automatic insertion and actual status-bar initial label:', label)
finally:
    doc.close(True)
