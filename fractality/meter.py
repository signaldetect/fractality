# ~coding: utf-8~

import Tkinter
import time

class Meter(Tkinter.Frame):
  '''
    A simple progress bar widget
  '''

  def __init__(self, master, fillcolor='blue', text='', value=0.0, **kw):
    Tkinter.Frame.__init__(self, master, bg='white', width=350, height=20)
    self.configure(**kw)
    #
    self._c = Tkinter.Canvas(self, bg=self['bg'], width=self['width'], height=self['height'],
                             highlightthickness=0, relief='flat', bd=0)
    self._c.pack(fill='x', expand=1)
    self._r = self._c.create_rectangle(0, 0, 0, int(self['height']), fill=fillcolor, width=0)
    self._t = self._c.create_text(int(self['width']) / 2, int(self['height']) / 2, text='')
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
      # if no text is specified get the default percentage string
      text = str(int(round(100 * value))) + ' %'
    #
    self._c.coords(self._r, 0, 0, int(self['width']) * value, int(self['height']))
    self._c.itemconfigure(self._t, text=text)

class Demo:
  def __init__(self, parent):
    self.root = parent
    #
    btn = Tkinter.Button(parent, text='Run', command=self.process)
    btn.pack(side=Tkinter.TOP)
    #
    self.meter = Meter(parent)
    self.meter.pack(side=Tkinter.BOTTOM)

  def process(self):
    n = 10000
    tic = time.time()
    #
    for i in xrange(n):
      self.meter.set((float(i) + 1.0) / float(n))
      self.root.update()
    #
    toc = time.time()
    print toc - tic, ' has elapsed'

if __name__ == '__main__':
  root = Tkinter.Tk()
  root.title('Demo')
  widget = Demo(root)
  root.mainloop()
