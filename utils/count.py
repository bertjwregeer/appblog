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

from google.appengine.ext import db
from google.appengine.api import memcache
import logging
import random

from config import NUM_SHARDS
import models

class Count():
	"""
	This is the support class that provides several functions to get the count of a counter, 
	as well as incrementing a counter all with sharding for increased availability and the hope
	that there will be less contention.
	"""
	def __init__(self):
		self.model = models.Count
	
	def inc(self, namespace, name):
		"""
		Increment a counter.
		"""
		cname = namespace + "." + name + str(random.randint(0, NUM_SHARDS - 1))
		
		shardcount = self.model.get_or_insert(cname, namespace=namespace, name=name)
		def txn():
			shardcount.count += 1
			shardcount.put()
		try:
			db.run_in_transaction(txn)
		except(db.Error), e:
			logging.error("Shard (%s) increment failed: %s", cname, e)
			return False
		
		memcache.incr("count." + namespace + "." + name)
		return True
	
	def dec(self, namespace, name):
		"""
		Decrement a counter. This should not happen often, so double check that it exists, find the
		first shard that exists and remove one, if the shard drops to 0, we just remove it entirely.
		"""
		
		for scount in self.model.all().filter("namespace = ", namespace).filter("name = ", name):
			scount.count -= 1
			if scount.count == 0:
				scount.delete()
			else:
				scount.put()
			break
		memcache.decr("count." + namespace + "." + name)

	def curcount(self, namespace, name):
		"""
		Get the current count for the requested item
		"""

		total = memcache.get("count." + namespace + "." + name)
		if total is None:
			total = 0
			for scount in self.model.all().filter("namespace = ", namespace).filter("name = ", name):
				total += scount.count
			memcache.add("count." + namespace + "." + name, total, 3600)
		return total
		
	def clear(self, namespace, name):
		"""
		Clear the counter, reset it back to 0
		"""
		
		for scount in self.model.all().filter("namespace = ", namespace).filter("name = ", name):
				scount.delete()
		memcache.delete("count." + namespace + "." + name)
