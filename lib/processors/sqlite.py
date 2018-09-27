# path: lib/processors
# filename: sqlite.py
# description: WSGI application SQLite database processors
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
import sqlite3

''' internal imports
'''
import classes.processor

''' classes
'''
class Insert(classes.processor.Processor):
	
	def run(self):

		# vars
		conf = self.conf
		debug = False	
		
		

		if conf.get('debug'):
			
			print('lib.processors.sqlite.Insert')
			debug = True
		
		if not conf.get('db'):
		
			print('db not found in conf')
			
			return False
			
		db = self.content.fnr(conf['db'])			

		if not conf.get('sql'):
			
			print('SQL statement not found')
			
			return False

		sql = self.content.fnr(conf['sql'])		

		con = None
		
		try:
			con = sqlite3.connect(db)

			cur = con.cursor()    
			cur.execute(sql)
			
			#print(cur.lastrowid)
			
			if self.conf.get('cache_id'):
				self.top.cache[self.conf['cache_id']] = cur.lastrowid
			
			return True

		except sqlite3.Error, e:

			print ("Error %s:" % e.args[0])
			
			return False

		finally:

			if con:
				
				con.commit()
				con.close()

		return True


class Delete(classes.processor.Processor):
	
	def run(self):
		
		# vars
		conf = self.conf
		debug = False

		if conf.get('debug'):
			
			print('lib.processors.sqlite.Delete')
			debug = True
		
		if not conf.get('db'):
		
			print('db not found in conf')
			
			return False
			
		db = self.content.fnr(conf['db'])			

		if not conf.get('sql'):
			
			print('SQL statement not found')
			
			return False

		sql = self.content.fnr(conf['sql'])		

		con = None

		try:
			con = sqlite3.connect(db)

			cur = con.cursor()    
			cur.execute(sql)

		except sqlite3.Error, e:

			print ("Error %s:" % e.args[0])
			
			return False

		finally:

			if con:
				
				con.commit()
				con.close()

		return True


class Update(classes.processor.Processor):
	
	def run(self):
		
		# vars
		conf = self.conf
		debug = False

		if conf.get('debug'):
			
			print('lib.processors.sqlite.Update')
			debug = True
		
		if not conf.get('db'):
		
			print('db not found in conf')
			
			return False
			
		db = self.content.fnr(conf['db'])			

		if not conf.get('sql'):
			
			print('SQL statement not found')
			
			return False

		sql = self.content.fnr(conf['sql'])		

		con = None
		
		try:
			con = sqlite3.connect(db)

			cur = con.cursor()    
			cur.execute(sql)

		except sqlite3.Error, e:

			print ("Error %s:" % e.args[0])
			
			return False

		finally:

			if con:
				
				con.commit()
				con.close()

		return True

class Select(classes.processor.Processor):
	
	def run(self):

		# vars
		conf = self.conf
		debug = False

		if conf.get('debug'):
			
			print('lib.processors.sqlite.Select')
			debug = True
		
		if not conf.get('db'):
		
			print('db not found in conf')
			
			return False
			
		db = self.content.fnr(conf['db'])			

		if not conf.get('sql'):
			
			print('SQL statement not found')
			
			return False

		sql = self.content.fnr(conf['sql'])		

		con = None
	
		conf.setdefault('reader','dict')

		try:
			con = sqlite3.connect(db)
			con.row_factory = sqlite3.Row
			
			cur = con.cursor()    
			cur.execute(sql)
			
			
			output = []
			
			if conf['reader'] == 'list':
				
				# list
				for row in cur:
					
					record = []
					for key in row.keys():
						
						record.append(row[key])

					output.append(record)
				
			else:
				# dict
				for row in cur:
					
					record = {}
					for key in row.keys():
						
						record[key] = row[key]

					output.append(record)
			
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
			
		except sqlite3.Error, e:

			print ("Error %s:" % e.args[0])
			
			return False
			
		finally:

			if con:
				
				con.commit()
				con.close()
		
		return True