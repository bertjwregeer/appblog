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

STATUS_CHOICES = (
	("draft",     "Draft"),
	("editor",    "Editor Review"),
	("published", "Published"),
)


class Entry(db.Model):
	author = db.UserProperty()
	title = db.StringProperty(required=True)
	status = db.StringProperty(required=True, default=STATUS_CHOICES[0][0], choices=[x[0] for x in STATUS_CHOICES])
	body = db.TextProperty(required=True)
	tags = db.ListProperty(db.Key)
	pubdate = db.DateProperty()
	pubtime = db.TimeProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	updated = db.DateTimeProperty(auto_now=True)
	
	# Next items are dynamically generated
	cache_slug = db.UnindexedProperty()
	slug = utils.MagicProperty(title, len, cache_prop=cache_slug, required=True)
	cache_html= db.UnindexedProperty()
	html = utils.MagicProperty(body, len, cache_prop=cache_html, required=True)
	
	def delete(self, *args, **kw):
		super(Entry, self).delete(*args, **kw)
		count = utils.Count()
		count.clear("entry", self.uripath)
	
	@property
	def hits(self):
		count = utils.Count()
		return count.curcount("entry", self.slug)

class EntryForm(djangoforms.ModelForm):
	status  = forms.CharField(widget=forms.Select(choices=STATUS_CHOICES), required=True, label='Status')
	body = forms.CharField(widget=forms.Textarea(attrs={"rows": "10"}), required=True, label='Body')
	
	class Meta:
		model = Entry
		fields = ["title", "body", "status"]

