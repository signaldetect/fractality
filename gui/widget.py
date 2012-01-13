# ~coding: utf-8~

import Tkinter as tk
import os

class TipButton(tk.Button):
  tip_delay = 1000

  def __init__(self, master=None, tip='', **kw):
    tk.Button.__init__(self, master, kw)
    #
    self.bind('<Enter>', self._delayedshow)
    self.bind('<Button-1>', self._leave)
    self.bind('<Leave>', self._leave)
    #
    self.frame = tk.Toplevel(self, bd=1, bg='black')
    self.frame.withdraw()
    self.frame.overrideredirect(1)
    self.frame.transient()
    #
    l = tk.Label(self.frame, text=tip, bg='yellow', justify='left')
    l.update_idletasks()
    l.pack()
    l.update_idletasks()
    #
    self.tipwidth = l.winfo_width()
    self.tipheight = l.winfo_height()

  def _delayedshow(self, event):
    self.focus_set()
    self.request = self.after(self.tip_delay, self._show)

  def _show(self):
    self.update_idletasks()
    fixx = self.winfo_rootx() + self.winfo_width()
    fixy = self.winfo_rooty() + self.winfo_height()
    #
    if (fixx + self.tipwidth) > self.winfo_screenwidth():
      fixx -= self.winfo_width() + self.tipwidth
    if (fixy + self.tipheight) > self.winfo_screenheight():
      fixy -= self.winfo_height() + self.tipheight
    #
    self.frame.geometry('+%d+%d' % (fixx, fixy))
    self.frame.deiconify()
    #print self.frame.geometry()
    #print self.winfo_screenwidth()

  def _leave(self, event):
    self.frame.withdraw()
    self.after_cancel(self.request)

class Dialog(tk.Toplevel):
  def __init__(self, parent, title=None, wait=False):
    tk.Toplevel.__init__(self, parent)
    self.transient(parent)
    #
    if title:
      self.title(title)
    #
    self.parent = parent
    self.result = None
    self.initial_focus = None
    #
    self.body()
    self.buttonbox()
    self.grab_set()
    #
    if not self.initial_focus:
      self.initial_focus = self
    #
    self.protocol('WM_DELETE_WINDOW', self.cancel)
    self.geometry('+%d+%d' % (parent.winfo_rootx(), parent.winfo_rooty()))
    self.wm_iconbitmap(os.path.join('gui', 'images', 'logo.ico'))
    self.initial_focus.focus_set()
    #
    if wait:
      self.wait_window(self)

  def body(self):
    '''
      Create dialog body.
      Overridable
    '''
    body = tk.Frame(self)
    body.pack(padx=5, pady=5)

  def buttonbox(self):
    '''
      Add standard button box.
      Overridable
    '''
    box = tk.Frame(self)
    #
    w = tk.Button(box, text='OK', width=10, command=self.ok,
                  default=tk.ACTIVE)
    w.pack(side=tk.LEFT, padx=5, pady=5)
    #
    w = tk.Button(box, text='Cancel', width=10, command=self.cancel)
    w.pack(side=tk.LEFT, padx=5, pady=5)
    #
    self.bind('<Return>', self.ok)
    self.bind('<Escape>', self.cancel)
    #
    box.pack()

  def align_center(self):
    x = self.parent.winfo_rootx()
    y = self.parent.winfo_rooty()
    x += (self.parent.winfo_width() - self.winfo_width()) / 2
    y += (self.parent.winfo_height() - self.winfo_height()) / 2
    #
    self.geometry('+%d+%d' % (x, y))
    self.update()

  def ok(self, event=None):
    '''
      Standard button semantics.
      Overridable
    '''
    if not self.validate():
      self.initial_focus.focus_set() # put focus back
      return
    #
    self.withdraw()
    self.update_idletasks()
    #
    self.apply()
    self.cancel()

  def cancel(self, event=None):
    '''
      Overridable
    '''
    # Put focus back to the parent window
    self.parent.focus_set()
    self.destroy()

  def validate(self):
    '''
      Overridable
    '''
    return True

  def apply(self):
    '''
      Overridable
    '''
    pass

class Meter(tk.Frame):
  '''
    A simple progress bar widget
  '''

  def __init__(self, master, fillcolor='blue', text='', value=0.0, **kw):
    tk.Frame.__init__(self, master, bg='white', width=350, height=20)
    self.configure(**kw)
    #
    self._c = tk.Canvas(self, bg=self['bg'], width=self['width'],
                        height=self['height'], highlightthickness=0,
                        relief='flat', bd=0)
    self._c.pack(fill='x', expand=1)
    self._r = self._c.create_rectangle(0, 0, 0, int(self['height']),
                                       fill=fillcolor, width=0)
    self._t = self._c.create_text(int(self['width']) / 2,
                                  int(self['height']) / 2, text='')
    #
    self.set(value, text)

  def set(self, value=0.0, text=None):
    # Make the value failsafe
    if value < 0.0:
      value = 0.0
    elif value > 1.0:
      value = 1.0
    #
    if text == None:
      # If no text is specified get the default percentage string
      text = str(int(round(100 * value))) + ' %'
    #
    self._c.coords(self._r, 0, 0, int(self['width']) * value,
                   int(self['height']))
    self._c.itemconfigure(self._t, text=text)

class ProgressDialog(Dialog):
  meter = None
  callback = None

  def __init__(self, parent, title='Processing...', callback=None):
    Dialog.__init__(self, parent, title)
    self.callback = callback
    self.protocol('WM_DELETE_WINDOW', self.abort)

  def body(self):
    '''
      Overridden
    '''
    self.meter = Meter(self)
    self.meter.pack(side=tk.TOP, padx=5, pady=5)

  def buttonbox(self):
    '''
      Add standard button box.
      Overridable
    '''
    box = tk.Frame(self)
    #
    w = tk.Button(box, text='Abort', width=10, command=self.abort)
    w.pack(side=tk.LEFT, padx=5, pady=5)
    #
    box.pack(side=tk.BOTTOM)
  
  def abort(self):
    self.callback()
    self.cancel()
