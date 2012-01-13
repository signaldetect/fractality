# ~coding: utf-8~

#import pdb

import numpy
import sys

from image import SrcImage, PckImage
from option import PckOption
from square import Square, Transform

class Packer:
  '''
  Example:
    pck = Packer()
    pck.image.load('file.jpg')
    pck.option.rank_size = 8
    pck.option.dom_step = 4
    pck.option.find_best_dom = True
    pck.compress(eps=0.005)
    pck.fpck.save('file.fpck')

  Parameters:
    eps  точность (максимальное СКО)
    rank_size  размер ранговой области
    dom_step  шаг поиска домена
    find_best_dom  True - искать лучший домен, False - искать домен удовлетворяющий макс. СКО
  '''

  image = SrcImage()
  option = PckOption()
  fpck = PckImage()

  quick_eps = 0.0
  cur_layer = 0
  doms_x = 0
  doms_y = 0
  dom_bit_x = 0
  dom_bit_y = 0
  doms = None

  def __init__(self):
    self.fpck.option = self.option

  def compress(self, eps):
    '''
      :param eps: Точность (максимальное СКО)
    '''
#    pdb.set_trace()
    (width, height) = self.option.fix_image_size(self.image)
    self.fpck.setup()
    #
    size = self.option.rank_size
    #
    eps *= 256
    self.quick_eps = eps * eps * size * size
    # Кол-во доменов, умещающихся по горизонтали и вертикали
    self.doms_x = (width - 2 * size) / self.option.dom_step + 1
    self.doms_y = (height - 2 * size) / self.option.dom_step + 1
    # Кол-во бит, необходимых для хранения каждой из координат
    self.dom_bit_x = numpy.uint8(numpy.ceil(numpy.log2(self.doms_x)))
    self.dom_bit_y = numpy.uint8(numpy.ceil(numpy.log2(self.doms_y)))
    #
    dom_group = numpy.ceil(numpy.log2(size))
    self.doms = numpy.empty((self.doms_y, self.doms_x, dom_group), dtype=object)
    #
    rank = Square()
    # Кол-во рангов
    nrank = 3 * width * height / (size * size)
    n = 0
    process = 0.0
    #
    c = 0
    while c < 3:
      self.cur_layer = c
      data = self.cur_color_map()
      #
      x = 0
      while x < width:
        y = 0
        while y < height:
          rank.fill_data(data, y, x, size)
          self.calc_for_rank(rank, 0)
          #
          n += 1
          process += rank.buf_size
          #
          part = float(n) / nrank
          sys.stdout.write('Complete {0:3.2f}%, compress {1:3.2f}%\t\r'.format(
            100.0 * part, 100.0 * (self.fpck.cur_bit / 8.0) / process))
          #
          y += size
        #
        x += size
      #
      c += 1
    #
    del self.doms

  def cur_color_map(self):
    '''
    '''
    return self.image.mx[:, :, self.cur_layer]

  def calc_for_rank(self, rank, level):
    '''
      :param rank:
      :param level:
    '''
    level += 1
    #
    if rank.rms == 0:
      self.fpck.add_bits(2, 2)
      self.fpck.add_bits(8, rank.mean)
      #
      print '\n-- 2 --'
      return level - 1
    #
    ranks = []
    ranks.append(rank)
    ranks.extend(Square() for i in xrange(7))
    #
    trans = Transform(rank)
    ranks[1].clone(trans.fliplr())
    ranks[2].clone(trans.flipud())
    ranks[3].clone(trans.rot90())
    ranks[4].clone(trans.rot180())
    ranks[5].clone(trans.rot270())
    ranks[6].clone(trans.trans())
    ranks[7].clone(trans.ttrans())
    #
    best_rms = self.quick_eps + 1000.0
    best_u = 0.0
    best_v = 0.0
    best_t = 0
    best_x = 0
    best_y = 0
    #
    j = 0
    while j < self.doms_x:
      i = 0
      while i < self.doms_y:
        dom = self.get_domain(i, j, rank.size, level - 1)
        #
        t = 0
        while t < 8:
          (stat, u, v) = ranks[t].calc_uv(dom)
          if not stat:
            t += 1
            continue
          #
          data = dom.bright_transform(u, v)
          eps = ranks[t].calc_distance(data)
          #
          if self.option.find_best_dom:
            if eps < best_rms:
              best_rms = eps
              best_u = u
              best_v = v
              best_t = t
              best_x = j
              best_y = i
          elif eps <= self.quick_eps:
            self.fpck.add_bits(2, 1)
            self.fpck.add_bits(self.dom_bit_y, i)
            self.fpck.add_bits(self.dom_bit_x, j)
            #
            if t == 3:   # rot90
              real_t = 5 # rot270
            elif t == 5: # rot270
              real_t = 3 # rot90
            else:
              real_t = t
            #
            self.fpck.add_bits(3, real_t)
            self.fpck.add_bits(7, int(u * 3.3 / 10.0 * 127.0))
            #
            '''
            if v < 0:
              self.fpck.add_bits(1, 1)
              self.fpck.add_bits(8, -v)
            else:
              self.fpck.add_bits(1, 0)
              self.fpck.add_bits(8, v)
            '''
            self.fpck.add_bits(1, int(v < 0))
            self.fpck.add_bits(8, int((-1 + 2 * int(v >= 0)) * v))
            #
            return level - 1
          #
          t += 1
        #
        i += 1
      #
      j += 1
    #
    if self.option.find_best_dom and (best_rms <= self.quick_eps):
      self.fpck.add_bits(2, 1)
      self.fpck.add_bits(self.dom_bit_y, best_y)
      self.fpck.add_bits(self.dom_bit_x, best_x)
      #
      if best_t == 3:   # rot90
        best_t = 5      # rot270
      elif best_t == 5: # rot270
        best_t = 3      # rot90
      #
      self.fpck.add_bits(3, best_t)
      self.fpck.add_bits(7, int(best_u * 3.3 / 10.0 * 127.0))
      #
      '''
      if best_v < 0:
        self.fpck.add_bits(1, 1)
        self.fpck.add_bits(8, -best_v)
      else:
        self.fpck.add_bits(1, 0)
        self.fpck.add_bits(8, best_v)
      '''
      self.fpck.add_bits(1, int(best_v < 0))
      self.fpck.add_bits(8, int((-1 + 2 * int(best_v >= 0)) * best_v))
      #
      return level - 1
    #
    self.fpck.add_bits(2, 0)
    #
    n = rank.size
    if n > 2:
      sub_rank = Square()
      data = rank.data
      m = n / 2
      #
      sub_rank.fill_data(data, 0, 0, m)
      level = self.calc_for_rank(sub_rank, level)
      #
      sub_rank.fill_data(data, m, 0, m)
      level = self.calc_for_rank(sub_rank, level)
      #
      sub_rank.fill_data(data, 0, m, m)
      level = self.calc_for_rank(sub_rank, level)
      #
      sub_rank.fill_data(data, m, m, m)
      level = self.calc_for_rank(sub_rank, level)
    else:
      cur_bit = self.fpck.cur_bit
      #
      self.fpck.add_bits(8, rank.data[0, 0])
      self.fpck.add_bits(8, rank.data[1, 0])
      self.fpck.add_bits(8, rank.data[0, 1])
      self.fpck.add_bits(8, rank.data[1, 1])
      #
      if (self.fpck.cur_bit - cur_bit) > rank.buf_size:
        print '\n-- Low --'
    #
    return level - 1

  def get_domain(self, i, j, size, level):
    '''
      :param i:
      :param j:
      :param size:
      :param level:
    '''
    dom = self.doms[i, j, level]
    #
    if dom == None:
      y = i * self.option.dom_step
      x = j * self.option.dom_step
      #
      dom = Square()
      dom.fill_data_scale(self.cur_color_map(), y, x, size, 2)
      self.doms[i, j, level] = dom
    #
    return dom
