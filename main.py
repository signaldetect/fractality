# ~coding: utf-8~

from fractality import Packer
import time

import psyco
psyco.bind(Packer.compress)
psyco.bind(Packer.calc_for_rank)
#psyco.log()
#psyco.profile()

def main():
  pck = Packer()
  #
  pck.image.load('cover.jpg')
  #
  pck.option.rank_size = 4
  pck.option.dom_step = 2
  pck.option.find_best_dom = True
  #
  tic = time.time()
  pck.compress(eps=0.005)
  toc = time.time() - tic
  print '\n{0:.2f} sec. ({1:.2f} min.) has elapsed'.format(toc, toc / 60)
  #
  pck.fpck.save('cover.fpck')

if __name__ == '__main__':
  main()
