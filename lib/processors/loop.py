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
		
		print('lib.processors.loop.Loop')
		
		conf = self.conf

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
			
			print('warning - data is not a list')
			print(type(self.content.data))
			self.content.data = [self.content.data]
			print('warning - data was converted to a list')
		
		# debug
		print('starting loop')
		
		if conf.get('subprocess'):

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
					
				
				# make a new empty content element in items
				tmp_content = {}
				
				# add the key with item to the content attributes
				tmp_content[key] = item
				
				# store count in tmp_content
				#self.content.load_data({'format': 'int', 'store': '%s_count' %key, 'value': count})
				tmp_content['%s_count' %key] = count
				count +=1		
				
				
				
				tmp_content.update(conf['subcontent'])
				
				'''
				# add the content
				if isinstance(conf['subcontent'],list):
					tmp_content.update({'content': conf['subcontent']})
				else:
					tmp_content.update(conf['subcontent'])
				'''
				# check for content in tmp_content
				
				#print(tmp_content)
				
				self.content.tree({'content': tmp_content})
			
		return True