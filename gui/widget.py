# ~coding: utf-8~

import Tkinter as tk

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
