# path: 
# filename: url.py
# description: application URL class

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

''' external imports
'''
import web
import yaml

import datetime
import os
import re

''' internal imports
'''
import classes.content

''' classes
'''
class View(object):
	
	def __init__(self):

		''' vars
		'''
		
		# timestamp 
		self.start_time = datetime.datetime.now()
		
		try:
			self.session = web.ctx.session #WSGI application
			
		except AttributeError:
			
			self.session = session #Cherry webserver
		
		# debug 
		#self.session.kill()
		
		# session vars
		if 'vars' not in dir(self.session):
			self.session.vars= {}
		
		# top Vars
		self.path_vars = {}
		self.get_vars = {}
		self.post_vars = {}
		self.post = False
		self.fnr_types = {}
		
		self.cache = {}
		#self.cache['includes'] = []
		self.error = None # is this still used?
		
		self.raw = {}
		self.attributes = {}

		# marker attributes and functions
		self.fnr_types = {

			# Configuration markers
			'this': 'self.attributes',	
			'parent': 'self.parent.attributes',
			'top': 'self.top.attributes',
			
			# Cached markers
			'cache': 'self.top.cache',
			'session': 'self.top.session.vars',
			
			# URI/GET/POST markers
			'path': 'self.top.path_vars',
			'get': 'self.top.get_vars',
			'post': 'self.top.post_vars',
			'getpost': 'self.top.getpost_vars',
			'raw': 'self.top.raw',
	
			# functions
			'exists': 'self.exists',
			#'count': 'self.count',
			'len': 'self.count',
			'random': 'self.random_choice',
			
			# sanitizing
			'escape': 'self.escape',
			'escape_markers': 'self.escape_markers', #undocumented
			'html_markers': 'self.html_markers', #undocumented
			'html_escape': 'self.html_escape',
			'escape_script': 'self.escape_script',

			# URI
			'url_quote': 'self.url_quote',
			'url_unquote': 'self.url_unquote',

			# decoration
			'keyword': 'self.keyword',
			'truncate': 'self.truncate',
			'last4': 'self.last4',
			'strip': 'self.strip',
			'singleline': 'self.singleline',
			#'remove': 'self.remove', #undocumented
			'dollar': 'self.dollar', #undocumented
			'title_case': 'self.title_case',
			'tab': 'self.tab',
			
			'lower': 'self.lower',
			'upper': 'self.upper',
			
			'us_phone': 'self.us_phone',
			'us_ssn': 'self.us_ssn',
			
			# object formating
			'uuid': 'self.uuid',
			'date': 'self.date',
			'int': 'self.int',
			'string': 'self.string',
			
			'key_val_list': 'self.key_val_list',

			# hashing
			'sha256': 'self.sha256',
			'md5': 'self.md5',
			
			# object conversion
			'json': 'self._json',
			'yaml': 'self._yaml',
			'csv': 'self.csv',
			
			# god only knows
			'join': 'self._join',
			'split': 'self.split',
			'list': 'self.list',
			'cleanup': 'self.cleanup', # clean chinese crap
		
		}
		
		return None
	
	
	def GET(self,path=None):
	
		print('GET Request')
	
		''' vars
		'''
		self.path = path
		
		# RAW
		self.raw = web.data()		

		# GET vars
		self.get_vars = self.build_get_vars()
		self.getpost_vars = self.get_vars
		
		# build page
		return self.run()
	
	
	def POST(self,path=None):
		
		print('POST Request')
	
		# This is required to for file uploads Input
		x = web.input()
		
		# vars
		self.path = path
		self.post = True

		# RAW
		self.raw = web.data()

		#debug
		#print(self.raw)

		# POST vars
		self.post_vars = self.build_post_vars()
		
		# GET vars
		self.get_vars = self.build_get_vars()
		
		self.getpost_vars = self.post_vars

		# remove GET vars from POST vars
		#self.remove_get_vars_from_post_vars()
	
		# build page
		return self.run()


	def build_get_vars(self):
		
		get_vars = web.webapi.rawinput("GET")
		
		return get_vars
	
	
	def build_post_vars(self):
		
		post_vars = web.webapi.rawinput("POST")
		
		#convert to dict
		tmp_post_vars = {}
		for key in post_vars:
			tmp_post_vars[key] = post_vars[key]
		post_vars = tmp_post_vars
		
		return post_vars
	
	
	def remove_get_vars_from_post_vars(self):
		
		# this fixes both a security vularibility and a functionality problem
		
		for key in self.post_vars:
			
			if key in self.get_vars:
				
				for value in self.get_vars[key]:
					
					self.post_vars[key].remove(value)
					
		return None


	def run(self):
		
		# vars
		
		# result of urls conf file
		available_urls = web.framework['urls']		
		
		path_config_files = []
		
		# cache the path for use by fnr
		self.cache['url'] = '%s/%s' %(web.ctx.home,self.path)
		self.cache['path'] = '/%s' %self.path
		self.cache['rurl'] = web.ctx.env.get('HTTP_REFERER')
		
		# convert the requested url into a  "/" delimited list
		url_list = self.path.split('/')
		
		if url_list[0] == '':
			url_list.pop(0)
		
		url_list.insert(0,'/')

		# convert the requested url back into a string with leading /
		url_string = url_list[0]+"/".join(url_list[1:])
		
		# compare visitor url with urls in url config
		requested_url = url_string
		
		for i in range(0,len(available_urls)):
			
			# this should return one dict key which is the url segment
			for available_url in available_urls[i]:
				
				#debug
				#print(available_url)
				#print("Type: "+ str(type(available_url)))
				
				r = "%s/"%requested_url.lower()
				a = "%s/"%available_url.lower()
				
				# if the requested url starts with the available url it is a hit
				if r.startswith(a):
					
					#debug
					#print("hit")
					
					# get a list of configuration files to load for this url
					path_config_files = available_urls[i][available_url].get('conf',[])
					
					# allow conf to be a string.  convert to list
					if isinstance(path_config_files,str):
						path_config_files = [path_config_files]
					
					# convert the requested url into a list delmitied by a slash (/)
					# filter removes and empty items casued by multiple slashes (//)
					requested_url_list = list(filter(None, requested_url.split("/")))
					
					# convert the available url into a list delmitied by a slash (/)
					
					available_url_list = list(filter(None, available_url.split("/")))
					
					# remove the available url from the requested url to get the path vars
					path_vars = requested_url_list[len(available_url_list):]
					
					# view name
					view_name = a
					
					''' Need to fid a way to abstract this
					'''
					# config hacks
					page_cache = False
					if 'cache' in available_urls[i][available_url]:
						page_cache = True
						
					if 'noindent' in available_urls[i][available_url]:
						self.attributes['noindent'] = True						

					if 'keepmarkers' in available_urls[i][available_url]:
						self.attributes['keepmarkers'] = True

					if 'header' in available_urls[i][available_url]:
						self.attributes['header'] = available_urls[i][available_url]['header']
						
					if 'debug' in available_urls[i][available_url]:
						self.attributes['debug'] = True						

					''' Will be resolved in future release
					'''


		# check for configuration files
		if len(path_config_files) == 0:
			
			print("Config Error:  No configuration files were found for the url '%s'." %url_string)


			gfx_agents = [
				"Chrome",
				"MSIE",
				"Firefox",
				"Safari",
				"AppleWebKit",
				"Gecko",
				"Dalvik",
			]

			for item in gfx_agents:
				if item in web.ctx.env['HTTP_USER_AGENT']:
			
					message_404 = '''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>404 Not Found</title>
</head><body>
<h1>Not Found</h1>
<p>The requested URL %s was not found on this server.</p>
<hr>
<address>WebYAML Application Server</address>
</body></html>''' %requested_url
			
					raise web.notfound(message_404)
					
			raise web.notfound()

		'''Page Caching - This cache is a copy of final output generated by WebYAML
		'''
		if page_cache:
			
			# is page in cache?
			cache_file = "cache/_:_%s" %url_string.strip("/").replace("/","_:_")
			
			try:
				f = open(cache_file,'r')
				output = f.read()
				f.close()
				
				print('found cache file')
				
				return output
				
			except IOError:
				
				print("cache file '%s' not found" %cache_file)
				# the page will still be generated and saved.
		
		# assign path_vars as dict with keys arg0, arg1, etc...
		for i in range(0, len(path_vars)):
			self.path_vars['arg'+str(i)] = path_vars[i]
			
		# search for configuration cache
		if view_name in web.framework['configuration_object'].cache:
			
			# read configuration from cache
			self.conf = web.framework['configuration_object'].cache[view_name]
			
			#debug
			print("reading configuration for view '%s' from cache"%view_name)
			
		else:
			
			# load core config files
			path_config_files.insert(0,"conf/processors/core.cfg")
			
			# load configuration files		
			self.conf =  web.framework['configuration_object'].load(*path_config_files)
			
			# write configuration to cache
			web.framework['configuration_object'].cache[view_name] = self.conf
			
			#debug
			print("writing configuration for view '%s' to cache"%view_name)
		
		# debug
		print("URL: %s" % url_string)
		print("GET vars: "+str(dict(self.get_vars)))
		print("POST vars: "+str(self.post_vars))
		print("PATH vars: "+str(self.path_vars))


		'''Pre-processing
			Create the Content Tree
		'''
		
		# insantiate content tree with the conf and a reference to self
		c = classes.content.Content(self,self.conf)

		# debug
		print("Cache:")
		print(str(self.cache))
		print("Session:")
		print(self.session.vars)
		
		'''Mid-processing
			Some content elements may request a function to be executed
			after the content tree is created.
		
		if 'functions' in self.cache:
			for function in self.cache['functions']:
				function()
		'''
		
		
		'''Processing
			Render all elements in the Content Tree
		'''
		# render all elements in the tree
		output = c.render()
		
		'''Post-Processing
		'''
		if not self.attributes.get('keepmarkers'):
			# cleanup - remove any markers from output before returning
			pattern = re.compile(r'({{[\w|\(|\)|\.|\:|\-]+}})')
			markers = list(set(pattern.findall(output)))

			for marker in markers:
				output = output.replace(marker,'')

		
		'''Debugging
		'''
		if self.attributes.get('debug'):
			
			# add debugging information
			length = len(output)

			# timestamp
			self.end_time = datetime.datetime.now()
			
			duration_seconds = (self.end_time-self.start_time).seconds
			duration_microseconds = ((self.end_time-self.start_time).microseconds)/float(1000000)
			debug = '''
<div><pre>
	Size: %d
	Time: %s
<div></pre>
''' %(length, duration_seconds+duration_microseconds)

			output = debug+output
		
		'''Page Caching - Cache this page if required
		'''
		if page_cache:
			
			try:
				f = open(cache_file,'w')
				f.write(output)
				f.close()
				
				print("wrote cache file '%s'." %cache_file)
				
			except IOError:
				
				print("could not write cache file '%s' not found" %cache_file)
		
		''' page headers
		'''
		#print(self.attributes)
		#print(self.conf)
		if self.attributes.get('header'):
			
			if not isinstance(self.attributes['header'], list):
			
				self.attributes['header'] = [self.attributes['header']]
		
			for header in self.attributes['header']:
				
				# debug
				#print(header)
				
				eval('web.header(%s)' %header)
		
		return output
		
		
