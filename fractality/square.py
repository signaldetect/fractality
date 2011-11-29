# ~coding: utf-8~

import numpy

class Transform:
  _prim = None # object of class Squares
  _mod = None # object of class Squares

  ''' Типы преобразования '''
  _none = None # без преобразования
  _fliplr = None # отражение слева на право
  _flipud = None # отражение сверху вниз
  _rot90 = None # поворот на 90
  _rot180 = None # поворот на 180
  _rot270 = None # поворот на 270
  _trans = None # отражение от главной диагонали (транспонирование)
  _ttrans = None # отражение от побочной диагонали

  def __init__(self, squares):
    self._prim = squares
    self._mod = squares.clone()
    size = squares.size
    #
    n = size * size
    self._none = numpy.arange(n)
    idx = self._none.reshape((size, size))
    # Отражение слева на право
    self._fliplr = idx[:, -1 : : -1].reshape(n)
    # Отражение сверху вниз
    self._flipud = idx[-1 : : -1, :].reshape(n)
    # Поворот на 90
    self._rot90 = numpy.rot90(idx).reshape(n)
    # Поворот на 180
    self._rot180 = numpy.rot90(idx, 2).reshape(n)
    # Поворот на 270
    self._rot270 = numpy.rot90(idx, 3).reshape(n)
    # Отражение от главной диагонали (транспонирование)
    self._trans = idx.transpose().reshape(n)
    # Отражение от побочной диагонали
    self._ttrans = numpy.rot90(idx, 3)[-1 : : -1, :].reshape(n)

  def none(self):
    self._mod.data = self._prim.data[:, self._none]
    return self._mod

  def fliplr(self):
    self._mod.data = self._prim.data[:, self._fliplr]
    return self._mod

  def flipud(self):
    self._mod.data = self._prim.data[:, self._flipud]
    return self._mod

  def rot90(self):
    self._mod.data = self._prim.data[:, self._rot90]
    return self._mod

  def rot180(self):
    self._mod.data = self._prim.data[:, self._rot180]
    return self._mod

  def rot270(self):
    self._mod.data = self._prim.data[:, self._rot270]
    return self._mod

  def trans(self):
    self._mod.data = self._prim.data[:, self._trans]
    return self._mod

  def ttrans(self):
    self._mod.data = self._prim.data[:, self._ttrans]
    return self._mod

class Squares(object):
  data = None
  size = 0

  count = 0
  count_x = 0
  count_y = 0

  area = 0.0
  summa = None
  div = None
  mean = None
  rms = None

  trans = None

  def __init__(self):
    pass

  def setup(self, data, size):
    self.data = data
    self.size = size
    #
    self.update()
    self.trans = Transform(self)

  def update(self):
    if self.data == None:
      return
    data = numpy.int32(self.data)
    n = self.data.shape[0]
    # Number of squares
    self.count = self.data.shape[0]
    # Number of elements in square
    self.area = a = float(self.data.shape[1])
    # Расчет суммы элементов
    self.summa = s = numpy.sum(self.data, axis=1)
    # Делимое для расчёта яркости
    self.div = numpy.sum(data * data, axis=1) * int(a) - s * s
    # Среднее значение
    self.mean = m = s / int(a)
    # Расчет отклонения от среднего значения
    self.rms = numpy.sum((data - m.reshape((n, 1))) ** 2, axis=1) / a

  def clone(self):
    other = Squares()
    #
    other.data = self.data.copy()
    other.size = self.size
    other.count_x = self.count_x
    other.count_y = self.count_y
    #
    other.update()
    other.trans = self.trans
    #
    return other

  def coord(self, ids):
    (y, x) = numpy.unravel_index(ids, (self.count_y, self.count_x))
    return (x, y)

  def compare(self, other):
    (u, v, stat) = other.calc_uv(self)
    bmap = self.calc_bright_map(u, v)
    eps = other.calc_distance(bmap)
    #
    return (u, v, eps, stat)

  def calc_uv(self, other):
    n = self.data.shape[0]
    m = other.data.shape[0]
    #
    u = numpy.zeros((n, m), dtype=float)
    v = numpy.zeros((n, m), dtype=float)
    stat = numpy.zeros((n, m), dtype=bool)
    #
    ident = (other.div == 0)
    #
    idx = numpy.nonzero(ident)[0]
    if idx.size > 0:
      #u[:, idx] = 0.0
      v[:, idx] = other.mean[idx]
    #
    idx = numpy.nonzero(numpy.invert(ident))[0]
    if idx.size > 0:
      n = other.data.shape[1]
      m = idx.size
      #
      d1 = numpy.int32(self.data)
      d2 = numpy.int32(other.data[idx, :]).transpose().reshape((n, m))
      s = numpy.dot(d1, d2)
      #
      (n, m) = s.shape
      s1 = numpy.tile(self.summa.reshape((n, 1)), (1, m))
      s2 = numpy.tile(other.summa[idx], (n, 1))
      #
      a = self.area
      u[:, idx] = (a * s - s2 * s1) / other.div[idx]
      v[:, idx] = (s1 - s2 * u[:, idx]) / a
    #
    min_u = 0.0
    max_u = 3.0
    min_v = -255.0
    max_v = 255.0
    #
    out = ((u > max_u) + (u < min_u) + (v > max_v) + (v < min_v))
    #(i, j) = numpy.nonzero(out)
    #stat[i, j] = False
    (i, j) = numpy.nonzero(numpy.invert(out))
    stat[i, j] = True
    #
    return (u, v, stat)
  
  def calc_bright_map(self, u, v):
    n = u.shape[1] # number of domains
    m = u.shape[0] # number of ranks
    #
    bmap = numpy.tile(self.data, (m, 1, 1))
    bmap = numpy.double(bmap) * u.reshape((m, n, 1)) + v.reshape((m, n, 1))
    #
    (k, i, j) = numpy.nonzero(bmap > 255.0)
    bmap[k, i, j] = 255.0
    #
    (k, i, j) = numpy.nonzero(bmap < 0.0)
    bmap[k, i, j] = 0.0
    #
    return numpy.uint8(bmap)

  def calc_distance(self, bmap):
    n = self.count
    a = self.area
    #
    data = self.data.reshape((n, 1, a))
    return numpy.sum((numpy.int32(data) - numpy.int32(bmap)) ** 2, axis=2) / a

class Ranks(Squares):
  def __init__(self):
    pass

  def setup(self, data, size):
    (height, width) = data.shape
    self.count_x = num_x = width / size
    self.count_y = num_y = height / size
    #
    k = num_x * num_y
    #
    n = k * size - 1
    h = (size - 1) * width
    m = (num_y - 1) * h + 1
    a = numpy.arange(0, n, size) + numpy.tile(numpy.arange(0, m, h), (num_x, 1)).reshape((1, k), order='F')
    #
    n = size * size
    h = width - size
    m = (size - 1) * h + 1
    b = numpy.arange(n) + numpy.tile(numpy.arange(0, m, h), (size, 1)).reshape((1, n), order='F')
    #
    idx = numpy.tile(b, (k, 1)) + a.transpose()
    (i, j) = numpy.unravel_index(idx, (height, width))
    #
    super(Ranks, self).setup(data[i, j], size)

class Domains(Squares):
  def __init__(self):
    pass

  def setup(self, data, size, step, scale=1):
    (height, width) = data.shape
    self.count_x = num_x = (width - scale * size) / step + 1
    self.count_y = num_y = (height - scale * size) / step + 1
    #
    k = num_x * num_y
    #
    n = k * step - 1
    h = step * (width - num_x)
    m = (num_y - 1) * h + 1
    a = numpy.arange(0, n, step) + numpy.tile(numpy.arange(0, m, h), (num_x, 1)).reshape((1, k), order='F')
    #
    n = scale * size * size - 1
    h = scale * (width - size)
    m = (size - 1) * h + 1
    b = numpy.arange(0, n, scale) + numpy.tile(numpy.arange(0, m, h), (size, 1)).reshape((1, size * size), order='F')
    #
    idx = numpy.tile(b, (k, 1)) + a.transpose()
    (i, j) = numpy.unravel_index(idx, (height, width))
    #
    super(Domains, self).setup(data[i, j], size)
