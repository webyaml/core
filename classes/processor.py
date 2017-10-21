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
import copy

''' internal imports
'''
#import

''' classes
'''
class Processor(object):

	def __init__(self,conf,element):
		
		# vars
		self.conf = copy.copy(conf)
		self.element = element
		self.content = self.element.content
		self.top = self.element.content.top
		self.parent = self.element.content.parent
		#self.data = None
		self.data = self.element.data
		
		return None

	def store(self,records,**kwargs):

		'''This needs to be depricated at some point
		use load_data instead
		'''

		print('DANGER USING STORE - REPLACE ASAP')
		
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
				
				print('created new object')
				
				print(eval('self.top.%s' %objName))
			
			# add to top fnr_types
			self.top.fnr_types.update({objName: 'self.top.%s' %objName})

	# data handling
	def load_data(self,conf):

		return self.element.load_data(conf)
