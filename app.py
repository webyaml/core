#!/usr/bin/env python
# filename: app.py
# path: /core/

# make python2 strings and dictionaries behave like python3
from __future__ import unicode_literals

try:
	from builtins import dict, str
except ImportError:
	from __builtin__ import dict, str


''' 
	Copyright 2017 Mark Madere

	Licensed under the Apache License, Version 2.0 (the "License");
	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.
'''

# Main Application Script

''' external imports
'''


import web
import os
import sys

'''	Current Working Directory

	This script can be envoked either directly in the 'core' directory,
	or through a symlink from within the sites directory.  The current
	working directory needs to set differnetly for each case
	
	The first issue is the python system path.  This is important 
	because python needs to know how to find modules and classes
	which need to be imported.
	
	The second issue is to make sure that these modules can locate
	configurations and additional modules that will be imported at
	run-time (or one-the-fly).
	
	After we determine where the scipt should be running we save the
	current working directory in the web object.  this maintains the correct
	behavior over multiple threads.
	
'''

if "framework" not in dir(web):

	# create a data object that is common across all threads
	web.framework = {}

	# Absolute path of this script
	web.framework['absolute_path'] = os.path.dirname(os.path.abspath(__file__))
	
	# use core as absolute path if available
	if not web.framework['absolute_path'].endswith('core') and os.path.exists("%s/core" %web.framework['absolute_path']):
		
		web.framework['absolute_path'] = "%s/core" %web.framework['absolute_path']
	
	# symlinked path: /{path-to-framework}/sites/{site}/core
	if web.framework['absolute_path'].split("/")[-3] == "sites":
		
		# change directory to one directory above absolute path
		web.framework['cwd'] = "/".join(web.framework['absolute_path'].split("/")[:-1])
		
	# non-symlinked path: /{path-to-framework}/core
	else:
		
		# change directory to the absolute path
		web.framework['cwd'] = "/".join(web.framework['absolute_path'].split("/"))


#debug 
print('Absolute Path: %s' %web.framework['absolute_path'])	

# Append the absolute path to the system path
#if web.framework['absolute_path'] not in sys.path:
sys.path.append(web.framework['absolute_path'])

# debug 
print('CWD: %s' %web.framework['cwd'])

# change workign directory
os.chdir(web.framework['cwd'])


''' internal imports
'''
import classes.url

# webpy vars
web.config.debug = True

# favicon handler
class favicon:
	def GET(self):
		#f = open('static/images/favicon.ico')
		web.header('Content-type', 'image/x-icon')
		#return f.read()

		path = 'static/images/favicon.ico'
		with open(path, 'rb') as f:
			content = f.read()
		return content


# webpy urls to webyaml classes
urls = (
		'/favicon.ico','favicon', # pass favicon url to the favicon handler
		'/(.*)', 'classes.url.URL',
		'(.*)', 'classes.url.URL',
	)


'''	Main
'''
if __name__ == "__main__":
	
	print("Starting CherryPy server")
	
	app = web.application(urls, globals())

	# sessions
	if web.config.get('_session') is None:
		session = web.session.Session(app, web.session.DiskStore('sessions'))
		web.config._session = session
	else:
		session = web.config._session	
	
	classes.url.session = session
	
	# start application
	app.run()
	
	
elif __name__.startswith('_mod_wsgi_'):
	
	print("Starting WSGI thread")
	
	# session hook
	def session_hook():
		web.ctx.session = session
	
	# File sessions
	web.config.session_parameters['cookie_path'] = '/'
	app = web.application(urls, globals())
	session = web.session.Session(app, web.session.DiskStore('sessions'))
	app.add_processor(web.loadhook(session_hook))
	application = app.wsgifunc()
	# End File sessions
	
	'''
	# Database sessions
	web.config.session_parameters['cookie_path'] = '/'
	db = web.database(dbn='mysql', db='db', user='user', pw='*******')
	app = web.application(urls, globals())
	store = web.session.DBStore(db, 'webapp_sessiondata')
	session = web.session.Session(app, store, initializer={'count': 0})
	app.add_processor(web.loadhook(session_hook))
	application = app.wsgifunc()
	# End Database sessions
	'''
		


