# Copyright (c) 2026 David Timmsdale
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. See LICENSE or https://mozilla.org/MPL/2.0/.
"""Writer status-bar chapter counts; LibreOffice 7.4 Python UNO component."""
import logging
from logging.handlers import RotatingFileHandler
import re
import uno
import unohelper
from com.sun.star.beans import PropertyValue
from com.sun.star.lang import EventObject, XInitialization, XComponent
from com.sun.star.frame import XStatusbarController, XFrameActionListener, XStatusListener
from com.sun.star.util import XModifyListener, XUpdatable
from com.sun.star.view import XSelectionChangeListener
from com.sun.star.task import XJob

COMMAND = 'vnd.dtimmsdale.chaptercounter:statusbartest'
RESOURCE = 'private:resource/statusbar/statusbar'
CONTROLLER = 'org.dtimmsdale.chaptercounter.StatusControllerV09'
JOB = 'org.dtimmsdale.chaptercounter.InsertStatusJobV09'
MODULE = 'com.sun.star.text.TextDocument'

def logger(ctx):
    log = logging.getLogger('chaptercounter')
    if not log.handlers:
        subst = ctx.ServiceManager.createInstanceWithContext('com.sun.star.util.PathSubstitution', ctx)
        path = uno.fileUrlToSystemPath(subst.substituteVariables('$(user)', True))
        handler = RotatingFileHandler(path + '/chaptercounter.log', maxBytes=262144, backupCount=2)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        log.addHandler(handler)
        log.setLevel(logging.INFO)
        log.propagate = False
    return log

def prop(name, value):
    p = PropertyValue()
    p.Name, p.Value = name, value
    return p

def insert_item(ctx):
    supplier = ctx.ServiceManager.createInstanceWithContext('com.sun.star.ui.ModuleUIConfigurationManagerSupplier', ctx)
    manager = supplier.getUIConfigurationManager(MODULE)
    settings = manager.getSettings(RESOURCE, True)
    def command(i):
        return dict((p.Name, p.Value) for p in settings.getByIndex(i)).get('CommandURL')
    commands = [command(i) for i in range(settings.getCount())]
    # Remove only our own item, correcting duplicates and stale placement.
    wanted = commands.index('.uno:StateWordCount') + 1
    if commands.count(COMMAND) == 1 and commands.index(COMMAND) == wanted:
        return False
    for i in reversed(range(len(commands))):
        if commands[i] == COMMAND:
            settings.removeByIndex(i)
    commands = [command(i) for i in range(settings.getCount())]
    position = commands.index('.uno:StateWordCount') + 1
    item = (prop('CommandURL', COMMAND), prop('Type', 0), prop('Style', 0), prop('Width', 230), prop('Offset', 0))
    uno.invoke(settings, 'insertByIndex', (position, uno.Any('[]com.sun.star.beans.PropertyValue', item)))
    # Session-only: never store or overwrite the user's status-bar customization.
    manager.replaceSettings(RESOURCE, settings)
    logger(ctx).info('Inserted status item after StateWordCount')
    return True

class InsertStatusJob(unohelper.Base, XJob):
    def __init__(self, ctx):
        self.ctx = ctx
    def execute(self, args):
        log = logger(self.ctx)
        log.info('Insertion job executed')
        try:
            insert_item(self.ctx)
        except Exception:
            log.error('Insertion job failed')
            raise
        return ()

class StatusController(unohelper.Base, XStatusbarController, XInitialization, XComponent, XUpdatable, XStatusListener, XSelectionChangeListener, XModifyListener, XFrameActionListener):
    def __init__(self, ctx, *args):
        self.ctx = ctx
        self.log = logger(ctx)
        self.frame = self.item = self.view = self.model = None
        self.listeners = []
        self.dead = self.busy = False
        self.static = False  # Internal test seam; no environment-triggered development mode.
        if args:
            self.initialize(args)
    def initialize(self, args):
        try:
            values = {p.Name: p.Value for p in args}
            self.item = values['StatusbarItem']
            self.frame = values['Frame']
            self.frame.addFrameActionListener(self)
            self.item.Text = 'Chapter: — / —'
            self.item.AccessibleName = 'Chapter Counter'
            self.log.info('Controller initialized')
        except Exception:
            self.log.error('Controller initialization failed')
            raise
    def update(self):
        if self.dead or self.busy:
            return
        self.busy = True
        try:
            view = self.frame.getController()
            model = view.getModel() if view else None
            if view != self.view or model != self.model:
                self._detach()
                if model and model.supportsService(MODULE):
                    self.view, self.model = view, model
                    view.addSelectionChangeListener(self)
                    model.addModifyListener(self)
            if self.static:
                self.item.Text = 'Chapter: — / —'
            elif self.model:
                counts = chapter_counts(self.model, self.view)
                self.item.Text = ('Chapter: %s / %s' % counts) if counts is not None else 'Chapter: — / —'
                self.item.QuickHelpText = 'Words to selection end / total chapter words; Chapter headings excluded'
            else:
                self.item.Text = 'Chapter: — / —'
        except Exception:
            self.log.error('Controller update failed')
            if self.item:
                self.item.Text = 'Chapter: error (see log)'
        finally:
            self.busy = False
    def _detach(self):
        view, model = self.view, self.model
        self.view = self.model = None
        for obj, method in ((view, 'removeSelectionChangeListener'), (model, 'removeModifyListener')):
            if obj:
                try:
                    getattr(obj, method)(self)
                except Exception:
                    self.log.error('Listener cleanup: %s', method)
    def selectionChanged(self, event):
        self.update()
    def modified(self, event):
        self.update()
    def frameAction(self, event):
        self.update()
    def statusChanged(self, event):
        self.update()
    def disposing(self, event):
        if event.Source == self.frame:
            self.dispose()
        elif event.Source == self.model or event.Source == self.view:
            self._detach()
    def dispose(self):
        if self.dead:
            return
        self.dead = True
        self._detach()
        if self.frame:
            try:
                self.frame.removeFrameActionListener(self)
            except Exception:
                self.log.error('Frame listener cleanup')
        self.frame = self.item = None
        for listener in self.listeners[:]:
            try:
                listener.disposing(EventObject(self))
            except Exception:
                self.log.error('Dispose notification')
        self.listeners.clear()
        self.log.info('Controller disposed')
    def addEventListener(self, listener):
        self.listeners.append(listener)
    def removeEventListener(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)
    # No window creation, mouse capture, dispatch interception, or window changes.
    def mouseButtonDown(self, event): return False
    def mouseButtonUp(self, event): return False
    def mouseMove(self, event): return False
    def command(self, *args): pass
    def paint(self, *args): pass
    def click(self, *args): pass
    def doubleClick(self, *args): pass

def word_count(text, separators=''):
    """Whitespace/dash-separated words; internal apostrophes and hyphens stay intact."""
    return len(re.findall(r'[^\s' + re.escape('–—' + separators) + r']+', text))

def chapter_counts(model, view):
    text = model.Text
    selection = view.getSelection()
    if not hasattr(selection, 'getCount') or selection.getCount() == 0:
        return None
    end = None
    for i in range(selection.getCount()):
        part = selection.getByIndex(i)
        if not hasattr(part, 'getEnd') or part.getText() != text:
            return None  # Tables, frames, notes and object selections have separate text stories.
        candidate = part.getEnd()
        if end is None or text.compareRegionStarts(candidate, end) < 0:
            end = candidate
    cursor = text.createTextCursorByRange(end)
    cursor.gotoStartOfParagraph(False)
    in_heading = cursor.ParaStyleName == 'Chapter'
    while cursor.ParaStyleName != 'Chapter':
        if not cursor.gotoPreviousParagraph(False):
            return None
    cursor.gotoEndOfParagraph(False)
    start = cursor.getEnd()
    scan = text.createTextCursorByRange(start)
    stop = text.getEnd()
    while scan.gotoNextParagraph(False):
        if scan.ParaStyleName == 'Chapter':
            scan.gotoStartOfParagraph(False)
            stop = scan.getStart()
            break
    total = text.createTextCursorByRange(start)
    total.gotoRange(stop, True)
    separators = model.WordSeparator
    total_count = word_count(total.String, separators)
    if in_heading:
        return 0, total_count
    progress = text.createTextCursorByRange(start)
    progress.gotoRange(end, True)
    return min(word_count(progress.String, separators), total_count), total_count

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(StatusController, CONTROLLER, ('com.sun.star.frame.StatusbarController',))
g_ImplementationHelper.addImplementation(InsertStatusJob, JOB, ('com.sun.star.task.Job',))
