# path: lib/processors
# filename: mongo.py
# description: WSGI application mongoDB processors
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
import pymongo
import yaml

''' internal imports
'''
import classes.processor

''' classes
''' 
class Mongo(classes.processor.Processor):
	
	def __init__(self,conf,element):
		
		# super class Element
		super(Mongo, self).__init__(conf,element)
		
		self.content.database_name = self.conf.get('database')
		if not self.content.database_name:
			print("config error - missing 'database'")
			
		self.content.database_name = self.content.fnr(self.content.database_name)
		
		print(self.content.database_name)
		
		self.collection_name = self.conf.get('collection')
		if not self.collection_name:
			print("config error - missing 'collection'")
		
		self.collection_name = self.content.fnr(self.collection_name)
		
		print(self.collection_name)
		
		'''Connect to database'''
		self.client = pymongo.MongoClient()
		self.content.database = self.client[self.content.database_name]
		
		return None
		
		
class Find(Mongo):
	
	def run(self):
		
		'''Filter'''
		
		filter = self.conf.get('filter')
		if not filter:
			filter = {}
			
		if isinstance(filter, str):
			
			# remove tabs
			filter =  filter.replace("\t","     ")

			# markup
			filter = self.content.fnr(filter)
			
			# parse yaml
			filter = yaml.load(filter)
			
			
		'''Query'''
		results = self.content.database[self.collection_name].find(filter)
		if not results.count():
			
			return False
		
		
		'''Loop'''
		loop = self.conf.get('loop')
		if loop:
			
			# remove tabs
			loop =  loop.replace("\t","     ")

			records = []
			for record in results:
			
				# turn objectId() into a string
				if '_id' in record:
					record['_id'] = str(record['_id'])
				
				# store record as 'record'
				#self.store([record],format='record',name='record')
				self.content.load_data({'format': 'raw', 'store': 'record', 'value': record})	
				
				#print(loop)
				
				# markup
				loop_result = self.content.fnr(loop)
				
				#print(loop_result)
				
				# parse yaml
				loop_result = yaml.load(loop_result)				
				
				records.append(loop_result)

			'''Store'''
			#self.store(records)
			self.content.load_data({'format': 'raw', 'store': 'records', 'value': records})
			
		else:
		
			records = []
			for record in results:
				
				if '_id' in record:
					record['_id'] = str(record['_id'])
				
				records.append(record)
			
			'''Store'''
			#self.store(records)
			self.content.load_data({'format': 'raw', 'store': 'records', 'value': records})
		
		return True
			
