# path: classes/
# filename: processor.py
# description: WSGI application processor

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
#import
import traceback
import datetime
from decimal import Decimal

''' internal imports
'''
#import

''' classes
'''
class Processor(object):

	def __init__(self,conf,element):
		
		# vars
		self.conf = conf
		# the caller object of this Processor
		self.element = element
		self.content = self.element.content
		self.top = self.element.content.top
		self.parent = self.element.content.parent
		self.data = None
		
		return None

	def store(self,records,**kwargs):
		
		print('Store')
		
		#print(kwargs)
		
		if 'format' in kwargs:
			
			# debug
			#print('format found in kwargs')
			
			format = kwargs['format']
			
		else:
			format = self.conf.get('format', 'list')
		
		#print('format: %s' %format)
		
		
		if 'name' in kwargs:
			
			#print('name found in kwargs')
			
			objName = kwargs['name']
		else:
			objName = self.conf.get('name')
		
		#print('objName: %s' %objName)
		
		if objName:
			
			if format == 'record':
				
				if objName in dir(self.top):
					# create top level object to store the output
					exec('self.top.%s.update(records[0])' %objName)
					
					print('cache object found')
					
				else:
					# create top level object to store the output
					exec('self.top.%s = records[0]' %objName)
					
					print('created new object')
				
			else:
				# create top level object to store the output
				exec('self.top.%s = records' %objName)
			
			# add to top fnr_types
			self.top.fnr_types.update({objName: 'self.top.%s' %objName})


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
		print('clases.processor.Processor.load_data')	
		
		# conf check
		
		#debug 
		#print(conf)
		
		# value
		if not conf.get('value'):
			
			print("error value not given")
		
		# format
		conf.setdefault('format','string')

		# store
		conf.setdefault('store',False)
		
		# data
		data = conf['value']
		
		if isinstance(data,str) and 'nomarkup' not in conf:
			
			# markup data
			data = self.element.fnr(data)

		# debug
		#print(data)
		
		# format data
		
		# CSV
		if conf['format'] == 'csv':
			
			print('format is csv')
			
			import csv
			
			reader = conf.get('reader','dict')
			kwargs = conf.get('kwargs',{})
			
			if reader == 'list':

				try: 				
				
					tmp_data = csv.reader(data.split('\n'),**kwargs)
					self.data = []
					for item in tmp_data:
						self.data.append(item)
				
				except: traceback.print_exc()			
				
			else:

				try:
				
					tmp_data = csv.DictReader(data.split('\n'),**kwargs)
					
					#print(tmp_data)
					
					self.data = []
					for item in tmp_data:
						
						#print(item)
						
						self.data.append(item)					
				
				except: traceback.print_exc()	
				
		
		# dict
		if conf['format'] == 'dict':
			
			print('format is dct')
			
			try:
				self.data = eval(data)
			
				if not isinstance(self.data,dict):
				
					print('warning data not a dictionary')
					
			except: traceback.print_exc()
		
		
		# int
		if conf['format'] == 'int':
			
			print('format is int')
			
			try:
				self.data = eval(data)
			
				if not isinstance(self.data,int):
				
					print('warning data not a int')
					
			except: traceback.print_exc()

		# json
		if conf['format'] == 'json':
			
			print('format is json')
			
			import json
			
			try:
				self.data = json.loads(data)
			
			except: traceback.print_exc()		
		
		
		# list
		if conf['format'] == 'list':
			
			print('format is list')
			
			try:
				self.data = eval(data)
			
				if not isinstance(self.data,list):
				
					print('warning data not a list')
					
			except: traceback.print_exc()	
		
		
		# python
		if conf['format'] == 'python':
			
			print('format is python')
			
			try:
				self.data = eval(data)
			
				print('python data is of the type %s' %type(self.data))
					
			except: traceback.print_exc()
		
		# raw
		if conf['format'] == 'raw':
			
			print('format is raw')
			
			self.data = data
			
		# string
		if conf['format'] == 'string':
			
			print('format is string')
			
			self.data = str(data)
		

		# yaml
		if conf['format'] == 'xml':
			
			print('format is xml')
			
			import xmltodict
			
			try:
				self.data = xmltodict.parse(data)
			
			except: traceback.print_exc()	
		
		
		# yaml
		if conf['format'] == 'yaml':
			
			print('format is yaml')
			
			import yaml
			
			try:
				self.data = yaml.load(data)
			
			except: traceback.print_exc()	
			
		# default (string)
		if not self.data:
			
			print('format is default')
			
			self.data = str(data)


		# entry point
		if conf.get('entry'):

			
			if conf['entry'].startswith('{{') and conf['entry'].endswith('}}'):
				
				entry = self.element.colon_seperated_to_brackets(conf['entry'].lstrip('{{').rstrip('}}'))
				
				exec('self.data = self.data%s' %entry)
		
		# store
		if conf.get('store'):
			
			if conf.get('update'):
				# add to top
				exec('self.top.%s.update(self.data)' %conf['store'])
				
				# debug
				print('updated top.%s with self.data' %conf['store'])
				
				return True

			# add to top
			exec('self.top.%s = self.data' %conf['store'])
			
			# add to top fnr_types
			self.top.fnr_types.update({conf['store']: 'self.top.%s' %conf['store']})

			print('stored self.data as %s' %conf['store'])
			
		return True

		