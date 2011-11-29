# ~coding: utf-8~

from fractality import Packer
import time

#import psyco
#psyco.bind(Packer.compress)
#psyco.bind(Packer.process)
#psyco.log()
#psyco.profile()

def main():
  pac = Packer()
  #
  pac.image.load('arthrosis.bmp')
  #
  pac.option.rank_size = 8
  pac.option.dom_step = 4
  pac.option.find_best_dom = True
  #
  tic = time.time()
  pac.compress(eps=0.005)
  toc = time.time() - tic
  print '\n{0:.2f} sec. ({1:.2f} min.) has elapsed'.format(toc, toc / 60)
  #
  pac.fpac.save('arthrosis.fpac')

if __name__ == '__main__':
  main()
