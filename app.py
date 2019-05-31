#!/usr/bin/env python
# filename: app.py
# path: /core/
''' 
# make python2 strings and dictionaries behave like python3
from __future__ import unicode_literals

try:
	from builtins import dict, str
except ImportError:
	from __builtin__ import dict, str


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


	WebYAML Application Script

	This script starts the web application.  It can be directly run
	in a shell or can be loaded via WSGI and a webserver.
	
	This script is typically located in the webyaml core and
	symlinked into your application directory.
	
	The application will fail to start if no core is found.
	Please refer to the documentation here:
	http://webyaml.com/docs/gettingstarted/filestructure
	
'''

# Main Application Script

''' external imports
'''
import web
import os
import sys

# vars
urls_config_file = 'conf/urls.cfg'
web.config.debug = True
first_load = False
urls = (
		'/favicon.ico','favicon', # pass favicon url to the favicon handler
		'/__ab__','AB', # pass apache bench test handler		
		'/(.*)', 'classes.view.View',
		'(.*)', 'classes.view.View',
	)

if "framework" not in dir(web):

	# create a data object that is common across all threads
	web.framework = {}

	# absolute path of this script
	web.framework['absolute_path'] = os.path.dirname(os.path.abspath(__file__))
	
	
	# does this directory contain a core?  core can be a symlink or directory
	if not os.path.exists("%s/core" %web.framework['absolute_path']):
		
		print("The application directory does not contain a symlink to 'core'")
		sys.exit(1)
	
	# set cwd and absolute_path
	web.framework['cwd'] = web.framework['absolute_path']
	web.framework['absolute_path'] = "%s/core" %web.framework['absolute_path']
	
	
	# mark that this is the first load of the thread
	first_load = True

# Append the absolute path to the system path
sys.path.append(web.framework['absolute_path'])

# change working directory
os.chdir(web.framework['cwd'])

# debug
#print('Absolute Path: %s' %web.framework['absolute_path'])	
#print('CWD: %s' %web.framework['cwd'])


''' internal imports
'''
import classes.configuration
import classes.view

#no cache
#first_load = True

# load view configuration files
if first_load:
	
	# debug
	print('starting new thread for application')
	
	web.framework['configuration_object'] = classes.configuration.Configuration()


''' Classes
'''
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

# Apache Bench handler
class AB:
	def GET(self):

		return "Hello World!"

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
	
	classes.view.session = session
	
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
