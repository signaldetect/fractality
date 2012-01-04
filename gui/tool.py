# ~coding: utf-8~

import os, time
import Tkinter as tk
import tkFileDialog
import tkMessageBox

from widget import TipButton

class ActionBar(tk.Frame):
  load_btn = None
  select_btn = None
  compress_btn = None
  decompress_btn = None

  def __init__(self, parent, actions):
    tk.Frame.__init__(self, master=parent, borderwidth=0, bg='grey')
    # Create buttons
    self.load_btn = self._add_button('Load image', 'load.ppm',
                                     callback=actions.load)
    self.select_btn = self._add_button('Select fragment', 'select.ppm',
                                       callback=actions.select)
    self.compress_btn = self._add_button('Compress', 'compress.ppm',
                                         callback=actions.compress)
    self.decompress_btn = self._add_button('Decompress', 'decompress.ppm',
                                           callback=actions.decompress)

  def _add_button(self, text, icon_name, callback):
    icon_name = os.path.join('gui', 'images', icon_name)
    icon = tk.PhotoImage(master=self, file=icon_name)
    btn = TipButton(master=self, tip=text, text=text,
                    padx=2, pady=2, image=icon, command=callback,
                    relief=tk.FLAT, borderwidth=0,
                    background='grey', activebackground='grey')
    btn._ntimage = icon
    btn.pack(side=tk.TOP, padx=4, pady=8)
    #
    return btn

class Actions:
  kernel = None
  view = None

  subs = []

  def __init__(self, kernel, view):
    self.kernel = kernel
    self.view = view
  
  def subscribe(self, sub):
    self.subs.append(sub)

  def load(self):
    path = tkFileDialog.askopenfilename(
      filetypes=[('BMP', '*.bmp'), ('PNG', '*.png')])
    if path:
      self.notify('load')
      #
      self.kernel.image.load(path)
      #
      self.kernel.image.show(self.view.axes)
      self.view.redraw()
      #
      self.view.toolbar.set_message('Image is loaded')
      #self.view.toolbar.set_message('Image isn\'t loaded')
      #
      self.notify('loaded')

  def select(self):
    self.notify('select')
    self.view.create_selector(callback=self.kernel.image.crop)
    self.notify('selected')

  def compress(self):
    self.notify('compress')
    #
    try:
      tic = time.time()
      self.kernel.compress()
      toc = time.time() - tic
    except MemoryError:
      tkMessageBox.showerror('Not enough memory',
                             'Please select a smaller fragment of the image')
      self.view.toolbar.set_message('Image isn\'t compressed')
      return
    #
    print '\n{0:.2f} sec. ({1:.2f} min.) has elapsed'.format(toc, toc / 60)
    self.view.toolbar.set_message('Image is compressed')
    #
    self.notify('compressed')
    #
    path = tkFileDialog.asksaveasfilename(defaultextension='.fpac',
                                          filetypes=[('FPAC', '*.fpac')])
    if path:
      self.kernel.fpac.save(path)
    self.view.toolbar.set_message('Compressed image is saved')

  def decompress(self):
    print 'Decompress'

  def notify(self, type):
    if type == 'compress':
      for sub in self.subs:
        sub.action_compress()
