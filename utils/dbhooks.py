### Shamelessly stolen from http://blog.notdot.net/2010/04/Pre--and-post--put-hooks-for-Datastore-models

from google.appengine.ext import db

class HookModel(db.Model):
	def before_put(self):
		pass
	
	def after_put(self):
		pass
	
	def put(self, **kwargs):
		self.before_put()
		super(HookModel, self).put(**kwargs)
		self.after_put()
		
old_put = db.put

def hooked_put(models, **kwargs):
	for model in models:
		if isinstance(model, HookModel):
			model.before_put()
	old_put(models, **kwargs)
	for model in models:
		if isinstance(model, HookModel):
			model.after_put()

db.put = hooked_put