# path: core/
# filename: content.py
# description: WSGI application content tree

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
		
		if 'top' not in dir(self.parent):
			self.parent.top = self.parent
		self.top = self.parent.top # top object
		
		self.view = self.top #migrate to this instead of top
		
		self.elementObj = None # placeholder for elementObj
		self.data = None
		self.fnr_types = self.top.fnr_types
		
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
		
		if isinstance(conf,str) :
			
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
		self.elementObj = _class(self)
		
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
		output = self.elementObj.render()+output
		
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
		
		# Indent the output and wrap
		#print('indent')
		
		# double markup with indent
		return  self.fnr(self.indent("%s\n%s\n%s" %(wrap[0],output,wrap[1])))
	

	'''	merge with render
	'''

	def indent(self,input,prefix="  "):
		
		# vars
		output = ''
		
		if self.top == self.parent:
			return input
		
		for line in input.split('\n'):
			output += prefix+str(line)+"\n"		
		
		return output.rstrip("\n")	


	''' 	find and replace functions
		need to find a way to move these
	
	'''

	def int(self,obj):

		#debug
		#print('int')
		
		if isinstance(obj, str) and obj.strip().isdigit():
			return int(obj)
			
		return obj
	

	def split(self,obj):

		#debug
		#print('split')
		
		if isinstance(obj, str):
		
			delimiter = self.attributes.get('delimiter')
			if delimiter:
				return obj.split(delimiter)
				
			return obj.split()
			
		return obj
	

	def sha256(self,password):
		
		if not password:
			return password
		
		#debug
		#print('sha256')
		
		import crypt
		import random
		import string
		
		password = crypt.crypt(password, '$5$')
		
		return password


	def md5(self,password):
		
		if not password:
			return password		
		
		#debug
		#print('md5')
		
		import hashlib
		password = password.strip()
		return hashlib.md5(password).hexdigest()


	def dollar(self,f):
		
		''' Note: Needs to be a number formatter not specifc to USD
		'''

		#debug
		#print('dollar')
		
		if not isinstance(f,float):
			
			return 'fix me - dollar was not float'
			
		return "%.2f" %f


	def key_val_list(self,d):
		
		#debug
		#print('key_val_list')
		
		if not isinstance(d,dict):
			return d
		
		output = []
		for key in d:
			
			output.append({'key': key, 'val': d[key]})
		
		return output


	def count(self,l):
		
		#debug
		#print('count')
		
		if not isinstance(l,list):
			return l
		
		return len(l)


	def exists(self,obj):
		
		# debug
		#print('exists')
		#print('obj:'+str(obj))
		
		if isinstance(obj, str) and obj != '':
			return 'True'
			
		if obj:
			return 'True'
			
		return 'False'
	
	
	def singleline(self,obj):

		# debug
		#print('singleline')
		
		if not isinstance(obj,str):
			
			return ''
			
		output = []
		for line in obj.split('\n'):
			
			output.append(line.strip())
		
		return ' '.join(output)
	
	
	def strip(self,obj):

		# debug
		#print('strip')
		
		char = self.attributes.get('char', "")
		
		print(char)
		
		if isinstance(obj,str):
			
			return obj.strip("\n").strip("\r").strip(char).strip()
			
			#return obj.strip(char)
		
		''' #consider adding the following
		if isinstance(obj,list):
		'''
		
		return obj


	def escape(self,obj):
		
		''' escape single and double qoutes in strings.
		'''

		# debug
		#print('escape')
		
		if isinstance(obj,list):
			string = ", ".join(obj)
		
		if isinstance(obj,str):
			obj = obj.replace("'",r"\'").replace('"',r'\"')
		
		return str(obj)
	
	
	def escape_breaks(self,obj):
		
		''' escape single and double qoutes in strings.
		'''

		# debug
		#print('escape_breaks')
		
		if not isinstance(obj,str):
			
			return obj
			
		return str(obj.replace("\n",r"\\n").replace('\r',r'\\n'))

	
	def html_breaks(self,obj):
		
		''' convert line breaks to html breaks
		'''

		# debug
		#print('convert_breaks')
		#print(type(obj))
		
		if not isinstance(obj,str):
			
			return obj
			
		return str(obj.replace("\n",r"</br>"))
	
	
	def escape_markers(self,obj):
		
		''' escape braces in strings.
			this was added for dcoumetnation - it may not be needed
		'''

		# debug
		#print('escape_markers')
		
		if isinstance(obj,str):
			obj = str(obj.replace("{{",r"\{\{").replace('}}',r'\}\}'))
		
		return obj
	
	
	def _join(self,obj):

		# debug
		#print('_join')
		
		if isinstance(obj,list):
			obj = ", ".join(obj)
		
		return obj
	

	def _json(self,obj):
	
		# debug
		#print('_json')	
		#print(obj)
		
		import json
		import decimal
		import datetime
		
		def walk(subobj):
			
			if isinstance(subobj,list):
				
				for i in range(0,len(subobj)):
					
					subobj[i] = walk(subobj[i])
			
			if isinstance(subobj,dict):
				
				for key in subobj:
					
					subobj[key] = walk(subobj[key])
			
			if isinstance(subobj,str):
				
				subobj = self.fnr(subobj)
			
			# Hack
			if isinstance(subobj,datetime.datetime):
				
				# uses the local date function to convert to string
				subobj = self.date(subobj)

			# Hack
			if isinstance(subobj,decimal.Decimal):
				
				subobj = str(subobj)
			
			return subobj
		
		obj = walk(obj)
		
		return  json.dumps(obj)


	def _yaml(self,obj):
		
		# debug
		#print('_yaml')	
		#print(obj)
		
		import decimal
		import json
		import yaml		

		# tweak for utf-8
		def my_unicode_repr(self, data):
			return self.represent_str(data.encode('utf-8'))
		
		yaml.representer.Representer.add_representer(unicode, my_unicode_repr)
		
		obj = json.loads(self._json(obj))
		
		return yaml.dump(obj, allow_unicode=True, default_flow_style=False)

	
	def truncate(self,obj):

		# debug
		#print('truncate')	
		
		if isinstance(obj, str) or isinstance(obj,list):		
		
			# length attribute
			length = int(self.attributes.get('length',50))
			
			return obj[:length]

		return obj
	
	
	def html_escape(self,obj):

		# debug
		#print('html_escape')
		
		import cgi
		
		if isinstance(obj, str):
			
			return cgi.escape(obj,quote=True).replace("{","&#123;").replace("}","&#125;").replace('\\','').replace('/','\/')
		
		return obj
	

	def html_markers(self,obj):

		# debug
		#print('html_markers')

		if isinstance(obj, str):
		
			return obj.replace("{","&#123;").replace("}","&#125;")
		
		return obj		
		
	
	def uuid(self,obj):

		# debug
		#print('uuid')
		
		import uuid
		
		# random uuid
		return str(uuid.uuid4()) #any obj will be ignored
	
	
	def url_quote(self,obj):

		# docs - https://docs.python.org/2/library/urllib.html#urllib.quote_plus

		# debug
		#print('url_quote')	
			
		if isinstance(obj,str):
		
			import urllib
			obj = urllib.quote_plus(obj)
		
		return obj
	
	
	def url_unquote(self,obj):

		# debug
		#print('url_unquote')	

		import urllib

		if isinstance(obj,str):

			return urllib.unquote_plus(obj)

		return obj	

	
	def date(self,obj):

		# debug
		#print('date')	
		
		import datetime
		
		format = self.attributes.get('format', "%Y-%m-%d")
		
		# no object, current time
		if not obj:
			
			obj =  datetime.datetime.now()
		
		# datetime object
		if isinstance(obj,datetime.datetime):
			
			try:
			
				return datetime.datetime.strftime(obj,format)
			except:
				return obj
		
		# unix timestamp
		if isinstance(obj,str):
			
			if not obj.isdigit():
				
				return obj
				
			obj = int(obj)
		
		if isinstance(obj,int):
			
			return datetime.datetime.fromtimestamp(obj).strftime(format)
	
		return obj

	
	def last4(self,obj):

		# debug
		#print('last4')	
		
		if isinstance(obj,str):		
			
			return "*"*(len(obj)-4)+ obj[-4:]
		
		return obj

	
	def keyword(self,obj):

		# debug
		#print('keyword')	
		
		if isinstance(obj,str):		
			
			return '<mark>%s</mark>'%obj
		
		return obj
	
	
	def title_case(self,obj):

		# debug
		#print('title_case')	
		
		if isinstance(obj,str):
		
			# split the string on spaces
			parts = obj.split()
			
			obj = []
			for part in parts:
				obj.append("%s%s" %(part[0].upper(),part[1:].lower()))
			
			return " ".join(obj)
		
		return obj


	def string(self,obj):

		# debug
		#print('string')
		
		return str(obj)


	def upper(self,obj):

		# debug
		#print('string')
		
		return str(obj).upper()


	def lower(self,obj):

		# debug
		#print('string')
		
		return str(obj).lower()


	def list(self, obj):
		
		# if the obj is not a list, make it the first element of a list
		if not isinstance(obj, list):
			obj = [obj]
		
		return obj
	
	
	def escape_script(self,obj):
		
		#print('escape_script')
		#print(type(obj))
		
		if isinstance(obj,str):
			
			return obj.replace('</script>','<\\/script>')
		
		#print('return default')
		#print(obj)
		return obj

	'''
	def cleanup(self,obj):
		
		if not isinstance(obj,str):
			return obj
		
		
		return obj.decode("utf-8").replace(u"\e2u3F3F",'')
	'''
	
	def us_phone(self,obj):
		
		if not isinstance(obj,str):
			
			obj = str(obj)
		
		out = obj
		if obj != "":
		
			out = "(%s) %s-%s"%(obj[0:3],obj[3:6],obj[6:10])
		
		return out


	def us_ssn(self,obj):
		
		if not isinstance(obj,str):
			
			obj = str(obj)
		
		out = "%s-%s-%s"%(obj[0:3],obj[3:5],obj[5:9])
		
		return out


	def random_choice(self,obj):
		
		if not isinstance(obj,list):
			return obj

		import random
		
		return random.choice(obj)
	

	# wtf - was this really needed?
	def tab(self,obj):
		
		return '\t'


	'''  END FNR FUNCTIONS
	'''



	''' 	Find and Replace method.  This the core of the framework
	'''

	def fnr(self,template,limit=10):

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
				start = str(template_copy).index('{{')
				end = str(template_copy).index('}}',start)
			
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

					# data inside of functions
					if i < len(marker)-1 and not quote_state and marker[i] == "(" and marker[i+1] != ")":
						if value:
							stack.append(''.join(value))
						value = []
						nested_state = True
						continue
					
					# data inside of functions
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
				
				# perform markup on input using markers
				for item in stack:
					
					# debug
					#print(item)
					
					# string literals
					if item.startswith("|"):
						markup_value = item.lstrip("|")
						continue
					
					# functions
					if item.endswith("()"):
						
						# search for function in fnr_types
						if item.rstrip("()") not in self.fnr_types:
							print("Error - '%s' is not a valid fnr function" %item)
							break
						
						markup_value = eval(self.fnr_types[item.rstrip("()")])(markup_value)
						continue
						
					# attributes
					if ":"  in item:
						
						# is this a marker for a local attribute?
						if item.split(":")[0] in self.attributes:
							
							# yes prepend this: to marker
							item = "this:%s" %item
						
						# is there a type for this marker
						if item.split(":")[0] not in self.fnr_types:
							print("WARN - '%s' is not a valid fnr attribute" %item.split(":")[0])
							break						
						
						# search for interger literals in fnr_types
						items = item.split(":")
						object = items[0]
						keys = ""
						for part in items[1:]:
							if part.startswith('|') and part.strip('|').isdigit():
								
								# int literal
								keys += "[%s]"%part.strip('|')
								continue
							
							keys += "['%s']"%part
						
						# debug
						#print(self.fnr_types[object])
						#print(keys)
						#print(markup_value)
						
						try:
							markup_value = eval(self.fnr_types[object]+keys)
							
						except KeyError:
							pass
						except TypeError:
							pass
							
						except: traceback.print_exc()
						
						continue
					
					# attribute object (or raw)
					if item in self.fnr_types:
						markup_value = eval(self.fnr_types[item])
						continue
					
					# if this attribute is for the local scope (this)
					if item in eval(self.fnr_types['this']):
						markup_value = eval(self.fnr_types['this'])[item]
						continue
					
					# end of loop
				
				# replace marker with markup_value
				if markup_value or markup_value == '' or markup_value == 0:
					template = str(template.replace("{{%s}}" %marker,str(markup_value)))
					
				'''debug - warning: lots of output, but this is useful if you need to see
					markups at this granular level.
				'''
				#print(marker,markup_value)
				
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
		if not conf.get('value') and conf['value'] != 0 and conf['value'] != '':
			print("error value not given")
			return False
		
		# format
		conf.setdefault('format','string')

		# store
		conf.setdefault('store',False)
		
		# data
		data = conf['value']
		
		if isinstance(data,str) and 'nomarkup' not in conf:
			
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
			
			self.data = str(data)
		

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
			
			self.data = str(data)


		# entry point
		if conf.get('entry'):
			
			if conf['entry'].startswith('{{') and conf['entry'].endswith('}}'):
				
				entry = self.colon_seperated_to_brackets(conf['entry'].lstrip('{{').rstrip('}}'))
				
				exec('self.data = self.data%s' %entry)
		
		# store
		if conf.get('store'):

			if 'merge' in conf and conf['store'] in dir(self.top):				
				
				if eval('isinstance(self.top.%s, dict)' %conf['store']):
				
					# merge with top item
					exec('self.top.%s.update(self.data)' %conf['store'])
					
					# debug
					#print('updated top.%s with self.data' %conf['store'])

				if eval('isinstance(self.top.%s, list)' %conf['store']):
				
					# merge with top item
					exec('self.top.%s.extend(self.data)' %conf['store'])
					
					# debug
					#print('extended top.%s with self.data' %conf['store'])

				if eval('isinstance(self.top.%s, str)' %conf['store']):
				
					# merge with top item
					exec('self.top.%s += self.data' %conf['store'])
					
					# debug
					#print('concatonated top.%s and self.data' %conf['store'])
				
			else:
			
				# add to top
				exec('self.top.%s = self.data' %conf['store'])

				# add to top fnr_types
				self.top.fnr_types.update({conf['store']: 'self.top.%s' %conf['store']})

				#print('stored self.data as top.%s' %conf['store'])
				
				
		#print(self.data)
		
		return True


	def colon_seperated_to_brackets(self,input):

		if input != "":
		
			# format input into a bracketed format
			
			# replace escaped colons
			input = str(input.replace("\:","_-_-_-_-_-_"))
			
			# split segments on colons
			segments = input.split(":")
			
			output = ""
			
			for segment in segments:
				
				# debug
				#print(segment)
				
				# record digits as numbers
				if segment.isdigit():
					
					# add segment to entry
					output += "[%s]" %segment
					continue
					
				# reinstate colons in segments 
				segment = str(segment.replace("_-_-_-_-_-_",":"))
				
				# escape quotes
				segment = str(segment.replace("'",r"\'").replace('"',r'\"'))
				
				# add segment to entry
				output += "['%s']" %segment
				
			return output
			
		return input
			
	