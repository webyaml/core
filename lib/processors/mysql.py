# path: 
# filename: db.py
# description: WSGI application MySQL database processors
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
import oursql

''' internal imports
'''
import classes.processor

''' classes
'''
class Select(classes.processor.Processor):

	
	def run(self):
		
		print('lib.processors.mysql.Select')
		
		conf = self.conf
		
		# debug
		#print(conf)
		
		if not conf.get('conf'):
		
			print('Database conf not found')
			
			return False
		
		if not conf.get('sql'):
			
			print('SQL statement not found')
			
			return False
				
		sql = self.content.fnr(conf['sql'])

		# limit
		if conf.get('limit'):
			
			# page
			conf['page'] = self.content.fnr(conf.get('page',1))
			if isinstance(conf['page'], str) and not conf['page'].isdigit():
				conf['page'] = 1
			
			conf['page'] = int(conf['page'])	- 1
			conf['limit'] = int(conf['limit'])
			
			sql = "%s LIMIT %d,%d" %(sql, conf['page'] * conf['limit'], int(conf['limit']))
			
		# debug
		print('sql: %s' %sql)	

		
		db_connection = oursql.connect(**conf.get('conf'))

		conf.setdefault('reader','dict')
		
		if conf['reader'] == 'list':
			select = db_connection.cursor()
		else:
			select = db_connection.cursor(oursql.DictCursor)
		
		try:
			select.execute(sql)
			
			#  store result in element
			output = select.fetchall()
			
			# debug
			#print(output)
			
			if not output:
				return False
				
			# handle the returned data
			if conf.get('result'):
				
				conf['result']['value'] = output
				
				if conf['reader'] == 'record':
					conf['result']['entry'] = '{{0}}'
				
				conf['result']['format'] = 'list'
				
				# load data
				if not self.content.load_data(conf['result']):
					
					print('failed to save - data failed to load')
						
					return False					
		
		except oursql.Error as e:
			
			# add mysql errors as content - useful for debugging
			
			conf['false'] = {'content': {'value': "MySQL error: %s" %str(e[1])}}
			
			print(e)
			
			return False
			
		return True
	

class Insert(classes.processor.Processor):

	def run(self):
		
		db_conf = self.conf.get('conf')
		if not db_conf:
			
			self.element.messages.append(["danger",'Database conf not found'])
			
			return False		
		
		sql = self.conf.get('sql')
		if not sql:
			
			self.element.messages.append(["danger",'SQL statement not found'])
			
			return False
		
		sql = self.content.fnr(self.content.fnr(self.conf.get('sql','')))
		
		print('sql: '+sql)
		
		db_connection = oursql.connect(**db_conf)
		insert = db_connection.cursor()
		
		try:
			insert.execute(sql, plain_query=True)
			
			if self.conf.get('cache_id'):
				self.top.cache[self.conf['cache_id']] = insert.lastrowid
			
			return True


		except oursql.Error as e:
			
			print(e)
			
			# we could possibly add content here
			
			self.conf['false'] = {'content': {'value': "MySQL error: %s" %str(e[1])}}
			
			return False
			
			
class Update(Insert):
	
	''' Same as insert.
	'''
	pass
		
		



class Select_old(classes.processor.Processor):

	
	def run(self):
		
		db_conf = self.conf.get('conf')
		if not db_conf:
			
			self.element.messages.append(["danger",'Database conf not found'])
			
			return False		
		
		sql = self.conf.get('sql')
		if not sql:
			
			self.element.messages.append(["danger",'SQL statement not found'])
			
			return False
		
		sql = self.content.fnr(self.conf.get('sql',''))
		
		print('sql: '+sql)
		
		
		
		db_connection = oursql.connect(**db_conf)
		
		format = self.conf.get('format', 'dict')
		if format == 'list':
			select = db_connection.cursor()
		else:
			select = db_connection.cursor(oursql.DictCursor)
		
		
		try:
			select.execute(sql)
			
			#  store result in element
			output = select.fetchall()
			
			print(output)
			
			
			if not output:
				return False
				
			json_fields = self.conf.get('json')
			if json_fields:
				
				import json
				
				for record in output:
					
					for field in json_fields:
						
						#print(record[field])
						#record[field] = json.loads(record[field])
						
						try:
							record[field] = json.loads(record[field])
						except:
							record[field] = {}
						
			
			# Create Cache
			cache = self.conf.get('name')
			if cache:
				
				if format == 'record':
					
					if cache in dir(self.top):
						# create top level object to store the output
						exec('self.top.%s.update(output[0])' %cache)
						
					else:
						# create top level object to store the output
						exec('self.top.%s = output[0]' %cache)
						
						#print('created new object')
					
				else:
					# create top level object to store the output
					exec('self.top.%s = output' %cache)
				
				# add to top fnr_types
				self.top.fnr_types.update({cache: 'self.top.%s' %cache})
			
			return True

		except oursql.Error as e:
			
			# we could possibly add content here
			
			self.conf['false'] = {'content': {'value': "MySQL error: %s" %str(e[1])}}
			
			print(e)
			
			return False	
	
