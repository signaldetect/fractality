# ~coding: utf-8~

import numpy

class PckOption:
  rank_size = 2 # размер ранговой области
  min_rank_size = 1
  dom_step = 1 # шаг поиска домена
  find_best_dom = False # искать лучший домен

  width = 0
  height = 0

  def __init__(self):
    pass

  def fix_image_size(self, image):
    '''
      :param image:
    '''
    try:
      (w, h) = image.img.size
    except (NameError, AttributeError):
      print 'Please, load any image file'
      return ()
    #
    print 'Origin size: {0}x{1}'.format(w, h)
    (w, h) = (w, h) - numpy.mod([w, h], [self.rank_size, self.rank_size])
    print 'New size: {0}x{1}'.format(w, h)
    #
    (self.width, self.height) = (w, h)
    image.mx = image.mx[: h, : w, :]
    #
    return (w, h)
