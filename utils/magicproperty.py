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
from google.appengine.ext import db


def MagicProperty(prop, magic_func=None, *args, **kw):
	if magic_func:
		# No pants required.
		return _MagicProperty(prop, magic_func, *args, **kw)
	else:
		# We are putting some pants on the function.
		def pants(magic_func):
			return _MagicProperty(prop, magic_func, *args, **kw)
		return pants


class _MagicProperty(db.Property):
	"""MagicProperty which will modify output based on a function that it is given.
	
	Inspired by: 
	http://appengine-cookbook.appspot.com/recipe/custom-model-properties-are-cute
	http://code.google.com/appengine/articles/extending_models.html
	http://googleappengine.blogspot.com/2009/07/writing-custom-property-classes.html
	
	"""
	def __init__(self, prop, magic_func, *args, **kw):
		super(_MagicProperty, self).__init__(*args, **kw)
		self.magic_func = magic_func
		self.magic_prop = prop
	
	def attr_name(self):
		# In google.appengine.ex.db there is an explicit warning not to use this method, so we test for it first.
		if self._attr_name:
			return self._attr_name()
		else:
			return "_" + self.name
	
	def __get__(self, model_instance, class_instance):
		if model_instance is None:
			return self
		
		# TODO: If the property that this one is functioning on is changed, we need a way to know that so that we recalculate
		
		# Original __get__ in google.appengine.ext.db has getattr to retrieve the value from the model instance
		magic_done = getattr(model_instance, self.attr_name(), None)
		if magic_done is None:
			magic_done = self.magic_func(self.magic_prop.__get__(model_instance, class_instance))
			
			# Set the attribute in the model
			setattr(model_instance, self._attr_name(), magic_done)
		return magic_done
		
	
	def __set__(self, *args):
		raise db.DerivedPropertyError("MagicProperty is magic. Magic may not be modified.")
	
