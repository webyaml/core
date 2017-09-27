# path: lib/processors
# filename: csvfile.py
# description: WSGI application csv processors

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
import csv
import os

''' internal imports
'''
import classes.processor

''' classes
'''
class Read(classes.processor.Processor):
	
	def run(self):
		
		print("lib.processrs.csvfile.Read")
		
		# check configuration
		if 'name' not in self.conf:
			
			print('name not in conf')
			return False
		
		if 'file' not in self.conf:
			
			print('file not in conf')
			return False
			
		filename = self.element.fnr(self.conf["file"])
			
		# read csv file
		print(filename)

		f = open(filename, 'r')
		content = f.read().split('\n')

		# parse dealpack data into list of dictionaries
		tmp_data = csv.DictReader(content)
		
		data = []
		for record in tmp_data:
			data.append(record)
		
		self.store(data)
		return True
	