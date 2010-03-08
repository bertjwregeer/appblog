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

from view import View
from shorturl import Shorturl
from requesthandler import RequestHandler
from count import Count
from magicproperty import MagicProperty

import re

# The ones commented out are just going to get procesed by urllib.quote.
RFC3986_ENCODE = [
	('!', ""),
	#('*', ""),
	#('\'', ""),
	#('(', ""),
	#(')', ""),
	#(';', ""),
	#(':', ""),
	('@', " at "),
	('&', " and "),
	('=', " equals "),
	('+', " plus "),
	('$', "dollar "),
	(',', ""),
	('/', " slash "),
	('?', ""),
	('%', "percent"),
	('#', "pound"),
	#('[', ""),
	#(']', ""),
	
	('<', " less-than "),
	('>', " greater-than "),
	
	#('{', ""),
	#('}', ""),
	('|', "or"),
	('\\', "backslash "),
	('^', " xor "),
	('`', ""),
	(' ', "_")		# Last, so that if there are spaces in any of the above they get processed as well
]

def slugify(s):
	"""
		This will create a "slug" that may then be used to identify an article or entry. This does not guarantee that it is 
		unique in any way shape or form.
	"""
	
	for special in RFC3986_ENCODE:
		s = s.replace(special[0], special[1])
	
	s = re.sub("_{1,2}", "_", s)
	s = re.sub("\.", "", s)
	
	return s.lower()
