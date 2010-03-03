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
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

# Django imports
from django import newforms as forms
from django.newforms.util import ErrorList, ValidationError

import utils

REDIRECT_CHOICES = (
	(301, "301 - Permanent Redirect"),
	(302, "302 - Temporary Redirect"),
	(403, "403 - Access Denied"),
	(404, "404 - File Not Found"),
	(500, "500 - Internal Server Error")
)

class Shorturl(db.Model):
	uripath = db.StringProperty(verbose_name="Path", required=True)
	httpcode = db.IntegerProperty(verbose_name="HTTP code", required=True, default=REDIRECT_CHOICES[0][0], choices=[x[0] for x in REDIRECT_CHOICES])
	location = db.StringProperty(verbose_name="Location")

	def delete(self, *args, **kw):
		super(Shorturl, self).delete(*args, **kw)
		count = utils.Count()
		count.clear("shorturl", self.uripath)

	@property
	def hits(self):
		count = utils.Count()
		return count.curcount("shorturl", self.uripath)
		
	

class ShorturlForm(djangoforms.ModelForm):
	httpcode = forms.IntegerField(widget=forms.Select(choices=REDIRECT_CHOICES), required=True, label='HTTP code')

	def clean_uripath(self):
		cleaned_data = self.clean_data
		uripath = cleaned_data.get('uripath')
		
		# We are going to test for uniqueness before we consider this field clean
		if self.instance == None or self.instance.uripath != uripath:
			if Shorturl.all().filter("uripath =", uripath).fetch(1):
				raise forms.ValidationError("Path already exists.")
		
		
		return uripath
		
	def clean_location(self):
		cleaned_data = self.clean_data
		httpcode = cleaned_data.get('httpcode')
		location = cleaned_data.get('location')

		if httpcode == 301 or httpcode == 302:
			if len(location):
				return location
			else:
				raise forms.ValidationError("Location required when using status code 301 or 302.")

		return location

	class Meta:
		model = Shorturl
	
