# ~coding: utf-8~

import matplotlib
matplotlib.use('TkAgg')

import Tkinter as tk
import os

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.widgets import RectangleSelector
from widget import TipButton

class View(tk.Frame):
  axes = None
  canvas = None
  toolbar = None

  selector = None

  def __init__(self, parent=None):
    tk.Frame.__init__(self, master=parent, borderwidth=0)
    #
    fig = Figure(figsize=(5, 5), dpi=100, facecolor='black')
    self.axes = fig.add_subplot(111)
    self.axes.set_axis_bgcolor('black')
    self.axes.tick_params(direction='out', labelsize='x-small', colors='grey')
    #
    self.canvas = FigureCanvasTkAgg(fig, master=self)
    self.canvas.show()
    self.canvas.get_tk_widget().config(background='black',
                                       borderwidth=2, highlightthickness=0)
    self.canvas.get_tk_widget().grid(row=0, column=0,
                                     sticky=tk.W+tk.E+tk.N+tk.S)
    #
    self.toolbar = Controls(self, self.canvas)
    self.toolbar.grid(row=0, column=1, rowspan=2, sticky=tk.N)
    self.toolbar.update()
    #
    self.canvas._tkcanvas.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)
    '''
    msg_btn = tk.Button(master=root, text='Msg', command=show_msg)
    msg_btn.pack(side=tk.LEFT)
    #
    quit_btn = tk.Button(master=root, text='Quit', command=app_quit)
    quit_btn.pack(side=tk.LEFT)
    '''

  def redraw(self):
    self.canvas.show()

  def create_selector(self, callback):
    # Closure
    def selected(eclick, erelease):
      if eclick.ydata > erelease.ydata:
        (eclick.ydata, erelease.ydata) = (erelease.ydata, eclick.ydata)
      if eclick.xdata > erelease.xdata:
        (eclick.xdata, erelease.xdata) = (erelease.xdata, eclick.xdata)
      #
      x = [eclick.xdata, erelease.xdata]
      y = [eclick.ydata, erelease.ydata]
      #
      self.axes.set_ylim(y[1], y[0])
      self.axes.set_xlim(x[0], x[1])
      self.redraw()
      #
      self.toolbar.set_message('Fragment selected')
      #
      del self.selector
      callback(x, y)
    # Make selector
    self.selector = RectangleSelector(self.axes, selected, drawtype='box',
                                      rectprops=dict(facecolor='red',
                                                     edgecolor='black',
                                                     alpha=0.5, fill=True))

class Controls(NavigationToolbar2TkAgg, tk.Frame):
  def __init__(self, parent, canvas):
    self.parent = parent
    NavigationToolbar2TkAgg.__init__(self, canvas, window=parent)

  def _Button(self, text, file, command):
    file = os.path.join('gui', 'images', file.replace('.ppm', '.gif'))
    img = tk.PhotoImage(master=self, file=file)
    btn = TipButton(master=self, tip=text, text=text,
                    padx=2, pady=2, image=img, command=command,
                    relief=tk.FLAT, borderwidth=0)
    btn._ntimage = img
    btn.pack(side=tk.TOP, pady=2)
    #
    return btn

  def _init_toolbar(self):
    (ymin, ymax) = self.canvas.figure.bbox.intervaly
    (width, height) = (50, ymax - ymin)
    #
    tk.Frame.__init__(self, master=self.window,
                      width=width, height=height,
                      borderwidth=4)
    # Make axes menu
    self.update()
    # Make buttons
    self.bHome = self._Button('Home', 'home.ppm',
                              command=self.home)
    self.bBack = self._Button('Back', 'back.ppm',
                              command=self.back)
    self.bForward = self._Button('Forward', 'forward.ppm',
                                 command=self.forward)
    self.bPan = self._Button('Pan', 'move.ppm',
                             command=self.pan)
    self.bZoom = self._Button('Zoom', 'zoom_to_rect.ppm',
                              command=self.zoom)
    self.bsubplot = self._Button('Configure Subplots', 'subplots.ppm',
                                 command=self.configure_subplots)
    self.bsave = self._Button('Save', 'filesave.ppm',
                              command=self.save_figure)
    # Make message bar
    self.message = tk.StringVar(master=self.window)
    self._message_label = tk.Label(master=self.window,
                                   textvariable=self.message)
    self._message_label.grid(row=1, column=0, sticky=tk.W)
