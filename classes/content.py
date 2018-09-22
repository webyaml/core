# path: core/
# filename: content.py
# description: WSGI application content tree
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
import os.path
import sys
import imp
import traceback

import urllib
import datetime
from decimal import Decimal

''' internal imports
'''
#import functions

''' classes
'''
class Content(list):

	def __init__(self,parent,conf):
		
		# super list class  - init with empty list
		super(Content, self).__init__()
		
		# vars
		self.attributes = conf # attributes, the 'content block'
		self.parent = parent # parent object
		#self.attributes['parent'] = self.parent.attributes # this adds support for {{parent[:parent[:parent]etc.]:attribute}}
		
		if 'top' not in dir(self.parent):
			self.parent.top = self.parent
		self.top = self.parent.top # top object
		
		self.view = self.top #migrate to this instead of top
		
		self.elementObj = None # placeholder for elementObj
		self.data = None
		self.marker_map = self.top.marker_map
		
		# main

		'''	this is a recursive class.
			working root to branch above this point
		'''
		
		# perform preprocessing
		self.process(self.attributes.get('process',{}))
		
		# build a tree of sub Content objects (a list of lists)
		self.tree(conf) # recursive function
		
		'''	an end node has been reached
			working branch to root below this point
		'''
		
		# init elementObj
		self.init_element()
		
		
		return None


	def process(self,conf):
		
		if isinstance(conf,dict):
			
			conf = [conf]
			
		if not isinstance(conf,list):
			
			print('process conf is unparseable')
			
			return False
			
		for item in conf:
			
			# log
			if item.get('log'):
				print(self.fnr(item['log']))
			
			#vars
			processor_type = item.get('type')
			
			if not processor_type:
				return False
			
			''' Dynamically load processors
			'''
			m = ".".join(processor_type.split('.')[:-1])
			c = ".".join(processor_type.split('.')[-1:])
			
			_class = self.loadmodule(m,c)
			
			if not _class:
				
				return False
			
			# instanciate element object
			self.processorObj = _class(self,item)
			
			# run processor
			try:
				output = self.processorObj.run()
				
				# debug
				#print('Processor Output: - %s' %str(output))
				
				if output == True:
					
					# convert bool True to string
					if item.get(True):
						item['true']	= item[True]	
					
					if item.get('true'):
						
						# sub content
						if isinstance(item['true'], dict) and item['true'].get('content'):
							
							self.tree({'content': item['true']})
							
							continue
						
						# sub process
						self.process(item['true']) #recurse
						
					else:
						continue
						
				elif output == False:
					
					# convert bool False to string
					if item.get( False ):
						item['false'] = item[False]	
				
					if item.get('false'):
						if isinstance(item['false'], dict) and item['false'].get('content'):
							
							self.tree({'content': item['false']})
							return False
							
						self.process(item['false']) #recurse
						
					else:
						#return False
						
						# are we in a list?  how to handle differntly
						continue
						
						
						
				# if process returns something other than false make it false
				else:
					
					return False			
			
			except: traceback.print_exc()
		
		
		return True

	def loadmodule(self,m,c):
		
		# debug
		#print(m)
		#print(c)
		
		# does the module exist in site directory
		if os.path.isfile("%s.py" %m.replace('.','/')):
			
			print('found a local module - importing')
			
			try:
				_module = imp.load_source(m,"%s.py" %m.replace('.','/'))
				
			except: 
				
				traceback.print_exc()
				
				return False
			
		# does the module exist in core directory
		elif os.path.isfile("core/%s.py" %m.replace('.','/')):
			
			try:
				#_module = imp.load_source(m,"core/%s.py" %m.replace('.','/'))
				__import__(m)
				_module = sys.modules[m]  #load module
				
			except: 
				
				traceback.print_exc()
				
				return False
			
		else:
			print("Could not find the the module '%s'." %m)
			
			return False

		# load class
		try:
			_class = getattr(_module,c)  
			
		except AttributeError:
			
			print("Could not find the class '%s' in the module '%s'." %(c,m))
			
			return False
		
		except: 
			
			traceback.print_exc()
			
			return False
			
		return _class


	def tree(self,conf):
		
		''' Recursivly create Content objects
		'''
		
		# Vars
		
		if isinstance(conf,basestring) :
			
			print("Warn: classes.content.tree() performing eval()")
			conf = eval(conf)
		
		if conf.get('content'):

			# convert dict to list
			if isinstance(conf['content'],dict):
				conf['content'] = [conf['content']]
			
			# recurse
			for item in conf['content']:
				try:
					self.append( Content(self,item) )
					
					'''
					except MyError:
					
						item = {errorcontent}
						self.append(Content(self,item))
					
					'''
					
					
				except: traceback.print_exc()
		
		
		return None


	def init_element(self):
		
		# Dynamically import an Element object
		
		element_type = self.attributes.get('type','classes.element.Element') # type/class of element or default
		m = ".".join(element_type.split('.')[:-1]) # module name and path
		c = ".".join(element_type.split('.')[-1:]) # class name
		
		_class = self.loadmodule(m,c)
		
		if not _class:
			
			return False


		# instanciate Element object
		#self.elementObj = _class(self)

		
		# making an exception for calling processor instead of element
		
		try:
		
			# instanciate Element object
			self.elementObj = _class(self)

		except Exception as e:
			
			# There was an error
			
			# copy the content block (conf) for showing in error message
			import copy
			orginal_conf = copy.deepcopy(self.attributes)
			
			self.attributes = {}
			self.attributes['noindent'] = True
			self.attributes['value'] = '''
<style>
	.error {
		border: 2pt solid #ea8a8a;
		padding-left: 10px;
		padding-right: 10px;
		border-radius: 10px;
		background: #ffefef;
	}
</style>
<pre class="error">
<h3>Content Error</h3>
There is an error in this content block:

{{yaml(e:code).html_escape()}}

Type: {{e:type}}
Message: {{e:message}}

{{e:suggestion}}

Stacktrace:
{{yaml(e:stack)}}
</pre>
'''
			self.attributes['e'] = {}
			self.attributes['e']['message'] = e.message
			self.attributes['e']['type'] = e.__repr__()			
			self.attributes['e']['code'] = orginal_conf
			self.attributes['e']['code'].pop('content', None)
			
			if e.message == "__init__() takes exactly 3 arguments (2 given)":
				
				self.attributes['e']['suggestion'] = '''
Suggestion: This error usually means that a processor was called as an element.

Try this content block instead:

{{yaml(e:suggestedcode).html_escape()}}
'''
			
			self.attributes['e']['suggestedcode'] = {"process": orginal_conf}
			#self.attributes['e']['stack'] = traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback,10)
			
			return self.init_element()
		
		
		return None

	
	def render(self):
		
		''' Render Element objects in tree
		'''
		
		#vars
		output = ''
		
		
		# render child elements
		for item in self:
			if isinstance(item, type(self)):
				output += item.render() #recurse
		
		# log entry if requested
		if 'log' in self.attributes:
			print(self.fnr(self.attributes['log']))
		
		# render this element
		output = unicode(self.elementObj.render())+output
		
		# split wrap
		wrap = self.attributes.get('wrap','|').split("|",1)
		if len(wrap) == 1:
			wrap.append('')
		
		# Helpers for API formating

		if 'nomarkup' in self.attributes:
			
			#print('nomarkup')
			
			return  wrap[0]+output+wrap[1]

		if 'singlemarkup' in self.attributes:
			
			#print('singlemarkup')
			
			return  self.fnr(wrap[0]+output+wrap[1],1)
		
		if 'noindent' in self.attributes or 'noindent' in self.top.attributes:
			
			#print('noindent')
			
			# double markup
			return  self.fnr(wrap[0]+output+wrap[1])
		
		# markup with indent
		return  self.fnr(self.indent("%s\n%s\n%s" %(wrap[0],output,wrap[1])))
	

	'''	merge with render
	'''

	def indent(self,input,prefix="  "):
		
		# vars
		output = ''
		
		if self.top == self.parent:
			return input
		
		for line in input.split('\n'):
			output += prefix+line+"\n"		
		
		#print(type(output))
		
		return output.rstrip("\n")


	''' 	Regenerate  This the core of the framework
	'''

	def fnr(self,template,limit=10,**kwargs):
		
		binary = False
		if 'binary' in kwargs:
			print('binary')
			binary = True
			

		#debug
		#print(type(template))
		
		count = 0
		
		while True:
		
			# copy the template.  this copy will be destroyed searching for markers
			template_copy = template
			template_original = template # second copy for caparision later
			
			'''	find all the markers 
				This does not support nested markers!
			'''
			
			# does this template include any markers?
			try:
				start = unicode(template_copy).index('{{')
				end = unicode(template_copy).index('}}',start)
			
			# no markers found, return input
			except ValueError:
				
				return template
			
			# markers found
			# find markers
			markers = []
			while True:
				
				# find the next marker's endpoints
				try:
					start = template_copy.index('{{')
					end = template_copy.index('}}',start)
				except ValueError:
					
					# all markers found
					break
				
				# add the marker to list
				markers.append(template_copy[start+2:end])
				
				# truncate template
				template_copy = template_copy[end+2:]
			
			# debug
			#print('markers: %s' %str(markers))

			'''	Parse each marker into a stack.
			'''
			for marker in markers:
				
				# vars
				quote_state = False
				nested_state = False
				quote_chr = None
				quote_characters = ["'",'"']
				escape_characters = ["\\"]
				
				value = []
				stack = []
				
				markup_value = None
				
				# parse this marker character by character
				for i in range(0,len(marker)):
					
					# debug
					#print("".join(value))
					
					# skip escape characters
					if marker[i] in escape_characters:
						continue
					
					# record charater after escpae character
					if i > 0 and marker[i-1] in escape_characters:
						value.append(marker[i])
						continue
					
					# start quote
					if not quote_state and marker[i] in quote_characters:
						quote_state = True
						quote_chr = marker[i]
						
						# record litteral character
						value.append("|")
						continue

					# end quote
					if quote_state and marker[i] == quote_chr:
						quote_state = False
						quote_chr = None
						continue				

					# data inside of methods
					if i < len(marker)-1 and not quote_state and marker[i] == "(" and marker[i+1] != ")":
						if value:
							stack.append(''.join(value))
						value = []
						nested_state = True
						continue
					
					# data inside of methods
					if nested_state and i < len(marker) and not quote_state and marker[i] == ")":
						if value:
							stack.insert(0, ''.join(value))
						value = []
						
						# syntax errrs may cause '()()' in item
						stack[1] += "()"
						nested_state = False
						continue
					
					# seperators
					if not quote_state and marker[i] == ".":
						if value:
							stack.append(''.join(value))
						value = []
						continue
					
					# otherwise 
					value.append(marker[i])
					
					# debug
					#print(marker[i])
					
				# reached the end of the marker
				if value:
					stack.append(''.join(value))
				
				'''	Perform markup on input using markers
				'''
				for item in stack:
					
					# debug
					#print(item)
					
					
					''' begin - i am not sure if this really needed any more
					'''
					# string literals
					if item.startswith("|"):
						markup_value = item.lstrip("|")
						continue
					''' end
					'''
					
					# methods
					if item.endswith("()"):
						
						# search for methods in marker_map
						if item.rstrip("()") not in self.marker_map:
							print("WARN - '%s' is not a valid marker methods" %item)
							
							markup_value = item
							continue
						
						markup_value = eval(self.marker_map[item.rstrip("()")])(self,markup_value)
						continue
						
					# attributes
					if ":"  in item:

						items = item.split(":")
						object = items[0]
						
						#print(self.attributes)
						
						# is this a marker for a local attribute?
						if object in self.attributes:
							
							# yes prepend this: to marker
							items.insert(1,object)
							
							object = "this" 
						
						# is there a type for this marker
						if object not in self.marker_map:
							
							#debug
							#print("WARN - '%s' is not a valid fnr attribute in %s" %(object,item))
							#print(template)
							break						
						
						keys = self.colon_seperated_to_brackets(":".join(items[1:]))
					
						# debug
						#print(self.marker_map[object])
						#print(keys)
						#print(markup_value)
						
						try:
							markup_value = eval(self.marker_map[object]+keys)

						except KeyError:
							
							#debug
							#print('KeyError in Content.fnr()')
							
							pass
							
						except TypeError:
							
							# debug
							print('TypeError in Content.fnr()')
							
							pass
							
						except: traceback.print_exc()
						
						continue

					# if this attribute is for the local scope (this)
					if item in eval(self.marker_map['this']):
						markup_value = eval(self.marker_map['this'])[item]
						continue
					
					# attribute object (or raw)
					if item in self.marker_map:
						markup_value = eval(self.marker_map[item])
						continue
					
					# end of loop
				
				# replace marker with markup_value
				if markup_value or markup_value == '' or markup_value == 0 or markup_value == []:
					
					if binary:
						
						# the markup_value is a binary object and should be considered to be a string
						
						template = template.replace("{{%s}}" %marker, str(markup_value))
						
					else:
					
						if not isinstance(markup_value,unicode):
							
							try:
							
								markup_value = unicode(markup_value)
								
							except UnicodeDecodeError:
								
								markup_value = unicode(markup_value.decode('UTF-8'))
								

						template = template.replace(u"{{%s}}" %marker, markup_value)
				
				'''debug - warning: lots of output, but this is useful if you need to see
					markups at this granular level.
				'''
				#print(marker,markup_value.__repr__())
				
			''' Can we make some sort of check here to see if there are markers that can still be replaced?
			'''
			
			if template == template_original:
				
				return template
				
			# increment count
			count += 1
			
			if limit == count:
				
				return template
				
			# iterate 
			
		return None


	# data handling
	def load_data(self,conf):
		
		'''	This method will load data into the current element or processor
			and optionally can be used to store the data for access by other
			elements and processors in the content tree.
		
			directives are attributes of a Data Object as defined in element and
			processor configurations
			
			data: # name given in config as specified by the element or processor
			
				# attributes
				value: # A pointer to data in marker syntax
				format: # the format of the value: csv, dict, int, json, list, python, string, xml, yaml (defaut=string)
				store: # (optional) name to store data as in self.top
				entry: # (optional) point in opject to load or store
				
				# csv attributes
				reader: list or dict (deafult=dict)
				kwargs:
					# will accpet any keyword arg for csv function
					delimter: # an optional delimer: ie: ";", "\t"
			
		'''
		
		# debug
		#print('clases.element.Element.load_data')	
		
		# conf check
		
		#debug 
		#print(conf)
		
		# value
		'''	This needs to be fixed to allow empty objects
		'''
		#if not conf.get('value'):
		#	print("error value not given")
		#	return False
		
		
		# format
		conf.setdefault('format','string')

		# store
		conf.setdefault('store',False)
		
		# data
		data = conf['value']
		
		if isinstance(data,basestring) and 'nomarkup' not in conf:
			
			# markup data
			data = self.fnr(data)

		# debug
		#print(data)
		
		# format data
		
		# CSV
		if conf['format'] == 'csv':
			
			#print('format is csv')
			
			import csv
			
			reader = conf.get('reader','dict')
			kwargs = conf.get('kwargs',{})
			
			if reader == 'list':

				try: 				
				
					tmp_data = csv.reader(data.split('\n'),**kwargs)
					self.data = []
					for item in tmp_data:
						if item:
							self.data.append(item)
				
				except: traceback.print_exc()			
				
			else:

				try:
				
					tmp_data = csv.DictReader(data.split('\n'),**kwargs)
					
					self.data = []
					for item in tmp_data:
						
						# clean up dictionary keys
						tmp_dict = {}
						for key in item:
							tmp_dict[key.strip()] = item[key].strip()
							
						self.data.append(tmp_dict)	
				
				except: traceback.print_exc()
		
		# dict
		if conf['format'] == 'dict':
			
			#print('format is dict')

			if isinstance(data, dict):
				self.data = data
			else:			
				try:
					self.data = eval(data)
				
					if not isinstance(self.data,dict):
					
						print('warning data not a dictionary')
						
				except: traceback.print_exc()
		
		# int
		if conf['format'] == 'int':
			
			#print('format is int')

			if isinstance(data, int):
				self.data = data
			else:
				try:
					self.data = eval(data)
				
					if not isinstance(self.data,int):
					
						print('warning data not a int')
						
				except: traceback.print_exc()

		# json
		if conf['format'] == 'json':
			
			#print('format is json')
			
			import json
			
			
			try:
				self.data = json.loads(data, parse_float=Decimal, strict=False)
			
			except: traceback.print_exc()		
		
		# list
		if conf['format'] == 'list':
			
			#print('format is list')
			
			#self.data = eval(data)
			#print('here')
			
			if isinstance(data, list):
				self.data = data
			else:
				try:
					self.data = eval(data)
				
					if not isinstance(self.data,list):
					
						print('warning - data not a list')
				except NameError:
					
					# Item not in top?
					pass
					
				except SyntaxError:
					
					# missing data obj?
					pass
					
				
				
				except: traceback.print_exc()
		
		# python
		if conf['format'] == 'python':
			
			#print('format is python')
			
			try:
				self.data = eval(data)
			
				print('python data is of the type %s' %type(self.data))
					
			except: traceback.print_exc()	
		
		# raw
		if conf['format'] == 'raw':
			
			#print('format is raw')
			
			self.data = data
			
		# string
		if conf['format'] == 'string':
			
			#print('format is string')
			
			self.data = unicode(data)
		

		# yaml
		if conf['format'] == 'xml':
			
			#print('format is xml')
			
			import xmltodict
			
			try:
				self.data = xmltodict.parse(data)
			
			except: traceback.print_exc()
		
		
		# yaml
		if conf['format'] == 'yaml':
			
			#print('format is yaml')
			
			import yaml
			
			try:
				self.data = yaml.load(data)
			
			except: traceback.print_exc()	
			
		# default (string)
		if not self.data:
			
			#print('format is default')
			
			self.data = unicode(data)


		# entry point
		if conf.get('entry'):
			
			if conf['entry'].startswith('{{') and conf['entry'].endswith('}}'):
				
				entry = self.colon_seperated_to_brackets(conf['entry'].lstrip('{{').rstrip('}}'))
				
				exec('self.data = self.data%s' %entry)
		
		# store
		if conf.get('store'):
			
			conf['store2']  = conf['store'] 
			
			# does conf['store'] have a prefix?
			
			#if parent in conf['store'] 
			
			if not ":" in conf['store2']:
				
				conf['store2'] = "top:%s" %conf['store']
			
			if conf['store2'].startswith('top:this'):
				
				conf['store2'] = conf['store2'].replace("top:this","attributes")
			
			# convert colons to dots
			
			conf['store2'] = conf['store2'].replace(":",".")
			
			#print(conf['store2'] )
			

			if 'merge' in conf and conf['store'] in self.top.marker_map:
				
				if eval('isinstance(self.%s, dict)' %conf['store2']):
				
					# merge with top item
					exec('self.%s.update(self.data)' %conf['store2'])
					
					# debug
					#print('updated top.%s with self.data' %conf['store'])

				if eval('isinstance(self.%s, list)' %conf['store2']):
				
					# merge with top item
					exec('self.%s.extend(self.data)' %conf['store2'])
					
					# debug
					#print('extended top.%s with self.data' %conf['store'])

				if eval('isinstance(self.%s, basestring)' %conf['store2']):
				
					# merge with top item
					exec('self.%s += self.data' %conf['store2'])
					
					# debug
					#print('concatonated top.%s and self.data' %conf['store'])
				
			else:
			
				# add to top
				print('self.%s = self.data' %conf['store2'])
				
				exec('self.%s = self.data' %conf['store2'])

				# add to top marker_map
				self.top.marker_map.update({conf['store']: 'self.%s' %conf['store2']})

				#print('stored self.data as top.%s' %conf['store'])
				
				
		#print(self.data)
		
		return True


	def colon_seperated_to_brackets(self,input):

		if input != "":
		
			input = unicode(input)
		
			# format input into a bracketed format
			
			# replace escaped colons
			input = input.replace("\:","_-_-_-_-_-_")
			
			# split segments on colons
			segments = input.split(":")
			
			output = ""
			
			for segment in segments:
				
				# debug
				#print(segment)
				
				# backwards compatibility
				if segment.startswith('|'):
					segment = segment.lstrip('|')
				
				
				# record digits as numbers
				if segment.isdigit():
					
					# add segment to entry
					output += "[%s]" %segment
					continue
					
				# reinstate colons in segments 
				segment = segment.replace("_-_-_-_-_-_",":")
				
				# escape quotes
				segment = segment.replace("'",r"\'").replace('"',r'\"')
				
				# add segment to entry
				output += "['%s']" %segment
				
			return output
			
		return input
			
	
