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

import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import config

import models
import utils
import utils.admin

class Shorturl(utils.RequestHandler):	
	def get(self, path):
		self.view.inject({ "page": {"title": "Administrator Interface", "self": "admin/shorturl/"}})
		
		if path == '':
			self.get_main(path);
		if path.startswith('edit'):
			self.get_edit(path)
		
		self.view.part("body", "admin/Shorturl.html", params=self.template_params)
		self.response.out.write(self.view.final("admin/base.html"))
	
	def get_main(self, path):
		q = models.Shorturl.all().order('uripath')
		table = utils.admin.paginate_table(self.request, self.view, models.Shorturl, q, properties = ["uripath", "httpcode", "location", "hits"])
		
		self.render_form()
		self.template_params['table'] = table
	
	def get_edit(self, path):
		
		self.render_form(action="edit");
	
	def post(self, path):
		self.view.inject({ "page": {"title": "Administrator Interface", "self": "/admin/shorturl/"}})
		
		if path == 'add':
			self.post_add(path)
		if path == 'delete':
			self.post_del(path)
		if path == 'edit':
			self.post_edit(path)
			
		self.view.part("body", "admin/Shorturl.html", params=self.template_params)
		self.response.out.write(self.view.final("admin/base.html"))
		
	def post_add(self, path):
		data = models.shorturl.ShorturlForm(data=self.request.POST)

		if data.is_valid():
			# TODO: Add error handling, what if adding the new shorturl fails?
			data.save()
			self.redirect("/admin/shorturl/")
		
		self.render_form(action="add", form=data)
		
	def post_edit(self, path):
		data = models.shorturl.ShorturlForm(data=self.request.POST, instance=models.Shorturl.get_by_id(long(self.request.get("id"))))

		if data.is_valid():
			# TODO: Add error handling, what if adding the new shorturl fails?
			data.save()
			self.redirect("/admin/shorturl/")

		self.render_form(action="edit", form=data)
	def post_del(self, path):
		ids = [long(x) for x in self.request.get_all("id")]
		
		if ids is []:
			self.redirect("/admin/shorturl/")
		
		shorturls = models.Shorturl.get_by_id(ids)
		
		for shorturl in shorturls:
			if shorturl is not None:
				shorturl.delete()
			
		self.redirect("/admin/shorturl")

	def render_form(self, action="add", form=None):
		if form is None:
			kwargs = {}
			if len(self.request.POST) is not 0:
				kwargs['data'] = self.request.POST;
			if self.request.get("id") is not '':
				kwargs['instance'] = models.Shorturl.get_by_id(long(self.request.get("id")));
				action = action + "?id=" + self.request.get("id")
			if kwargs == {}:
				data = models.shorturl.ShorturlForm()
			else:
				data = models.shorturl.ShorturlForm(**kwargs)
		else:
			data = form
			if self.request.get("id") is not '':
				action = action + "?id=" + self.request.get("id")
		
		self.template_params['form'] = self.view.render("form.html", params={
							"form": data,
							"form_action": "admin/shorturl/" + action,
							"form_legend": "Add Shorturl"}
					)
		return self.template_params['form']