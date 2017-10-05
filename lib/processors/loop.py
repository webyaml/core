# path: lib/processors
# filename: loop.py
# description: WSGI application image file processors

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
		
		print('lib.processors.loop.Loop')
		
		conf = self.conf

		if not conf.get('data'):
			
			print('data not in conf')
			return False
		
		# get the incrementor key
		key = conf.setdefault('key', 'i')
		
		# do we load content or a subprocess for each item
		if conf.get('subprocess') and conf.get('subcontent'):
			
			print('error - subprocess and subcontent defined')
			return False
		
		# load data
		if not self.load_data(conf['data']):
			
			print('failed to loop - data failed to load')
				
			return False
		
		# data must be a list to loop
		if not isinstance(self.data,list):
			
			print('warning - data is not a list')
			self.data = [self.data]
			print('warning - data was converted to a list')
		
		# debug
		print('starting loop')
		
		if conf.get('subprocess'):

			print('calling subprocessors')

			#for each element in data perform a process
			for item in self.data:
				
				print(item)
				
				# stop loop if limit has been reached
				if conf.get('limit') and conf['limit'] == len(items):
					break
				
				# store the item to be used by fnr functions
				self.store(item,format='python',name=key)			
				
				# evaluate filter
				if conf.get('filter') and isinstance(filter,str):
					
					# debug
					#print(self.fnr(conf.get('filter')))
					
					# filter must be True to show item
					if not eval(self.element.fnr(conf.get('filter'))):
						continue
				
				# update attributes to include item
				#self.content.attributes.update(item)
				
				if not self.element.process(conf['subprocess']):
					
					return False
		
		if conf.get('subcontent'):	
			
			print('rendering subcontent')
			
			#for each element in data create an content item
			#content = []
			
			for item in self.data:

				print(item)
				print(type(item))
				
				# stop loop if limit has been reached
				if conf.get('limit') and conf['limit'] == len(items):
					break
				
				# store the item to be used by fnr functions
				#self.store(item,format='python',name=key)			
				
				# evaluate filter
				if conf.get('filter') and isinstance(filter,str):
					
					# debug
					#print(self.fnr(conf.get('filter')))
					
					# filter must be True to show item
					if not eval(self.element.fnr(conf.get('filter'))):
						continue
				
				# make a new empty content element in items
				tmp_content = {}
				
				# add the key with item to the content attributes
				tmp_content[key] = item
				
				# add the content
				
				if isinstance(conf['subcontent'],list):
					tmp_content.update({'content': conf['subcontent']})
				else:
					tmp_content.update(conf['subcontent'])
				
				#print(tmp_content)
				
				self.content.tree({'content': tmp_content})
				
				# append to content
				#content.append(tmp_content)
			'''
			if content:
				# continue Content Tree true content
				self.content.tree({'content': content})
				
				return True
			'''
			
		return True