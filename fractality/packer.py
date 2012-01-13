# ~coding: utf-8~

#import pdb

import numpy
import sys

from image import SrcImage, PacImage
from option import PacOption
from square import Ranks, Domains

class UnPacker:
  '''
  Example:
    pac = UnPacker()
    pac.fpac.load('file.jpg')
    pac.decompress()
    pac.image.save('file.fpac')
  '''

  image = SrcImage()
  option = PacOption()
  fpac = PacImage()

  quick_eps = 0.0
  doms_x = 0
  doms_y = 0
  dom_bit_x = 0
  dom_bit_y = 0

  ranks = None
  proc_ranks_idx = None

  def __init__(self):
    self.fpac.option = self.option

  def decompress(self):
    '''
    '''
#    pdb.set_trace()
    self.option = self.fpac.option
    (width, height) = (self.option.width, self.option.height)
    size = self.option.rank_size
    # Кол-во доменов, умещающихся по горизонтали и вертикали
    self.doms_x = (width - 2 * size) / self.option.dom_step + 1
    self.doms_y = (height - 2 * size) / self.option.dom_step + 1
    # Кол-во бит, необходимых для хранения каждой из координат
    self.dom_bit_x = numpy.uint8(numpy.ceil(numpy.log2(self.doms_x)))
    self.dom_bit_y = numpy.uint8(numpy.ceil(numpy.log2(self.doms_y)))
    #
    self.image.mx = numpy.empty((height, width, 3))
    for c in xrange(3):
      mx = self.image.mx[:, :, c]

  def fill_domain(self, doms, size):
    '''
    '''
    opr = self.fpac.get_bits(2)
    temp = Domain()
    dom.clear()
    dom.area = size * size
    dom.size = size
    dom.data = numpy.zeros((size, size))
    #
    if opr == 0:
      if size == 2:
        dom.data[0, 0] = self.fpac.get_bits(8)
        dom.data[0, 1] = self.fpac.get_bits(8)
        dom.data[1, 0] = self.fpac.get_bits(8)
        dom.data[1, 1] = self.fpac.get_bits(8)
      else:
        temp = fill_domain(dom.size / 2)
        temp.flush_data(dom.data, dom.size, 0, 0)
        #
        temp = fill_domain(dom.size / 2)
        temp.flush_data(dom.data, dom.size, 0, dom.size / 2)
        #
        temp = fill_domain(dom.size / 2)
        temp.flush_data(dom.data, dom.size, dom.size / 2, 0)
        #
        temp = fill_domain(dom.size / 2)
        temp.flush_data(dom.data, dom.size, dom.size / 2, dom.size / 2)
    elif opr == 1:
      dom_y = self.fpac.get_bits(self.dom_bit_y)
      dom_x = self.fpac.get_bits(self.dom_bit_x)
      #
      t = self.fpac.get_bits(3)
      u = self.fpac.get_bits(7)
      u = u / 127.0 / 3.3 * 10.0
      bit = self.fpac.get_bits(1)
      v = self.fpac.get_bits(8)
      if bit:
        v *= -1
      #
      step = self.option.dom_step
      temp.fill_data_scale(temp_data, self.option.width,
                           dom_x * step, dom_y * step, size, 2)
      dom.clone(temp, t)
      dom.bright_transform(dom, u, v)
    elif opr == 2:
      bright = self.fpac.get_bits(8)
      dom.data = numpy.ones((size, size)) * bright
    else:
      return False
    #
    return True
