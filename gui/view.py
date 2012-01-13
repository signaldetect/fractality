# ~coding: utf-8~

import matplotlib
matplotlib.use('TkAgg')

import Tkinter as tk
import os
import tool, form, widget

from core.messaging import Publisher
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.widgets import RectangleSelector
from tkFont import Font

class View:
  root = None

  info = None
  graph = None
  actions = None
  props = None

  toolbar = None
  settings = None

  def __init__(self):
    self.root = tk.Tk()
    self.root.wm_title('Fractality GUI')
    self.root.wm_iconbitmap(os.path.join('gui', 'images', 'logo.ico'))
    #
    self.info = Informer(parent=self.root)
    self.graph = Graph(parent=self.root)
    self.actions = tool.Actions()
    self.props = form.Properties()
    #
    self.toolbar = tool.ActionBar(parent=self.root, actions=self.actions)
    self.settings = form.PropertyEditor(parent=self.root, props=self.props)
    #
    self.toolbar.grid(row=0, column=0, rowspan=2,
                      sticky=tk.N+tk.S, ipadx=4)
    self.settings.grid(row=0, column=1, rowspan=2,
                       sticky=tk.N, padx=8, pady=8)
    self.info.grid(row=1, column=1,
                   sticky=tk.W+tk.E+tk.S, padx=8, pady=19)
    self.graph.grid(row=0, column=2, rowspan=2,
                    sticky=tk.W+tk.E+tk.N+tk.S)
    #
    self.root.grid_rowconfigure(0, weight=1, minsize=200)
    self.root.grid_columnconfigure(2, weight=1, minsize=300)

  def run(self):
    tk.mainloop()
  
  def quit(self):
    self.root.quit()    # stops mainloop
    self.root.destroy() # this is necessary on Windows to prevent Fatal
                        # Python Error: PyEval_RestoreThread: NULL tstate

class InformerSubscriber:
  def progress_stopped(self):
    pass

class Informer(tk.Frame, Publisher):
  parent = None
  console = None
  progress = None

  def __init__(self, parent=None):
    tk.Frame.__init__(self, master=parent, borderwidth=0)
    Publisher.__init__(self)
    #
    self.parent = parent
    #
    self.console = tk.Text(self, width=5, height=12, relief=tk.FLAT,
                           state=tk.DISABLED,
                           font=Font(family='Helvetica', size=8))
    self.console.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)

  def send(self, text=''):
    self.console.config(state=tk.NORMAL)
    self.console.insert(tk.END, text + '\n')
    self.console.config(state=tk.DISABLED)

  def compress_started(self, option):
    self.send('Compressing...')
    #self.send('Decompressing...')
    self.progress = widget.ProgressDialog(self.parent, title='Compressing...',
                                          callback=self.stop_progress)
    self.progress.update()
    self.progress.align_center()

  def progressing(self, value):
    #sys.stdout.write('\nComplete {0:3.2f}%\t\n'.format(100.0 * value))
    self.progress.meter.set(value)
    self.progress.update()

  def compress_aborted(self):
    self.send('Image isn\'t compressed')

  def compressed(self):
    self.progress.ok()
    self.send('Image is compressed')

  def stop_progress(self):
    self.send('Stop...')
    self.notify('progress_stopped')

class Graph(tk.Frame):
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
    btn = widget.TipButton(master=self, tip=text, text=text,
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
