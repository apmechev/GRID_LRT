#!/usr/bin/env python

def get_config():

    config = {
        'collection_interval': 10,    # Seconds, how often to collect metric data
	'proclist':['NDPPP','bbs-reducer','losoto']
    }

    return config
