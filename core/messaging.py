# ~coding: utf-8~

class Publisher:
  def __init__(self):
    self.subs = []

  def subscribe(self, sub):
    self.subs.append(sub)

  def unsubscribe(self, sub):
    if self.subs.count(sub) > 0:
      self.subs.remove(sub)
  
  def notify(self, msg, **kw):
    for sub in self.subs:
      if hasattr(sub, msg):
        getattr(sub, msg)(**kw)
