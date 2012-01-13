# ~coding: utf-8~

import os
import Tkinter as tk
import tkFileDialog

from core.messaging import Publisher
from widget import TipButton
#from fractality.image import SrcImage

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

class ActionsSubscriber:
  def load_invoked(self, path):
    pass

  def select_invoked(self):
    pass
  
  def compress_invoked(self):
    pass

  def save_invoked(self, path):
    pass

  def decompress_invoked(self):
    pass

class Actions(Publisher):
  def __init__(self):
    Publisher.__init__(self)
  
  def load(self):
    path = tkFileDialog.askopenfilename(filetypes=[
      ('All Image Files',
       '*.bmp;*.jpg;*.jpeg;*.png;*.ppm;*.pbm;*.tif;*.tiff'),
      ('BMP', '*.bmp'), ('JPEG', '*.jpg;*.jpeg'), ('PNG', '*.png'),
      ('PPM', '*.ppm;*.pbm'), ('TIFF', '*.tif;*.tiff')])
    if path:
      self.notify('load_invoked', path=path)

  def select(self):
    self.notify('select_invoked')

  def compress(self):
    self.notify('compress_invoked')

  def decompress(self):
    self.notify('decompress_invoked')
    #
    path = tkFileDialog.asksaveasfilename(defaultextension='.bmp',
                                          filetypes=[
      ('BMP', '*.bmp'), ('JPEG', '*.jpg;*.jpeg'), ('PNG', '*.png'),
      ('PPM', '*.ppm;*.pbm'), ('TIFF', '*.tif;*.tiff')])
    if path:
      self.notify('resave_invoked', path=path)
    '''
    other = SrcImage()
    other.load('arthrosis.bmp')
    self.kernel.option.rank_size = 8
    (width, height) = self.kernel.option.fix_image_size(other)
    (width, height) = self.kernel.option.fix_image_size(self.kernel.image)
    rms = self.kernel.image.rmsdiff(other)
    print rms
    '''

  def compressed(self):
    path = tkFileDialog.asksaveasfilename(defaultextension='.fpac',
                                          filetypes=[('FPAC', '*.fpac')])
    if path:
      self.notify('save_invoked', path=path)
