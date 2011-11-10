# ~coding: utf-8~

from PIL import Image
import numpy

class SrcImage:
  img = None
  mx = None

  def __init__(self):
    pass

  def load(self, file_name):
    '''
      :param file_name:
    '''
    try:
      self.img = Image.open(file_name)
    except IOError:
      print 'Bad file name: {0}'.format(file_name)
      return
    #
    self.mx = numpy.array(self.img)[-1 : : -1, :, :]

  def show(self):
    pass
  
class PckImage:
  option = None

  cur_bit = 0
  #bits = None
  out_buf = None

  def __init__(self):
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

  def save(self, file_name):
    '''
      Save to binary file and flush output buffer
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
