# ~coding: utf-8~

import Tkinter as tk

class PropertyEditor(tk.Frame):
  KIND = {
    'entry': 0,
    'option': 1,
    'check': 2
  }

  count = 0

  meth = None
  rank_size = None
  dom_step = None
  find_best_dom = None
  tol = None

  def __init__(self, parent, props):
    tk.Frame.__init__(self, master=parent, borderwidth=0)
    props.setup(parent=self)
    #
    self.meth = self._add_prop('Method', self.KIND['option'],
                               var=props.meth, options=props.METHODS)
    self.rank_size = self._add_prop('Rank size', var=props.rank_size)
    self.dom_step = self._add_prop('Domain step', var=props.dom_step)
    self.find_best_dom = self._add_prop('Find best domain',
                                        self.KIND['check'],
                                        var=props.find_best_dom)
    self.tol = self._add_prop('Error tolerance', var=props.tol)
    #
    self.grid_columnconfigure(1, weight=1)

  def _add_prop(self, caption='', kind=0, var=None, options=['',]):
    tk.Label(self, text=caption).grid(row=self.count, column=0,
                                      sticky=tk.W, padx=2, pady=2)
    #
    prop = None
    if kind == self.KIND['entry']:
      prop = tk.Entry(self, justify=tk.RIGHT)
      if var:
        prop.config(textvariable=var)
    elif kind == self.KIND['option']:
      if var and options:
        prop = apply(tk.OptionMenu, (self, var) + tuple(options))
    elif kind == self.KIND['check']:
      prop = tk.Checkbutton(self)
      if var:
        prop.config(variable=var)
    #
    prop.grid(row=self.count, column=1, sticky=tk.W+tk.E, padx=2, pady=2)
    self.count += 1
    #
    return prop

class Properties:
  _options = None

  METHODS = ['FE-algorithm', 'Pearson correlation', 'Entropy factor']

  meth = None
  rank_size = None
  dom_step = None
  find_best_dom = None
  tol = None

  def __init__(self, options):
    self._options = options

  def setup(self, parent):
    self.meth = tk.StringVar(parent)
    self.meth.set(self.METHODS[0]) # default value
    #
    self.rank_size = tk.IntVar(parent)
    self.rank_size.set(8) # default value
    #
    self.dom_step = tk.IntVar(parent)
    self.dom_step.set(4) # default value
    #
    self.find_best_dom = tk.BooleanVar(parent)
    self.find_best_dom.set(True) # default value
    #
    self.tol = tk.DoubleVar(parent)
    self.tol.set(0.005) # default value
  
  def action_compress(self):
    # Export all properties to options
    self._options.rank_size = self.rank_size.get()
    self._options.dom_step = self.dom_step.get()
    self._options.find_best_dom = self.find_best_dom.get()
    self._options.eps = self.tol.get()
