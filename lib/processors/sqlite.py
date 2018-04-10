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
		
		con = None
		
		db = self.conf.get('db')
		
		if not db:
			
			print('no db was given')
			return False
		

		sql = self.conf.get('sql')
		
		if not sql:
			
			print('no sql was given')
			return False

		cache = self.conf.get('cache',{})
			
		db = self.content.fnr(db)
		sql = self.content.fnr(sql)

		try:
			con = sqlite3.connect(db)

			cur = con.cursor()    
			cur.execute(sql)
			
			print(cur.lastrowid)
			
			if cache:
				if 'id' in cache:
					self.top.cache[cache['id']] = cur.lastrowid

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
		
		con = None
		
		db = self.conf.get('db')
		
		if not db:
			
			print('no db was given')
			return False
		

		sql = self.conf.get('sql')
		
		if not sql:
			
			print('no sql was given')
			return False
		
		db = self.content.fnr(db)
		sql = self.content.fnr(sql)

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
		
		con = None
		
		db = self.conf.get('db')
		
		if not db:
			
			print('no db was given')
			return False
		

		sql = self.conf.get('sql')
		
		if not sql:
			
			print('no sql was given')
			return False
		
		db = self.content.fnr(db)
		sql = self.content.fnr(sql)

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
		
		self.element.data = []
		con = None
		
		db = self.conf.get('db')
		
		if not db:
			
			print('no db was given')
			return False
		

		sql = self.conf.get('sql')
		
		if not sql:
			
			print('no sql was given')
			return False

		cache = self.conf.get('cache',{})
			
		db = self.content.fnr(db)
		sql = self.content.fnr(sql)

		try:
			con = sqlite3.connect(db)
			con.row_factory = sqlite3.Row
			
			cur = con.cursor()    
			cur.execute(sql)
			
			for row in cur:
				
				record = {}
				for key in row.keys():
					
					record[key] = row[key]

				self.element.data.append(record)	
			
			if self.element.data:
				self.element.record = self.element.data[0]
			else:
				self.element.record = {}
			
		except sqlite3.Error, e:

			print ("Error %s:" % e.args[0])
			
			return False
			
		finally:

			if con:
				
				con.commit()
				con.close()
		
		return True