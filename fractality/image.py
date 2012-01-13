# ~coding: utf-8~

from PIL import Image

import ImageChops
import numpy, struct, math, operator

class SrcImage:
  img = None
  mx = None

  def __init__(self):
    pass

  def create(self):
    mx = self.mx[-1 : : -1, :, :]
    w = mx.shape[1]
    h = mx.shape[0]
    #self.img = Image.frombuffer('RGB', (w, h), mx, 'raw', 'RGB', 0, 1)
    self.img = Image.fromstring('RGB', (w, h), mx.tostring(),
                                'raw', 'RGB', 0, 1)

  def load(self, file_path):
    '''
      :param file_path:
    '''
    try:
      self.img = Image.open(file_path)
    except IOError:
      print 'Bad file path: {0}'.format(file_path)
      return
    #
    self.img = self.img.convert('RGB')
    self.mx = numpy.array(self.img)[-1 : : -1, :, :]

  def save(self, file_path):
    '''
      :param file_path:
    '''
    try:
      self.img.save(file_path)
    except IOError:
      print 'Bad file path: {0}'.format(file_path)

  def show(self, axes=None):
    if axes:
      axes.cla()
      axes.imshow(numpy.asarray(self.img))
    else:
      self.img.show()

  def crop(self, x, y):
    box = (int(x[0]), int(y[0]), int(x[1]), int(y[1]))
    self.img = self.img.crop(box)
    #self.img.save('cropped.bmp')
    self.img.load()
    #
    self.mx = numpy.array(self.img)[-1 : : -1, :, :]

  def rmsdiff(self, other):
    '''
      Calculate the root-mean-square difference between two images
    '''
    im1 = self.img
    im2 = other.img
    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value * ((idx % 256) ** 2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    return math.sqrt(sum_of_squares / float(im1.size[0] * im1.size[1]))
    '''
    h1 = self.img.histogram()
    h2 = other.img.histogram()
    return math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
    '''
    '''
    im1 = self.img
    im2 = other.img
    #
    h = ImageChops.difference(im1, im2).histogram()
    # Calculate RMS
    #return math.sqrt(reduce(operator.add,
    #                        map(lambda h, i: h * (i**2), h, range(256))
    #                       ) / (float(im1.size[0]) * im1.size[1]))
    return math.sqrt(sum(h*(i**2) for i, h in enumerate(h)) / (float(im1.size[0]) * im1.size[1]))
    '''

class PacImage:
  option = None

  cur_level = 0
  levels = None

  cur_bit = 0
  out_buf = None

  def __init__(self):
    #self.fid = open('debug.dat', 'wt')
    pass

  def __del__(self):
    #self.fid.close()
    pass

  def setup(self):
    '''
    '''
    if self.option == None:
      return
    # Максимальный размер выходного буфера
    n = numpy.uint32(self.option.width * self.option.height * 3 * 1.2)
    # Выделение памяти под выходной буфер
    self.out_buf = numpy.zeros(n, dtype=numpy.uint16)
    self.cur_bit = 0

  def start_rec(self):
    '''
    '''
    size = self.option.rank_size
    n = int(numpy.ceil(numpy.log2(size)))
    #
    self.levels = list()
    for i in xrange(n):
      self.levels.append(dict())
    #
    self.cur_level = 0

  def next_level(self):
    '''
    '''
    self.cur_level += 1

  def rec_bits(self, r, b, val):
    '''
      :param r:
      :param b:
      :param val:
    '''
    #self.fid.write('{0}: {1}\t{2}\n'.format(r, b, val))
    i = self.cur_level
    if self.levels[i].has_key(r):
      self.levels[i][r] += [b, val]
    else:
      self.levels[i][r] = [b, val]

  def flush_bits(self, width):
    '''
      :param width:
    '''
    size = self.option.rank_size
    n = int(numpy.ceil(numpy.log2(size))) - 1
    #
    for i in xrange(n, 0, -1):
      num_x = width / (2 ** (abs(i - n) + 1))
      #
      for id in self.levels[i].keys():
        y = id / (2 * num_x)
        x = (id % num_x) / 2
        parent_id = (num_x / 2) * y + x
        #
        self.levels[i - 1][parent_id] += self.levels[i][id]
    #
    root = self.levels[0]
    del self.levels
    #
    for recs in root.values():
      for i in xrange(0, len(recs), 2):
        #self.txt_bits(recs[i], recs[i + 1])
        self.add_bits(recs[i], recs[i + 1])
    #
    del root

  def txt_bits(self, b, val):
    self.fid.write('{0}\t{1}\n'.format(b, val))

  def add_bits(self, b, val):
    '''
      :param b:
      :param val:
    '''
    nb = numpy.uint8(b) # bit8
    val = numpy.uint16(val) # bit16
    #
    num_word = numpy.uint32(self.cur_bit) # bit32
    nbit_on_word = numpy.uint8(num_word - ((num_word >> 4) << 4)) # bit8
    num_word = num_word >> 4
    nbit_on_sword = numpy.uint16(0) # bit16
    #
    rtail = 16 - numpy.int8(nbit_on_word + nb)
    if rtail < 0:
      nbit_on_sword = numpy.uint16(abs(rtail))
    #
    left_p = numpy.uint16(((val >> nbit_on_sword) << (16 - (nb - nbit_on_sword))) >> nbit_on_word) # bit16
    right_p = numpy.uint16(val << (16 - nbit_on_sword)) # bit16
    #
    self.out_buf[num_word] += left_p
    self.out_buf[num_word + 1] = ((self.out_buf[num_word + 1] >> nbit_on_sword) << nbit_on_sword) + right_p
    #
    self.cur_bit += b

  def get_bits(self, b):
    nb = numpy.uint8(b) # bit8
    #
    num_word = numpy.uint32(self.cur_bit) # bit32
    nbit_on_word = numpy.uint8(num_word - ((num_word >> 4) << 4)) # bit8
    num_word = num_word >> 4
    nbit_on_sword = numpy.uint8(0) # bit8
    #
    rtail = 16 - numpy.int8(nbit_on_word + nb)
    if rtail < 0:
      nbit_on_sword = numpy.uint8(abs(rtail))
      rtail = 0
    #
    if num_word < len(self.out_buf):
      left_p = numpy.uint16((self.out_buf[num_word] << nbit_on_word) >> (nbit_on_word + rtail)) # bit16
    else:
      left_p = numpy.uint16(0)
    if (num_word + 1) < len(self.out_buf):
      right_p = numpy.uint16(self.out_buf[num_word + 1] >> (16 - nbit_on_sword)) # bit16
    else:
      right_p = numpy.uint16(0)
    #
    left_p <<= nbit_on_sword
    #
    self.cur_bit += b
    return left_p + right_p

  def compression(self, src_image):
    bsize = float(src_image.mx.size)
    csize = numpy.uint32(numpy.ceil(self.cur_bit / 8.0))
    return 100.0 * csize / bsize

  def save(self, file_name):
    '''
      Save data to a binary file and flush output buffer
      :param file_name:
    '''
    # Start of writing
    try:
      fid = open(file_name, 'wb')
    except IOError:
      print 'Can''t create file: {0}'.format(file_name)
      return
    # Write options to binary file
    fid.write('fc')
    fid.write(numpy.uint8([1, 0]))
    fid.write(numpy.uint16(self.option.width))
    fid.write(numpy.uint16(self.option.height))
    fid.write(numpy.uint16(self.option.rank_size))
    fid.write(numpy.uint16(self.option.min_rank_size))
    fid.write(numpy.uint8(self.option.dom_step))
    # Write main data to binary file
    data_ln = numpy.uint32(numpy.ceil(self.cur_bit / 8.0))
    fid.write(data_ln)
    fid.write(self.out_buf[: (data_ln / 2)])
    # End of writing and clear output buffer
    fid.close()
    del self.out_buf

  def load(self, file_path):
    '''
      Load data from a binary file
      :param file_name:
    '''
    # Start of reading
    try:
      fid = open(file_path, 'rb')
    except IOError:
      print 'Can''t open file: {0}'.format(file_path)
      return
    # Check format support
    ch = fid.read(2)
    if (ch[0] != 'f') or (ch[1] != 'c'):
      print 'The format is not supported'
      return
    ch = fid.read(2)
    if (ord(ch[0]) > 1) or (ord(ch[1]) > 0):
      print 'The format is not supported'
      return
    # Read options from a binary file
    ch = fid.read(2)
    self.option.width = struct.unpack('H', ch)[0]
    ch = fid.read(2)
    self.option.height = struct.unpack('H', ch)[0]
    ch = fid.read(2)
    self.option.rank_size = struct.unpack('H', ch)[0]
    ch = fid.read(2)
    self.option.min_rank_size = struct.unpack('H', ch)[0]
    ch = fid.read(1)
    self.option.dom_step = struct.unpack('B', ch)[0]
    ch = fid.read(4)
    data_ln = struct.unpack('I', ch)[0]
    # Read main data from a binary file
    ch = fid.read(data_ln)
    self.out_buf = numpy.array(struct.unpack('B' * (data_ln - 1), ch),
                               dtype=numpy.uint16)
    # End of reading
    fid.close()
