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
    '''
      :param squares:
    '''
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

class Square:
  data = None
  size = 0

  area = 0.0
  summa = 0
  div = 0
  mean = 0.0
  rms = 0.0

  def __init__(self):
    pass

  def update(self):
    '''
    '''
    if self.data == None:
      return
    data = numpy.int32(self.data)
    # Number of elements in square
    self.area = a = float(self.data.size)
    # Расчет суммы элементов
    #self.summa = s = numpy.sum(self.data)
    # Делимое для расчёта яркости
    #self.div = numpy.sum(data * data) * int(a) - s * s
    # Среднее значение
    #self.mean = m = s / a
    # Расчет отклонения от среднего значения
    #self.rms = numpy.sum((data - m) ** 2) / a

  def fill_data(self, src, i, j, size):
    '''
      Запонение данными из источника
      :param src: источник данных
      :param i: начало данных в источнике (номер строки)
      :param j: начало данных в источнике (номер столбца)
      :param size: размер данных
    '''
    self.data = src[i : (i + size), j : (j + size)].copy()
    self.size = size
    self.update()

  def fill_data_scale(self, src, i, j, size, scale):
    '''
      Запонение данными из источника c масштабированием
      :param src: источник данных
      :param i: начало данных в источнике (номер строки)
      :param j: начало данных в источнике (номер столбца)
      :param size: размер данных
      :param scale: величина масштабирования
    '''
    n = scale * size
    self.data = src[i : (i + n) : scale, j : (j + n) : scale].copy()
    self.size = size
    self.update()

  def clone(self, other, t):
    '''
      Копирование с выполнением афинного преобразования
      :param data:
    '''
    if t == 0: # none
      # Без преобразования
      self.data = other.data.copy()
    elif t == 1: # fliplr
      # Отражение слева на право
      self.data = other.data[:, -1 : : -1].copy()
    elif t == 2: # flipud
      # Отражение сверху вниз
      self.data = other.data[-1 : : -1, :].copy()
    elif t == 3: # rot90
      # Поворот на 90
      self.data = numpy.rot90(other.data).copy()
    elif t == 4: # rot180
      # Поворот на 180
      self.data = numpy.rot90(other.data, 2).copy()
    elif t == 5: # rot270
      # Поворот на 270
      self.data = numpy.rot90(other.data, 3).copy()
    elif t == 6: # trans
      # Отражение от главной диагонали (транспонирование)
      self.data = other.data.transpose().copy()
    elif t == 7: # ttrans
      # Отражение от побочной диагонали
      self.data = numpy.rot90(other.data, 3)[-1 : : -1, :].copy()
    #
    self.size = other.data.shape[0]
    self.update()

  def calc_uv(self, other):
    '''
      :param other:
    '''
    if other.div == 0:
      u = 0.0
      v = other.mean
    else:
      n = self.area
      s1 = self.summa
      s2 = other.summa
      #
      s = numpy.sum(numpy.int32(self.data) * numpy.int32(other.data))
      u = (n * s - s2 * s1) / other.div
      v = (s1 - s2 * u) / n
    #
    min_u = 0.0
    max_u = 3.0
    min_v = -255.0
    max_v = 255.0
    #
    if (u > max_u) or (u < min_u) or (v > max_v) or (v < min_v):
      stat = False
    else:
      stat = True
    #
    return (stat, u, v)

  def bright_transform(self, u, v):
    '''
      :param u:
      :param v:
    '''
    val = numpy.double(self.data) * u + v
    #
    (i, j) = numpy.nonzero(val > 255.0)
    val[i, j] = 255.0
    #
    (i, j) = numpy.nonzero(val < 0.0)
    val[i, j] = 0.0
    #
    return numpy.uint8(val)

  def flush_data(self, data, i, j):
    '''
      :param data:
      :param i:
      :param j:
    '''
    data[i : (i + self.size), j : (j + self.size)] = self.data.copy()

  def calc_distance(self, data):
    '''
      :param data:
    '''
    return numpy.sum((numpy.int32(self.data) - numpy.int32(data)) ** 2
                    ) / self.area

  def clear(self):
    if self.data != None:
      del self.data
      self.size = 0

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

  def compare_fe(self, other):
    (u, v, stat) = other.calc_uv(self)
    #
    m = u.shape[0] # number of ranks
    dmap = numpy.uint8(numpy.tile(self.data, (m, 1, 1)))
    #
    eps = other.calc_distance(dmap)
    #
    return (u, v, eps, stat)

  def compare_pearson(self, other):
    (u, v, stat) = other.calc_uv(self)
    bmap = self.calc_bright_map(u, v)
    eps = other.calc_distance(bmap)
    #
    return (u, v, eps, stat)

  def compare_entropy(self, other):
    (u, v, stat) = other.calc_uv(self)
    #
    n = u.shape[1] # number of domains
    m = u.shape[0] # number of ranks
    #
    emap = numpy.uint8(numpy.tile(self.data, (m, 1, 1)))
    emap = numpy.double(emap) * numpy.log2(u.reshape((m, n, 1)))
    #
    eps = other.calc_distance(emap)
    #
    return (u, v, eps, stat)

  def compare_nonlinear(self, other):
    pass

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
    a = numpy.arange(0, n, size
                    ) + numpy.tile(numpy.arange(0, m, h), (num_x, 1)
                                  ).reshape((1, k), order='F')
    #
    n = size * size
    h = width - size
    m = (size - 1) * h + 1
    b = numpy.arange(n) + numpy.tile(numpy.arange(0, m, h), (size, 1)
                                    ).reshape((1, n), order='F')
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
    a = numpy.arange(0, n, step
                    ) + numpy.tile(numpy.arange(0, m, h), (num_x, 1)
                                  ).reshape((1, k), order='F')
    #
    n = scale * size * size - 1
    h = scale * (width - size)
    m = (size - 1) * h + 1
    b = numpy.arange(0, n, scale
                    ) + numpy.tile(numpy.arange(0, m, h), (size, 1)
                                  ).reshape((1, size * size), order='F')
    #
    idx = numpy.tile(b, (k, 1)) + a.transpose()
    (i, j) = numpy.unravel_index(idx, (height, width))
    #
    super(Domains, self).setup(data[i, j], size)
