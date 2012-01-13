# ~coding: utf-8~

import time
import tkMessageBox

from fractality.packer import Compressor, Decompressor
from gui.view import View

class Central:
  kernel = None
  view = None

  fpac_path = None
  pac = None

  def __init__(self):
    self.kernel = Compressor()
    self.view = View()

  def run(self):
    self.view.actions.subscribe(self)
    self.view.info.subscribe(self)
    #
    self.kernel.subscribe(self.view.actions)
    self.kernel.subscribe(self.view.info)
    self.kernel.subscribe(self.view.props)
    #
    self.view.run()

  def load_invoked(self, path):
    self.kernel.image.load(path)
    self.kernel.image.show(self.view.graph.axes)
    self.view.graph.redraw()
    #
    self.view.info.send('Image is loaded')
    #self.view.info.send('Image isn\'t loaded')

  def select_invoked(self):
    self.view.graph.create_selector(callback=self.kernel.image.crop)

  def compress_invoked(self):
    try:
      tic = time.time()
      self.kernel.run()
      toc = time.time() - tic
    except MemoryError:
      tkMessageBox.showerror('Not enough memory',
                             'Please select a smaller fragment of the image')
      self.view.info.send('Image isn\'t compressed')
      return
    #
    self.view.info.send('{0:.2f} sec. ({1:.2f} min.) has elapsed'.format(toc, toc / 60))
    c = self.kernel.fpac.compression(self.kernel.image)
    self.view.info.send('Compression: {0:.2f}%'.format(c))

  def save_invoked(self, path):
    self.fpac_path = path
    self.kernel.fpac.save(path)
    self.view.info.send('Compressed image is saved')

  def decompress_invoked(self):
    if self.fpac_path == None:
      return
    #
    self.pac = Decompressor()
    self.pac.fpac.load(self.fpac_path)
    #
    tic = time.time()
    self.pac.run()
    toc = time.time() - tic
    #
    self.view.info.send('Image is reconstructed')
    self.view.info.send('{0:.2f} sec. ({1:.2f} min.) has elapsed'.format(toc, toc / 60))
    #
    (width, height) = self.kernel.option.fix_image_size(self.pac.image)
    (width, height) = self.kernel.option.fix_image_size(self.kernel.image)
    rms = self.kernel.image.rmsdiff(self.pac.image)
    self.view.info.send('RMS error between source and reconstructed image:')
    self.view.info.send('{0:.2f}%'.format(rms))

  def resave_invoked(self, path):
    self.pac.image.save(path)
    self.view.info.send('Decompressed image is saved')

  def progress_stopped(self):
    self.kernel.is_process = False
