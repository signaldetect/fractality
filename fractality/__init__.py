# ~coding: utf-8~

#import pdb

import numpy
import sys

from image import SrcImage, PacImage
from option import PacOption
from square import Ranks, Domains

class Packer:
  '''
  Example:
    pac = Packer()
    pac.image.load('file.jpg')
    pac.option.rank_size = 8
    pac.option.dom_step = 4
    pac.option.find_best_dom = True
    pac.option.eps=0.005
    pac.compress()
    pac.fpac.save('file.fpac')

  Parameters:
    rank_size -- размер ранговой области
    dom_step -- шаг поиска домена
    find_best_dom -- True - искать лучший домен,
                     False - искать домен удовлетворяющий макс. СКО
    eps -- точность (максимальное СКО)
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

  def compress(self):
    '''
    '''
#    pdb.set_trace()
    (width, height) = self.option.fix_image_size(self.image)
    self.fpac.setup()
    #
    size = self.option.rank_size
    #
    eps = self.option.eps * 256
    self.quick_eps = eps * eps * size * size
    # Кол-во доменов, умещающихся по горизонтали и вертикали
    self.doms_x = (width - 2 * size) / self.option.dom_step + 1
    self.doms_y = (height - 2 * size) / self.option.dom_step + 1
    # Кол-во бит, необходимых для хранения каждой из координат
    self.dom_bit_x = numpy.uint8(numpy.ceil(numpy.log2(self.doms_x)))
    self.dom_bit_y = numpy.uint8(numpy.ceil(numpy.log2(self.doms_y)))
    #
    m = 3.0 * numpy.ceil(numpy.log2(size))
    n = 0.0
    for c in xrange(3):
      mx = self.image.mx[:, :, c]
      size = self.option.rank_size
      #
      self.proc_ranks_idx = numpy.array([], dtype=int)
      self.fpac.start_rec()
      #
      while size >= 2:
        self.process(mx, size)
        #
        r = numpy.arange(self.ranks.count)
        r = numpy.setdiff1d(r, self.proc_ranks_idx)
        #
        if size > 2:
          for i in r:
            self.fpac.rec_bits(i, 2, 0)
        else:
          for i in r:
            self.fpac.rec_bits(i, 2, 0)
            #
            for j in xrange(4):
              # -- Low --
              self.fpac.rec_bits(i, 8, self.ranks.data[i, j])
        #
        size /= 2
        self.fpac.next_level()
        #
        n += 1.0
        sys.stdout.write('\nComplete {0:3.2f}%\t\n'.format(100.0 * n / m))
      #
      self.fpac.flush_bits(width)

  def process(self, mx, size):
    # Init ranks
    ranks = self.ranks = Ranks()
    ranks.setup(mx, size)
    # Init domains
    doms = Domains()
    doms.setup(mx, size, self.option.dom_step, scale=2)
    #
    n = ranks.count
    m = doms.count
    #
    u = numpy.empty((8, n, m))
    v = numpy.empty((8, n, m))
    eps = numpy.empty((8, n, m))
    stat = numpy.empty((8, n, m), dtype=bool)
    #
    (u[0], v[0], eps[0], stat[0]) = doms.compare(ranks)
    (u[1], v[1], eps[1], stat[1]) = doms.compare(ranks.trans.fliplr())
    (u[2], v[2], eps[2], stat[2]) = doms.compare(ranks.trans.flipud())
    (u[3], v[3], eps[3], stat[3]) = doms.compare(ranks.trans.rot90())
    (u[4], v[4], eps[4], stat[4]) = doms.compare(ranks.trans.rot180())
    (u[5], v[5], eps[5], stat[5]) = doms.compare(ranks.trans.rot270())
    (u[6], v[6], eps[6], stat[6]) = doms.compare(ranks.trans.trans())
    (u[7], v[7], eps[7], stat[7]) = doms.compare(ranks.trans.ttrans())
    # Skip some ranks
    xi = self.skiped_ranks()
    if xi.size > 0:
      stat[:, xi, :] = False
      self.proc_ranks(xi)
    # Check RMS
    idx = numpy.nonzero(ranks.rms == 0.0)[0]
    if idx.size > 0:
      idx = numpy.setdiff1d(idx, xi)
      #
      stat[:, idx, :] = False
      self.proc_ranks(idx)
      #
      for i in idx:
        # -- 2 --
        self.fpac.rec_bits(i, 2, 2)
        self.fpac.rec_bits(i, 8, ranks.mean[i])
    #
    (t, i, j) = numpy.nonzero(numpy.invert(stat))
    eps[t, i, j] = eps.max() + 1.0
    #
    if self.option.find_best_dom:
      t = eps.min(axis=2).argmin(axis=0)
      i = numpy.arange(n) # ranks
      j = eps.argmin(axis=2)[t, i] # domains
      # For every rank...
      best_rms = eps[t, i, j]
      best_u = u[t, i, j]
      best_v = v[t, i, j]
      best_t = t
      (best_x, best_y) = doms.coord(j)
      #
      idx = numpy.nonzero(best_rms <= self.quick_eps)[0]
      if idx.size > 0:
        self.save_doms(i[idx], best_u[idx], best_v[idx],
                       best_t[idx], best_x[idx], best_y[idx])
        self.proc_ranks(i[idx])
    else:
      (t, i, j) = numpy.nonzero(eps <= self.quick_eps)
      if t.size > 0:
        (val, idx) = numpy.unique(i, return_index=True)
        #
        (t, i, j) = (t[idx], i[idx], j[idx])
        (x, y) = doms.coord(j)
        #
        self.save_doms(i, u[t, i, j], v[t, i, j], t, x, y)
        self.proc_ranks(i)

  def proc_ranks(self, idx):
    '''
      Set current ranks as processed
    '''
    self.proc_ranks_idx = numpy.append(self.proc_ranks_idx, idx)

  def skiped_ranks(self):
    '''
      Get skiped ranks indexes
    '''
    idx = self.proc_ranks_idx
    if idx.size > 0:
      self.proc_ranks_idx = numpy.array([], dtype=int)
      #
      n = self.ranks.count_x / 2
      m = idx.size
      #
      y = idx / n
      x = idx % n
      #
      idx = numpy.zeros((4, m), dtype=int)
      idx[0, :] = y * n * 4 + x * 2
      idx[1, :] = idx[0, :] + 1
      idx[2, :] = idx[0, :] + n * 2
      idx[3, :] = idx[2, :] + 1
      #
      idx = idx.reshape(m * 4, order='F')
    #
    return idx

  def save_doms(self, r, u, v, t, x, y):
    i = numpy.nonzero(t == 3)[0] # if rot90
    j = numpy.nonzero(t == 5)[0] # if rot270
    t[i] = 5 # --> rot270
    t[j] = 3 # --> rot90
    #
    for i in xrange(r.size):
      self.fpac.rec_bits(r[i], 2, 1)
      self.fpac.rec_bits(r[i], self.dom_bit_y, y[i])
      self.fpac.rec_bits(r[i], self.dom_bit_x, x[i])
      #
      self.fpac.rec_bits(r[i], 3, t[i])
      self.fpac.rec_bits(r[i], 7, numpy.int32(u[i] * 3.3 / 10.0 * 127.0))
      #
      self.fpac.rec_bits(r[i], 1, numpy.int32(v[i] < 0.0))
      self.fpac.rec_bits(r[i], 8, numpy.int32((-1.0 + 2.0 * numpy.float32(v[i] >= 0)) * v[i]))
