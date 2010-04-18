###
 # Copyright (c) 2010 Bert JW Regeer;
 #
 # Permission to use, copy, modify, and distribute this software for any
 # purpose with or without fee is hereby granted, provided that the above
 # copyright notice and this permission notice appear in all copies.
 #
 # THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 # WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 # MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 # ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 # WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 # ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 # OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 #
###

import logging
import hashlib
from google.appengine.ext import db

def MagicProperty(prop, magic_func=None, cache_prop=None, pass_instance=False, *args, **kw):
	if magic_func:
		# No pants required.
		return _MagicProperty(prop, magic_func, cache_prop, pass_instance, *args, **kw)
	else:
		# We are putting some pants on the function.
		def pants(magic_func):
			return _MagicProperty(prop, magic_func, cache_prop, pass_instance, *args, **kw)
		return pants

class _MagicDatastore():
	"""This is an internal class for _MagicProperty."""
	
	def __init__(self, val):
		self.value = val
	
	def retval(self):
		return self.value

class _MagicProperty(db.Property):
	"""MagicProperty which will modify output based on a function that it is given.
	
	This has several ways in which it may be called:
	
	In this example we create the model, no caching is done, so any data that is returned from the datastore
	will be erased the first time that the MagicProperty is accessed and recomputed.
	
		class MagicTest(db.Model):
			title = db.StringProperty(required=True)
			chars = utils.MagicProperty(title, len, required=True)
	
		mytest = MagicTest(title="It was for the good of the school!")
		
		>>> print mytest.title
		It was for the good of the school!
		>>> print mytest.chars
		34
		
		mytest = MagicTest.all().get()
		
		>>> print mytest.title
		Hello
		>>> print mytest.chars		
		5	# Do note, this is recalculated the first time it is called, as long as title does not change it won't be recomputed.
	
	In this example we create the model, and we also create a caching property so that even when we get values back 
	from the datastore we use the cached computed value rather than running the function again. Do note that this requires overriding put()
	to prime the cache as there is currently no way to specify that certain properties should be "saved" before others.
	
		class MagicTesting(db.Model):
			title = db.StringProperty(required=True)
			cache = db.UnindexedProperty()
			chars = utils.MagicProperty(title, len, cache_prop=cache, required=True)
		
			def put(self, *args, **kw):
				prime_cache = self.chars
				super(MagicTesting).put(*args, **kw)
		
		mytesting = MagicTesting(title="Get the pocket knife out of my boot.")
	
		>>> print mytesting.title
		Get the pocket knife out of my boot.
		>>> print mytesting.chars
		36
		
		mytesting = MagicTest.all().get()
		
		>>> print mytesting.title
		How are you?
		>>> print mytesting.chars	
		12	# This is not recomputed so long as the title has not changed, however it uses more datastore space to store a hash.
		
		
	Inspired by: 
	http://appengine-cookbook.appspot.com/recipe/custom-model-properties-are-cute
	http://code.google.com/appengine/articles/extending_models.html
	http://googleappengine.blogspot.com/2009/07/writing-custom-property-classes.html
	
	"""
	def __init__(self, prop, magic_func, cache_prop, pass_instance, *args, **kw):
		"""
		Extra parameters you can give this initializer.
		
			prop		= Property to be acted upon
			magic_func	= The function to be called when the property is accessed
			cache_prop	= The property that can hold our cache, I suggest it is an db.UnindexedProperty() since it just stores sha1 hashes
		"""
		super(_MagicProperty, self).__init__(*args, **kw)
		self.magic_func = magic_func
		self.magic_prop = prop
		self.magic_cache = cache_prop
		self.magic_pass = pass_instance
		
	def get_cache_val(self, model_instance, class_instance):
		if self.magic_cache is not None:
			return self.magic_cache.__get__(model_instance, class_instance)
		return getattr(model_instance, self.attr_name() + "orig", None)
			
	def set_cache_val(self, model_instance, val):
		val = hashlib.sha1(val).hexdigest()
		
		if self.magic_cache is not None:
			self.magic_cache.__set__(model_instance, val)
		setattr(model_instance, self.attr_name() + "orig", val)
	
	def attr_name(self):
		# In google.appengine.ex.db there is an explicit warning not to use this method, so we test for it first.
		if self._attr_name:
			return self._attr_name()
		else:
			return "_" + self.name
	
	def __get__(self, model_instance, class_instance):
		if model_instance is None:
			return self
		
		cur = self.magic_prop.__get__(model_instance, class_instance)
		cur = cur.encode('utf-8')		
		last = self.get_cache_val(model_instance, class_instance)
		if last == hashlib.sha1(cur).hexdigest():
			logging.info("Cache hit: %s" % (cur))
			return getattr(model_instance, self.attr_name(), None)
		
		logging.info("Cache miss: %s" % (cur))
		
		magic_done = u""
		if self.magic_pass:
			magic_done = self.magic_func(model_instance, cur)
		else:
			magic_done = self.magic_func(cur)
		
		# Set the attribute in the model
		setattr(model_instance, self.attr_name(), magic_done)
		self.set_cache_val(model_instance, cur)
		
		return magic_done
		
	def __set__(self, model_instance, value):
		if isinstance(value, _MagicDatastore):
			setattr(model_instance, self.attr_name(), value.retval())
		else:
			raise db.DerivedPropertyError("MagicProperty is magic. Magic may not be modified.")
	
	def get_value_for_datastore(self, model_instance):
		output = super(_MagicProperty, self).get_value_for_datastore(model_instance)
		
		if len(output) > 500:
			return db.Text(output)
		else:
			return output
	
	def make_value_from_datastore(self, value):
		return _MagicDatastore(value)
