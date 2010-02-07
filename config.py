import os

SETTINGS = { 
	"title": "Using Namespace",
	"description": "The Love of Hardware and Software",	# A blog about PCB's, Electronics and Code
	"lang": "en",
	"author": "Bert JW Regeer",
	"contact": "contact",					# For email use mailto:example@example.net
	
	# Enable or disable short URL's. For the mainpage handler this is one extra db query if enabled
	"shorturl": True
}

# Before running your own version, please change this to something that is not easy to guess

SECRET = "GO Hamster GO!"

# Do not modify below this line

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
VIEW_PATH = ROOT_PATH + "/views/"

# Over how many rows do we want to shard the counters.
# Increase this if you are seeing a lot of waiting on writing counters
NUM_SHARDS = 10