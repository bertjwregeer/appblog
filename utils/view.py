###
 # Copyright (c) 2009 Bert JW Regeer;
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

import os
from google.appengine.api import users
from google.appengine.ext.webapp import template

import config
from config import VIEW_PATH

class View():
	"""
	
	A two-step-view system allows multiple different templates to be rendered which
	are then stored in the View, then when the final version output has to be created
	all those parts are passed to the final template file to produce the final output. 
	
	"""
	def __init__(self, handler, convenience =True):
		self.parts = {}
		self.defaults = {}
		self.request = handler.request
		
		user = users.get_current_user()
		
		if convenience:
			# Set up some defaults that can come in handy
			self.defaults['logout'] = { "url": users.create_logout_url(self.request.uri), "text": "Logout" }
			self.defaults['login']  = { "url": users.create_login_url(self.request.uri), "text": "Login" }
			if user:
				self.defaults['loggedin'] = True
			else:
				self.defaults['loggedin'] = False
			
			self.defaults['site']   = { 
						"title": config.SETTINGS["title"], 
						"description": config.SETTINGS["description"],
						"author": config.SETTINGS["author"],
						"appurl": self.request.application_url + "/",
						"cururl": self.request.uri 
						}
			
			if config.SETTINGS["contact"].startswith("mailto:"):
				self.defaults['site']['contact'] = config.SETTINGS["contact"]
			else:
				if not config.SETTINGS["contact"].startswith("/"):
					config.SETTINGS["contact"] = "/" + config.SETTINGS["contact"]
				
				self.defaults['site']['contact'] = self.request.application_url + config.SETTINGS["contact"]
	def inject(self, params):
		"""
		Allows the addition of extra variables into the defaults that are 
		accessible to all the templates, can override already set variables.
		"""
		
		self.defaults.update(params)	
		
	def part(self, part, tfile = "", params = {}):
		"""
		Renders a template file and places it in the parts dictionary, as well as 
		returning the rendered template to the callee.
		"""
		
		if not tfile:
			tfile = part + ".html"
		
		self.parts[part] = self.render(tfile, params)
		
		return self.parts[part]
		
	
	def render(self, tfile, params = {}):
		"""
		Renders a template file and returns it to caller.
		"""
		
		# Parameters passed in may override default values
		values = self.defaults
		values.update(params);
		
		return template.render(VIEW_PATH + tfile, values)	
		
	def final(self, tfile, params = {}):
		"""
		Finalize the rendering, take the parts that currently exist, splice in
		the parameters.
		"""
		
		values = self.defaults
		values.update(self.parts)
		values.update(params)
		
		return template.render(VIEW_PATH + tfile, values)
