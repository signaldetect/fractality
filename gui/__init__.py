# ~coding: utf-8~

import os
import Tkinter as tk
import graph, tool, form

class Application:
  root = None

  kernel = None
  view = None
  actions = None
  props = None

  toolbar = None
  settings = None

  def __init__(self, kernel):
    self.root = tk.Tk()
    self.root.wm_title('Fractality GUI')
    self.root.wm_iconbitmap(os.path.join('gui', 'images', 'logo.ico'))
    #
    self.kernel = kernel
    self.view = graph.View(parent=self.root)
    self.actions = tool.Actions(self.kernel, self.view)
    self.props = form.Properties(self.kernel.option)
    #
    self.actions.subscribe(self.props)
    #
    self.toolbar = tool.ActionBar(parent=self.root, actions=self.actions)
    self.settings = form.PropertyEditor(parent=self.root, props=self.props)
    #
    self.toolbar.grid(row=0, column=0, sticky=tk.N+tk.S, ipadx=4)
    self.settings.grid(row=0, column=1, sticky=tk.N+tk.S, padx=8, pady=8)
    self.view.grid(row=0, column=2, sticky=tk.W+tk.E+tk.N+tk.S)
    #
    self.root.grid_rowconfigure(0, weight=1, minsize=300)
    self.root.grid_columnconfigure(2, weight=1, minsize=300)

  def run(self):
    tk.mainloop()
  
  def show_msg(self):
    self.view.toolbar.set_message('ok!')

  def quit(self):
    self.root.quit()    # stops mainloop
    self.root.destroy() # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
