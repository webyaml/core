# path: 
# filename: url.py
# description: application URL class

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
import os
#import sys
import yaml
import re
#import copy

import datetime

''' internal imports
'''
import classes.content

''' classes
'''
class URL(object):
	
	def __init__(self):

		''' vars
		'''
		
		# timestamp 
		self.start_time = datetime.datetime.now()
		
		# urls
		self.urls_config_file = 'conf/urls.cfg'
		self.urls = []
		
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
		self.cache['includes'] = []
		#self.error = None
		self.raw = {}
		self.attributes = {}
		
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
		
		'''
		for key in get_vars:
			
			# convert string to list
			if isinstance(get_vars[key],str):
				get_vars[key] = [get_vars[key]]
		'''
		
		return get_vars
	
	
	def build_post_vars(self):
		
		post_vars = web.webapi.rawinput("POST")
		
		#convert to dict
		tmp_post_vars = {}
		for key in post_vars:
			tmp_post_vars[key] = post_vars[key]
		post_vars = tmp_post_vars
		
		'''
		for key in post_vars:
			
			# convert string to list
			if isinstance(post_vars[key],str):
				post_vars[key] = [post_vars[key]]
		'''
		
		return post_vars
	
	
	def remove_get_vars_from_post_vars(self):
		
		# this fixes both a security vularibility and a functionality problem
		
		for key in self.post_vars:
			
			if key in self.get_vars:
				
				for value in self.get_vars[key]:
					
					self.post_vars[key].remove(value)
					
		return None


	def run(self):
		
		# cache the path for use by fnr
		
		''' This needs to be moved somewhere else
		'''
		#self.cache['path'] = "/"+self.path
		self.cache['rurl'] = web.ctx.env.get('HTTP_REFERER')
		
		# convert the requested url into a  "/" delimited list
		url_list = self.path.split('/')
		
		if url_list[0] == '':
			url_list.pop(0)
		
		url_list.insert(0,'/')

		# convert the requested url back into a string with leading /
		url_string = url_list[0]+"/".join(url_list[1:])
		
		# read urls conf file
		result = self.load_conf(self.urls_config_file)
		if not result:
			if self.error: 
				return self.error
			return 'Failed to load the urls config file'

		available_urls = result
		
		#debug
		#print(available_urls)
		
		
		# modify urls to include aliases
		tmp_available_urls = []
		for item in available_urls:
			
			for path in item:
				
				tmp_available_urls.append(item)
	
				aliases =  item[path].get('alias')
				
				if aliases:
					
					# allow aliases to be a string. convert to list
					if isinstance(aliases,str):
						aliases = [aliases]
					
					if isinstance(aliases,list):
						
						for alias in aliases:
					
							tmp_item = {}
							tmp_item[alias] = item[path]
							
							tmp_available_urls.append(tmp_item)
		
		available_urls = tmp_available_urls
		
		#debug
		#print(available_urls)
		
		# create an index of the urls
		url_index = []
		for item in available_urls:
			url_index.append(item.keys()[0])
		
		# sort the index
		sorted_url_index = sorted(url_index)
		
		# sort the available_urls
		sorted_available_urls = []
		
		for item in sorted_url_index:
			
			# append item from available_urls to sorted_available_urls
			sorted_available_urls.append(available_urls[url_index.index(item)])
		
		available_urls = sorted_available_urls
		
		#debug
		#print(available_urls)
		
		# build list of config files for url
		
		# compare visitor url with urls in url config
		requested_url = url_string
		
		#debug 
		#print("Full URL: "+str(requested_url))
		
		for i in range(0,len(available_urls)):
			
			# this should return one dict key which is the url segment
			for available_url in available_urls[i]:
				
				#debug
				#print(available_url)
				
				# if the requested url starts with the available url it is a hit
				if requested_url.lower().startswith(available_url.lower()):
					
					#debug
					#print("hit")
					
					# get a list of configuration files to load for this url
					path_config_files = available_urls[i][available_url].get('conf',[])
					
					# allow conf to be a string.  convert to list
					if isinstance(path_config_files,str):
						path_config_files = [path_config_files]
					
					# convert the requested url into a list delmitied by a slash (/)
					requested_url_list = filter(None, requested_url.split("/"))
					
					# convert the available url into a list delmitied by a slash (/)
					available_url_list = filter(None, available_url.split("/"))
					
					# remove the available url from the requested url to get the path vars
					path_vars = requested_url_list[len(available_url_list):]
					
					# does this url allow caching?
					page_cache = False
					if 'cache' in available_urls[i][available_url]:
						page_cache = True
						
					if 'noindent' in available_urls[i][available_url]:
						self.attributes['noindent'] = True						

					if 'keepmarkers' in available_urls[i][available_url]:
						self.attributes['keepmarkers'] = True

					if 'header' in available_urls[i][available_url]:
						self.attributes['header'] = available_urls[i][available_url]['header']					
					
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

		
		# assign path_vars as dict with keys arg0, arg1, etc...
		for i in range(0, len(path_vars)):
			self.path_vars['arg'+str(i)] = [path_vars[i]]
			
		# check for configuration files
		if len(path_config_files) == 0:
			
			return "Config Error:  No configuration files were found for the url '%s'." %url_string
		
		
		# load core config files
		
		# add error handling
		path_config_files.insert(0,"conf/processors/core.cfg")
		
		
		# concatenate and read configuration files
		result =  self.load_conf(*path_config_files)
		
		#debug 
		#print(result)
		
		if not result:
			if self.error: 
				return self.error
			return False
		
		self.conf = result
		
		# debug
		print("URL: %s" % url_string)
		print("GET vars: "+str(dict(self.get_vars)))
		print("POST vars: "+str(self.post_vars))
		print("PATH vars: "+str(self.path_vars))


		'''Pre-processing
			Create the Content Tree
		'''
		
		# insantiate content tree with the conf and a reference to self
		c = classes.content.Content(self.conf,self)

		# debug
		print("Cache:")
		print(str(self.cache))
		print("Session:")
		print(self.session.vars)
		
		'''Mid-processing
			Some content elements may request a function to be executed
			after the content tree is created.
		'''
		if 'functions' in self.cache:
			for function in self.cache['functions']:
				function()
		
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
		if 'debug' in self.conf and self.conf['debug']:
			
			# add debugging information
			length = len(output)

			# timestamp
			self.end_time = datetime.datetime.now()
			
			duration_seconds = (self.end_time-self.start_time).seconds
			duration_microseconds = ((self.end_time-self.start_time).microseconds)/float(1000000)
			debug = '''
				<pre>
					Size: %d
					Duration: %s
				</pre>
				''' %(length, duration_seconds+duration_microseconds)

			output += debug
		
		'''Page Caching
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
				
				print(header)
				
				eval('web.header(%s)' %header)
		
		return output
		
		
	def read_files(self,files):
		
		#debug
		#print(files)
		
		# vars
		output = ''
		
		for file in files:
			
			#debug
			#print("looking for file '%s'" % file)			
			
			# skip if this file already been included?
			if file in self.cache['includes']:
				
				#debug
				#print("file '%s' already included" % file)
				
				continue
			
			# does configuration file exist in local dir
			if os.path.isfile("%s" % file):

				#debug
				#print("found file '%s' in local dir" % file)

				# read config file
				f = open(file, 'r')
				content = f.read()+"\n"
				f.close()
			
			# does configuration file exist in framework dir
			elif os.path.isfile("core/%s" % file):
				
				#debug
				#print("found file '%s' in core dir" % file)				
				
				# read config file
				f = open("core/%s" % file, 'r')
				content = f.read()+"\n"
				f.close()
			
			# configuration not found
			else:
				
				# debug
				print("Config Error:  The configuration file '%s' was not found." % file)
				
				return False
			
			if content.startswith('cache'):

				# add file to cache
				self.cache['includes'].append(file)
				
				# remove first line from file
				content = "\n".join(content.split('\n')[1:])
			
			output += "%s\n" %content
			
		return output


	def includes(self,content,indentation=0):
		
		# search yaml for imports
		output = ""
		
		#debug
		#print(content)
		
		for line in content.split('\n'):
			
			line =  line.replace("\t","    ")
			
			if line.strip().startswith("include "):
				
				# debug
				#print("FOUND an INCLUDE")
				
				result = self.read_files(line.strip().split()[1:])
				
				# debug
				#print(result)
				
				if result == False:
					return False
				
				result = self.includes(result,(len(line) - len(line.lstrip(' '))))
				if not result:
					
					print("not output from includes")
					
					return False				
				
				output += result
				
			else:
				
				output += '%s%s\n' %(" "*indentation, line)

		return output


	def simple_anchor_syntax(self,input):
		
		# search yaml for imports
		output = ""
		
		#debug
		#print(input)
		
		for line in input.split('\n'):
			
			#line =  line.replace("\t","     ")
			
			if line.strip().startswith("**"):
				
				line = line.replace("**", "<<: *")
				
			output += '%s\n' % line

		return output



	def yaml_error_display(self,e,content):

		''' YAML debug helper
			print combined yaml file with line numbers
		'''
		
		print(e)

		tmp_content = ''
		
		i = 1
		for line in content.split('\n'):
			
			line = line.replace("<","&lt;").replace(">","&gt;")
			
			
			tmp_content += '%d\t%s\n'%(i,line)
			i += 1
		
		self.error = '''%s

%s''' %(str(e),tmp_content)


	def load_conf(self,*files):
		
		# vars
		conf = False
		
		result = self.read_files(files)
		
		#debug
		#print(result)
		
		if not result:
			
			return False
		
		# add includes to configuraion file
		result = self.includes(result)
		#debug
		#print(result)
		
		# replace simple anchor syntax with yaml syntax
		
		# **anchor:
		#     vs
		# <<: *anchor
		
		result = self.simple_anchor_syntax(result)
		#debug
		#print(result)
		
		
		if not result:
			return False
			
		content = result
		
		#debug
		#print(content)
		
		try:
			conf = yaml.load(content)
			
		except yaml.parser.ParserError as e:
			
			return self.yaml_error_display(e,content)
			
		except yaml.composer.ComposerError as e:
			
			return self.yaml_error_display(e,content)
			
		except yaml.scanner.ScannerError as e:
			
			return self.yaml_error_display(e,content)

		#debug 
		#print(conf)
		
		return conf
