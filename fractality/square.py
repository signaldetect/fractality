# ~coding: utf-8~

import numpy

class Transform:
  ''' Типы преобразования '''

  data = None

  def __init__(self, src):
    self.data = src.data

  def none(self):
    # Без преобразования
    return self.data

  def fliplr(self):
    # Отражение слева на право
    return self.data[:, -1 : : -1]

  def flipud(self):
    # Отражение сверху вниз
    return self.data[-1 : : -1, :]

  def rot90(self):
    # Поворот на 90
    return numpy.rot90(self.data)

  def rot180(self):
    # Поворот на 180
    return numpy.rot90(self.data, 2)

  def rot270(self):
    # Поворот на 270
    return numpy.rot90(self.data, 3)

  def trans(self):
    # Отражение от главной диагонали (транспонирование)
    return self.data.transpose()

  def ttrans(self):
    # Отражение от побочной диагонали
    return numpy.rot90(self.data, 3)[-1 : : -1, :]

class Square:
  data = None
  size = 0

  buf_size = 0.0
  summa = 0
  div = 0
  mean = 0.0
  rms = 0.0

  def __init__(self):
    pass

  def update(self):
    if self.data == None:
      return
    data = numpy.int32(self.data)
    #
    self.buf_size = b = float(self.data.size)
    # Расчет суммы элементов
    self.summa = s = numpy.sum(self.data)
    # Делимое для расчёта яркости
    self.div = numpy.sum(data * data) * int(b) - s * s
    # Среднее значение
    self.mean = m = s / b
    # Расчет отклонения от среднего значения
    self.rms = numpy.sum((data - m) ** 2) / b

  def fill_data(self, src, i, j, size):
    '''
      Запонение данными из источника
    '''
    self.data = src[i : (i + size), j : (j + size)].copy()
    self.size = size
    self.update()

  def fill_data_scale(self, src, i, j, size, scale):
    '''
      Запонение данными из источника c масштабированием
    '''
    n = scale * size
    self.data = src[i : (i + n) : scale, j : (j + n) : scale].copy()
    self.size = size
    self.update()

  def clone(self, data):
    '''
      Копирование после выполнения афинного преобразования
    '''
    self.data = data.copy()
    self.size = data.shape[0]
    self.update()

  def calc_uv(self, other):
    if other.div == 0:
      u = 0.0
      v = other.mean
    else:
      n = self.buf_size
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
    self.data = data[i : (i + self.size), j : (j + self.size)].copy()
    self.update()

  def calc_distance(self, data):
    return numpy.sum((numpy.int32(self.data) - numpy.int32(data)) ** 2) / self.buf_size
