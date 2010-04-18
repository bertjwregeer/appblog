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
from datetime import datetime

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

# Django imports
from django import newforms as forms
from django.newforms.util import ErrorList, ValidationError

import utils
from utils import dbhooks

from vendor.markdown import markdown

STATUS_CHOICES = (
	("draft",     "Draft"),
	("editor",    "Editor Review"),
	("published", "Published"),
)


class Entry(dbhooks.HookModel):
	author = db.UserProperty()
	title = db.StringProperty(required=True)
	status = db.StringProperty(required=True, default=STATUS_CHOICES[0][0], choices=[x[0] for x in STATUS_CHOICES])
	body = db.TextProperty(required=True)
	tags = db.ListProperty(db.Key)
	pubdate = db.DateTimeProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	updated = db.DateTimeProperty(auto_now=True)
		
	# Next items are dynamically generated
	cache_slug = db.UnindexedProperty()
	@utils.MagicProperty(title, cache_prop=cache_slug, pass_instance=True, required=True)
	def slug(instance, s):
		s = utils.slugify(s)
		
		ss = s
		ss = ss.decode('utf-8')
		def _unique():
			q = Entry.all().filter("slug =", ss)
			e = q.get()
			
			if e is None:
				return False
			
			if instance.is_saved():
				if instance.key() == e.key():
					return False
			
			return True
		
		counter = 0
		while _unique():
			ss = "%s-%s" % (s, counter)
			counter += 1
		
		return ss
	
	cache_html = db.UnindexedProperty()
	@utils.MagicProperty(body, cache_prop=cache_html, required=True)
	def html(s):
		return markdown.markdown(s)
	
	@property
	def hits(self):
		count = utils.Count()
		return count.curcount("entry", str(self.key()))
	
	def delete(self, *args, **kw):
		count = utils.Count()
		count.clear("entry", str(self.key()))
		super(Entry, self).delete(*args, **kw)
	
	def before_put(self):
		# Because there is no way to specify that a property has a dependency on another we fake a get, so that the cache is primed
		prime_cache = self.slug
		prime_cache = self.html
		
		# Check to see if the status has changed to published, or from published to non-published.
		
		if self.status == STATUS_CHOICES[2][0]:
			if self.pubdate is None:
				self.pubdate = datetime.utcnow()
		else:
			self.pubdate = None

class EntryForm(djangoforms.ModelForm):
	status  = forms.CharField(widget=forms.Select(choices=STATUS_CHOICES), required=True, label='Status')
	body = forms.CharField(widget=forms.Textarea(attrs={"rows": "10"}), required=True, label='Body')
	
	class Meta:
		model = Entry
		fields = ["title", "body", "status"]

