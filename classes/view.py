# path: 
# filename: url.py
# description: application URL class
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
import lib.marker.methods

''' classes
'''
class View(object):
	
	def __init__(self):

		''' vars
		'''
		
		self.error = None # is this still used?
		
		
		# timestamp - used by debug
		self.start_time = datetime.datetime.now()
		
		# web.py sessions
		try:
			self.session = web.ctx.session #WSGI application
		except AttributeError:
			self.session = session #Cherry webserver
		
		# debug 
		#self.session.kill() 
		
		# urls.cfg
		self.urls_config_file = 'conf/urls.cfg'
		
		
		# top/view Vars
		self.path_vars = {}
		self.get_vars = {}
		self.post_vars = {}
		self.post = False
		self.marker_map = {}
		
		self.cache = {}
		self.raw = {}
		self.attributes = {}

		# session vars
		if 'vars' not in dir(self.session):
			self.session.vars= {}

		
		# marker attributes
		self.marker_map = {

			# Attributes
			
			# Caches
			'cache': 'self.top.cache',
			'session': 'self.top.session.vars',
			
			# URI/GET/POST
			'path': 'self.top.path_vars',
			'get': 'self.top.get_vars',
			'post': 'self.top.post_vars',
			'getpost': 'self.top.getpost_vars',
			'raw': 'self.top.raw',			

			# ATTRIBUTES
			'this': 'self.attributes',	
			'parent': 'self.parent.attributes',
			'top': 'self.top.attributes',
			'view': 'self.view.attributes',
			'data': 'self.data',
		
		}
		
		# add marker methods
		self.mmethods = lib.marker.methods
		self.marker_map.update(self.mmethods.marker_map)
		
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
		
		#print("POST vars: "+str(self.post_vars))
		
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
		# but it assumes that get vars come before post vars and has been problematic
		# this method is not currently being used
		
		for key in self.post_vars:
			
			if key in self.get_vars:
				
				for value in self.get_vars[key]:
					
					self.post_vars[key].remove(value)
					
		return None


	def run(self):
		
		# vars
		
		# result of urls conf file
		web.framework['urls']  = web.framework['configuration_object'].load_views(self.urls_config_file)
		available_urls = web.framework['urls']		
		
		content_config_files = []
		
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
		requested_url = url_list[0]+"/".join(url_list[1:])
		self.requested_url = requested_url
		
		# compare visitor url with urls in url config	
		for i in range(0,len(available_urls)):
			
			# this should return one dict key which is the url segment
			for available_url in available_urls[i]:
				
				#debug
				#print(available_url)
				#print("Type: "+ str(type(available_url)))
				
				r = "%s/"%requested_url.lower()
				a = "%s/"%available_url.lower()
				
				# if the requested url starts with the available url then the request is part of a path
				if r.startswith(a):

					'''	View Confiuration
					'''

					# view name - used for caching content configuration
					self.attributes['name'] = a

					# assign/update attributes - supports inheritence /1/2/ inherits from /1
					self.attributes.update(available_urls[i][available_url])
					

					'''	This sting to list conversion should happen at another level
					'''
					# get a list of configuration files to load for this url
					content_config_files = self.attributes.get('conf',[])
					
					# allow conf to be a string.  convert to list
					if isinstance(content_config_files,basestring):
						content_config_files = [content_config_files]
					
					# update conf attribute
					self.attributes['conf'] = content_config_files
					
					
					'''	PATH vars
					'''					
					# filter removes any empty items casued by multiple slashes (//)
					requested_url_list = list(filter(None, requested_url.split("/")))
					available_url_list = list(filter(None, available_url.split("/")))
					
					# remove the available url from the requested url to get the path vars
					path_vars = requested_url_list[len(available_url_list):]
		
		
		# Handle 404 errors
		if not 'conf' in self.attributes or len(self.attributes['conf']) == 0:

			print("Config Error:  No configuration files were found for the view '%s'." %requested_url)
			
			return self.error404()


		''' Custom Headers
		'''
		if 'header' in self.attributes:
			
			if not isinstance(self.attributes['header'], list):
			
				self.attributes['header'] = [self.attributes['header']]
		
			for header in self.attributes['header']:
					
				eval('web.header(%s)' %header)
				
		else:
			web.header('Content-Type','text/html; charset=utf-8')
		
		
		'''Cache Output - READ
			This cache is used to make static copies of final output generated by WebYAML.
			If your view requires dynamic processing DO NOT use this type of cache.
		'''
		if 'cache' in self.attributes and self.attributes['cache'] == 'output':
			
			cache_file = "cache/_:_%s" %str(requested_url.strip("/").replace("/","_:_"))
			
			# is page in cache?
			try:
				f = open(cache_file,'r')
				output = f.read()
				f.close()
				
				#debug
				#print('found cache file')
				
				return output
				
			except IOError:
				
				# warn - the page will still be generated
				print("cache file '%s' not found" %cache_file)
					
		
		'''	This view is not cached, therefore path vars must be assigned
		'''
		# assign path_vars as dict with keys arg0, arg1, etc...
		for i in range(0, len(path_vars)):
			self.path_vars['arg'+str(i)] = path_vars[i]
		
		# debug
		print("URL: %s" % requested_url)
		print("GET vars: "+str(dict(self.get_vars)))
		print("POST vars: "+str(self.post_vars))
		print("PATH vars: "+str(self.path_vars))

		
		# CACHE INPUT
		
		''' 	The view configuration file may be cached in memory.
			If the configuration is not found load from file(s).
		'''
		if 'cache' in self.attributes and self.attributes['cache'] == 'input':
			
			# search for configuration cache
			if self.attributes['name'] in web.framework['configuration_object'].cache['conf']:
				
				# read configuration from cache
				self.conf = web.framework['configuration_object'].cache['conf'][self.attributes['name']]
				
				#debug
				#print("reading configuration for view '%s' from cache"%self.attributes['name'])
				
			else:
				
				# load core config files
				content_config_files.insert(0,"conf/processors/core.cfg")
				
				# load configuration files		
				self.conf =  web.framework['configuration_object'].load(*content_config_files)
				
				# write configuration to cache
				web.framework['configuration_object'].cache['conf'][self.attributes['name']] = self.conf
				
				#debug
				#print("writing configuration for view '%s' to cache"%self.attributes['name'])
			
		else:
			# load core config files
			content_config_files.insert(0,"conf/processors/core.cfg")
			
			# load configuration files		
			self.conf =  web.framework['configuration_object'].load(*content_config_files)
		
		
		''' Generate Output	
		'''
		#Create the Content Objects and perform Pre-processing
		c = classes.content.Content(self,self.conf)
		
		#Render all elements of the Content Tree
		output = c.render()
		
		
		# debug
		print("Cache:")
		print(self.cache)
		print("Session:")
		print(self.session.vars)		
		
		
		'''	Unless otherwise indicated remove any remaining markers
		'''
		# Remove any markers from output before returning
		if 'keepmarkers' not in self.attributes:
			
			pattern = re.compile(r'({{[\w|\(|\)|\.|\:|\-]+}})')
			markers = list(set(pattern.findall(output)))

			for marker in markers:
				output = unicode(output.replace(marker,''))

		
		'''	Extra Debugging output
		'''
		if 'debug' in self.attributes:
			
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
		
		
		'''	Cache Output - Write
			This cache is used to make static copies of final output generated by WebYAML.
			If your view requires dynamic processing do not use this type of cache.
		'''
		if 'cache' in self.attributes and self.attributes['cache'] == 'output':
			cache_file = "cache/_:_%s" %str(requested_url.strip("/").replace("/","_:_"))
			
			try:
				f = open(cache_file,'w')
				f.write(output)
				f.close()
				
				print("wrote cache file '%s'." %cache_file)
				
			except IOError:
				
				print("could not write cache file '%s' not found" %cache_file)
		
		
		'''	Return Output
		'''
		
		return output
		



	def error404(self):
		
		# vars
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
			if 'HTTP_USER_AGENT' in web.ctx.env and item in web.ctx.env['HTTP_USER_AGENT']:
				message_404 = '''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>404 Not Found</title>
</head><body>
<h1>Not Found</h1>
<p>The requested URL %s was not found on this server.</p>
<hr>
<address>WebYAML Application Server</address>
</body></html>''' %self.requested_url
		
				raise web.notfound(message_404)
				
		raise web.notfound()
			
