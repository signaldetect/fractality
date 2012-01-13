# ~coding: utf-8~

from fractality import Packer
from gui import Application

if __name__ == '__main__':
  pac = Packer()
  app = Application(kernel=pac)
  app.run()
