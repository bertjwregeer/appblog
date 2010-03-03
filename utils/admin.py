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

"""
Helper functions that are only meant to be used in administrative context.
"""

def paginate_table(request, view, model, query, properties=[], count=20):
	"""
	This will dynamically create a table that includes pagination with next and previous buttons.
	"""
	# TODO: Add in the previous button logic
	
	table = {"headers": [], "data": []}
	paginate = {"prev": "", "next": ""}
	
	cursor = request.get("after", None)
	if cursor:
		query.with_cursor(cursor)
	
	resultset = query.fetch(count)
	cursor = query.cursor()
	
	for prop in properties:
		vname = getattr(model, prop, None)
		vname = getattr(vname, 'verbose_name', prop.capitalize().replace('_', ' '))
		
		table['headers'].append(vname)
	
	for row in resultset:
		key = row.key().id()
		ritems = {"key": key, "props": []}
		for prop in properties:
			ritems['props'].append(getattr(row, prop))
		
		table['data'].append(ritems)
	
	if query.with_cursor(cursor).get() is not None:
		paginate['next'] = "?after=" + cursor
	
	return view.render("admin/table.html", params = {"table": table, "paginate": paginate})