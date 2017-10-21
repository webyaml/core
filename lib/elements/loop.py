# path: lib/elements/
# filename: loop.py
# description: WSGI application preprocessor element

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
import classes.element

class Loop(classes.element.Element):

	''' This element will extend the content tree with records from a list of dictionaries
	'''

	def __init__(self,content):
		
		print('lib.elements.loop.Loop')
		
		# super class Element
		super(Loop, self).__init__(content)

		# vars
		#conf = self.content.attributes
		conf = self.conf
		filter = conf.get('filter')
		
		# debug
		#print(conf)

		# conf checks
		if not conf.get('data'):
			
			print('failed to loop - data not defined')
			return None
		
		# load item object
		if not conf.get('subcontent'):
			
			print('failed to loop - subcontent not found')
			return None
		
		# load data
		if not self.load_data(conf['data']):
			
			print('failed to loop - data failed to load')
			
			if conf.get('default'):
				
				print("attempting to show default")
				
				self.content.tree({'content': conf.get('default')})				
				
			return None		
		
		# debug
		#print(self.data)
		
		# data must be a list to loop
		if not isinstance(self.data,list):
			
			print('warning - data is not a list')
			
			try:
				self.data = [self.data]
				print('warning - data was converted to a list')
				
			except Error as e:
				
				print(e)
				return
		
		# check for a list of subcontent
		if isinstance(conf['subcontent'], list):
			
			#convert to content dictionary
			conf['subcontent'] = {'content':conf['subcontent']}			
		
		# debug
		print('starting loop')
		
		
		#for each element in data create an content item
		items = []
		
		for item in self.data:
			
			item = copy.copy(item)
			
			#print(item)
			
			# stop loop if limit has been reached
			if conf.get('limit') and conf['limit'] == len(items):
				break

			# evaluate filter
			if conf.get('filter') and isinstance(filter,str):
				
				''' This needs to be fix - store is depricated
				'''
				
				# store the item to be used by fnr functions
				#self.store(item,format='python',name='i')				
				self.load_data({'format': 'raw', 'store': 'i', 'value': item})
					
				# debug
				#print(self.fnr(conf.get('filter')))
				
				# filter must be True to show item
				if not eval(self.fnr(conf.get('filter'))):
					continue
			
			
			if isinstance(item, dict):
				
				#print('found dict')
				
				item.update(conf['subcontent'])
				items.append(item)
			
			if isinstance(item, str):
				
				#print('found str')
				
				tmp_record = {'i': item}
				tmp_record.update(conf['subcontent'])				
				items.append(tmp_record)
			
			if isinstance(item, int):
				
				#print('found int')
				
				tmp_record = {'i': item}
				tmp_record.update(conf['subcontent'])				
				items.append(tmp_record)

			#print(item)
				
		#debug
		#print(items)
		
		if items:
			# continue Content Tree true content
			self.content.tree({'content': items})
			
			return None
			
		if conf.get('default'):
			self.content.tree({'content': conf.get('default')})
			
			return None

		print('nothing looped')
