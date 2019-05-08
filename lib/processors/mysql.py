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

		# vars
		conf = self.conf
		debug = False		
		
		
		if conf.get('debug'):
			
			print('lib.processors.mysql.Select')
			debug = True		
		
		
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
		if debug:
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
			if debug:
				print(output)
				
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
			
			# return false if output is an empty list
			if not output:
				return False					
		
		except oursql.Error as e:
			
			# add mysql errors as content - useful for debugging
			
			conf['false'] = {'content': {'value': "MySQL error: %s" %str(e[1])}}
			
			print(e)
			
			return False
			
		return True
	

class Insert(classes.processor.Processor):

	
	def run(self):
		
		# vars
		conf = self.conf
		debug = False		
		
		
		if conf.get('debug'):
			
			print('lib.processors.mysql.Insert')
			debug = True		
		
		
		if not conf.get('conf'):
		
			print('Database conf not found')
			
			return False
		
		if not conf.get('sql'):
			
			print('SQL statement not found')
			
			return False

		sql = self.content.fnr(conf['sql'])
		
		# clean remaining markers in sql
		if not conf.get('keepmarkers'):
			pattern = re.compile(r'({{[\w|\(|\)|\.|\:|\-]+}})')
			markers = list(set(pattern.findall(sql)))

			for marker in markers:
				sql = unicode(sql.replace(marker,''))			
			
		
		# debug
		if debug:
			print('sql: %s' %sql)
		
		db_connection = oursql.connect(**conf.get('conf'))
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
