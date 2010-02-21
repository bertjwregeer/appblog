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
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import config

import models
import utils

class Entry(utils.RequestHandler):
	def get(self, path):
		self.view.inject({ "page": {"title": "Administrator Interface"}})
		
		# TODO: Implement paging so that when there are more than 20 URL's we can page through them
		q = models.Entry.all()
		entries = q.fetch(20)
		
		form = self.view.render("form.html", params={
							"form": models.entry.EntryForm(), 
							"form_action": "admin/entry/", 
							"form_legend": "Create new entry"}
					)
		
		self.view.part("body", "admin/Entry.html", params={"form": form, "entries": entries})
		
		self.response.out.write(self.view.final("admin/base.html"))
	
	def post(self, path):
		data = models.entry.EntryForm(data=self.request.POST)
		
		if data.is_valid():
			# TODO: Move this back into the form
			entry = data.save(commit=False)
			self.redirect("/admin/entry/")
		else:
			logging.error("Data is not valid!")
		
		form = self.view.render("form.html", params={
							"form": data,
							"form_action": "admin/entry/",
							"form_legend": "Create new entry"}
					)
		self.view.part("body", "admin/Entry.html", params={"form": form})
		self.response.out.write(self.view.final("admin/base.html"))