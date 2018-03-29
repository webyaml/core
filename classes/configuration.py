# path:  classes
# filename: configuration.py
# description: application configuration class

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

#import datetime
import os
import re

''' internal imports
'''
import classes.content

''' classes
'''
class Configuration(object):
	
	def __init__(self):
		
		self.cache = {}
		self.cache['files'] = []		


	def load_views(self,*files):
		
		''' Load View configuration files
		'''
		
		available_urls = self.load(*files)
		
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

		# create an index of the urls
		url_index = []
		for item in tmp_available_urls:
			url_index.append(list(item.keys())[0])
		
		# sort the index
		sorted_url_index = sorted(url_index)
		
		# sort the available_urls
		sorted_available_urls = []
		
		for item in sorted_url_index:
			
			# append item from available_urls to sorted_available_urls
			sorted_available_urls.append(tmp_available_urls[url_index.index(item)])
		
		tmp_available_urls = sorted_available_urls
		
		return tmp_available_urls



	def load(self,*files):
		
		''' wrapper for loading configuration files
		'''
		
		self.cache['includes'] = []

		self.error = None
		
		# read urls conf file
		result = self.load_conf(*files)
		
		if not result:
			if self.error: 
				return self.error
			return 'Failed to load the config file %s' %conf_file
		
		return result


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
		result = self.simple_anchor_syntax(result)
		#debug
		#print(result)
		
		
		if not result:
			return False
			
		content = result
		
		#debug
		#print(content)
		
		
		''' Attempt to support redeclaring an anchor
			without getting found duplicate anchor error
		
			Starting from the bottom of the document
			rename duplicate anchors above
		'''
		
		#self.fix_redeclared_anchors(content)
		
		
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

			# add file to includes list
			self.cache['includes'].append(file)			
			
			# Is there a cache entry for file?
			if file in self.cache['files']:
				
				# has the file been changed since last entry?
				if self.cache['files'][file].get('site') and os.stat("%s" % file).st_mtime == self.cache['files'][file].get('mtime'):
					
					return "%s\n" %self.cache['files'][file]['content']				

				if self.cache['files'][file].get('core') and os.stat("core/%s" % file).st_mtime  == self.cache['files'][file].get('mtime'):
					
					return "%s\n" %self.cache['files'][file]['content']
			
			# cache needs to be updated for file
			if os.path.isfile("%s" % file):

				#debug
				#print("found file '%s' in local dir" % file)
				print("reading '%s'" %file)

				# read config file
				f = open(file, 'r')
				content = f.read()+"\n"
				f.close()
				
				self.cache['files'][file] = {}
				self.cache['files'][file]['site'] = True
				self.cache['files'][file]['content'] = content
				self.cache['files'][file]['mtime'] = os.stat("%s" % file).st_mtime 				
				
			# does configuration file exist in framework dir
			elif os.path.isfile("core/%s" % file):
				
				print("reading '%s'" %file)
				
				#debug
				#print("found file '%s' in core dir" % file)				
				
				# read config file
				f = open("core/%s" % file, 'r')
				content = f.read()+"\n"
				f.close()

				self.cache['files'][file] = {}
				self.cache['files'][file]['site'] = True
				self.cache['files'][file]['content'] = content
				self.cache['files'][file]['mtime'] = os.stat("core/%s" % file).st_mtime 				
				
			# configuration not found
			else:
				
				# debug
				print("Config Error:  The configuration file '%s' was not found." % file)
				
				return False
			
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
			
			if line.strip().startswith("**"):
				line = line.replace("**", "<<: *")
			
			output += '%s\n' % line

		return output


	def fix_redeclared_anchors(self,input):

		''' Attempt to support redeclaring an anchor
			without getting found duplicate anchor error
		
			Starting from the bottom of the document
			rename duplicate anchors above
		'''		
		
		# search yaml for imports
		output = ""
		
		#debug
		#print(input)
		
		for line in input.split('\n'):
			
			m = re.search('([^\s]+):\ &([^\s](.*))$', line)
			if m:
				
				#print(m.group(1))
				print(m.group(2))
				
				if len(m.group(2).split('#')[0].strip().split(" ")) > 1:
					print('named anchor is a string')
					
				

		return input		


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



