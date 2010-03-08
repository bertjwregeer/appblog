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

import cgi
import urllib
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache

import models
import utils

class Shorturl():
	"""
	
	Provides the implementation for the short URL
	
	The only reason this exists is so that URL's on PCB's and documentation do not have to be
	extremely long. It allows simple things like example.net/sample to redirect to the appropriate
	page which contains the documentation, or blog post that contains the information.
	
	"""
	def __init__(self, handler):
		self.model = models.Shorturl
		self.handler = handler
		self.count = utils.Count()
		
	def domagic(self, path):
		"""
		This is where it all happens ... we check to see if it is a valid short URL and act upon it.
		
		The model has a httpcode value which is going to determine the HTTP code that we send the client
		
		500 = Server Error
		404 = File is missing
		403 = Access Denied
		302 = Temporary redirect
		301 = Permanent Redirect
		"""
		
		path = urllib.unquote(path).decode("utf-8")
		
		surl = memcache.get("shorturl." + path)
		
		if not surl:
		# Prepare the query
			q = self.model.all().filter("uripath =", path)
			surl = q.get()
			memcache.add("shorturl." + path, surl, 3600)
	
		if surl:
			self.count.inc("shorturl", surl.uripath)
			
			code = surl.httpcode
			
			if code == 500:
				self.handler.error(500)
				self.handler.response.out.write("Internal Server Error")
			elif code == 404:
				self.handler.error(404)
				self.handler.response.out.write("Object Not Found!")
			elif code == 403:
				self.handler.error(403)
				self.handler.response.out.write("Access Denied")
			elif code == 302:
				self.handler.redirect(surl.location)
			elif code == 301:
				self.handler.redirect(surl.location, permanent=True)
			else:
				# If we don't know the status code, we just output it directly 
				# and the location field becomes a simple message that is output directly to the browser
				self.handler.response.set_status(code)
				self.handler.response.out.write(surl.location)

			return True
		else:
			return False
