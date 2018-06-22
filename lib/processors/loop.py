# path: lib/processors
# filename: loop.py
# description: WSGI application image file processors
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
import copy

''' internal imports
'''
import classes.processor

''' classes
'''
class Loop(classes.processor.Processor):

	'''
	Description:
		
		Loop over a set of data to do more processing
	
	Usage:
	
		type: lib.processors.loop.Loop
	'''
	
	def run(self):
		
		conf = self.conf
		debug = False		

		if conf.get('debug'):
			
			print('lib.processors.loop.Loop')
			debug = True

		if not conf.get('data'):
			
			print('data not in conf')
			return False
		
		# get the incrementor key
		key = conf.setdefault('key', 'i')
		
		# data format
		conf['data'].setdefault('format', 'list')
		
		# do we load content or a subprocess for each item
		if conf.get('subprocess') and conf.get('subcontent'):
			
			print('error - subprocess and subcontent defined')
			return False
		
		# load data
		if not self.content.load_data(conf['data']):
			
			print('failed to loop - data failed to load')
				
			return False
			
		# just to be safe
		#self.content.data = self.element.data
		
		# data must be a list to loop
		if not isinstance(self.content.data,list):
			
			if debug:
				print('warning - data is not a list')
				print(type(self.content.data))
				
			self.content.data = [self.content.data]
			
			if debug:
				print('warning - data was converted to a list')
		
		if debug:
			print('starting loop')
		
		if conf.get('subprocess'):

			if debug:
				print('calling subprocessors')
			
			#for each element in data perform a process
			
			count = 0
			
			for item in self.content.data:
				
				#debug
				#print(item)
				#print('count: %d' &count)
				#print(conf['limit'])
				
				# stop loop if limit has been reached
				if conf.get('limit') and int(conf['limit']) == count:
					break
					
				# store count				
				self.content.load_data({'format': 'raw', 'store': '%s_count' %key, 'value': count})
				count +=1
				
				# store the item to be used by fnr functions
				self.content.load_data({'format': 'raw', 'store': key, 'value': item})	
				
				# evaluate filter
				if conf.get('filter') and isinstance(conf['filter'],str):
					
					# debug
					#print(self.fnr(conf.get('filter')))
					
					# filter must be True to show item
					if not eval(self.content.fnr(conf['filter'])):
						continue
				
				# update attributes to include item
				#self.content.attributes.update(item)
				
				if not self.content.process(conf['subprocess']):
					
					return False
		
		if conf.get('subcontent'):	
			
			if debug:
				print('rendering subcontent')
			
			#for each element in data create an content item
			
			count = 0
			
			for item in self.content.data:

				# debug
				#print(item)
				#print(type(item))
				
				# stop loop if limit has been reached
				if conf.get('limit') and int(conf['limit']) == count:
					break
					
				# store the item to be used by fnr functions
				#self.content.load_data({'format': 'raw', 'store': key, 'value': item})						
					
				'''
				print(conf.get('filter'))
				
				# evaluate filter
				if conf.get('filter') and isinstance(filter,str):
					

					
					# filter must be True to show item
					if not eval(self.content.fnr(conf.get('filter'))):
						continue
				
						
				# debug
				print(conf.get('filter'))
				print(self.content.fnr(conf.get('filter')))						


				'''							
				# filter must be True to show item
				if conf.get('filter') and not eval(self.content.fnr(conf['filter'])):
					continue					
				
				
				new_content = {}
				new_content['content'] = []
				
				
				
				# make a new empty content element in items
				#tmp_content = {}
				
				# add the key with item to the content attributes
				#tmp_content[key] = item
				
				# store count in tmp_content
				#self.content.load_data({'format': 'int', 'store': '%s_count' %key, 'value': count})
				#tmp_content['%s_count' %key] = count
				
				
				
				# add the content
				if isinstance(conf['subcontent'],list):
					
					for element in conf['subcontent']:
						
						tmp = copy.copy(element)
						tmp[key] = item
						tmp['%s_count' %key] = count
					
						new_content['content'].append(tmp)
					
				else:
					
					tmp = copy.copy(conf['subcontent'])
					tmp[key] = item
					tmp['%s_count' %key] = count
					
					new_content['content'].append(tmp)
				
				# check for content in tmp_content
				
				#print(new_content)
				
				self.content.tree(new_content)
				
				count +=1
			
		return True