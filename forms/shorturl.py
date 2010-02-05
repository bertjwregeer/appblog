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


from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

# Django imports
from django import newforms as forms

import models

REDIRECT_CHOICES = (
	(301, "301 - Permanent Redirect"),
	(302, "302 - Temporary Redirect"),
	(403, "403 - Access Denied"),
	(404, "404 - File Not Found"),
	(500, "500 - Internal Server Error")
)
	
class ShorturlForm(djangoforms.ModelForm):
	httpcode = forms.IntegerField(widget=forms.Select(choices=REDIRECT_CHOICES), required=True, label='HTTP code')
	class Meta:
		model = models.Shorturl 
