# path: lib/processors
# filename: dataObj.py
# description: WSGI application data store processors
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
class Create(classes.processor.Processor):
	
	def run(self):
		
		conf = self.conf
		debug = False
		
		if conf.get('debug'):
		
			print('lib.processors.dataObj.Create')
			debug = True
		
		if not conf.get('data'):
			
			print('data not in conf')
			return False
			
		# load data
		if not self.content.load_data(conf['data']):
			
			print('data failed to load')
			
			return False
	
		return True
		
		
class Modify(classes.processor.Processor):
	
	def run(self):


		conf = self.conf
		debug = False
		
		if conf.get('debug'):
		
			print('lib.processors.dataObj.Modify')
			debug = True

		if not conf.get('source'):
			
			print('source not in conf')
			return False

		if not conf.get('data'):
			
			print('data not in conf')
			return False
		
		# load dataObj into self.content.data
		try:
			exec('self.content.dataObj = self.top.%s'%conf["source"]["dataObj"])
			
		except AttributeError:
			
			print('Error: dataObj %s not found'%conf["source"]["dataObj"])
			
			return False
		
		# debug
		#print(self.content.dataObj)
		
		
		# load the new data
		if not self.content.load_data(conf['data']):
			
			print('data failed to load')
			
			return False
		
		
		# get the entry point
		entry = ''
		if conf["source"].get('entry'):
		
		
			if conf["source"]['entry'].startswith('{{') and conf["source"]['entry'].endswith('}}'):
				
				entry = self.content.colon_seperated_to_brackets(conf["source"]['entry'].lstrip('{{').rstrip('}}'))
			else:
				print('Error: entry not in the form of a marker')
				return False
			
			#print(entry)
		
		
		# do we replace or append new data?
		
		if 'merge' in conf['source']:
			
			if debug:
				print('merge')
			
			if eval('isinstance(self.content.dataObj%s, dict)' %entry):
				
				if debug:
					print('source is a dict')				
			
				# merge with top item
				exec('self.content.dataObj%s.update(self.content.data)' %entry)
				
			if eval('isinstance(self.content.dataObj%s, list)' %entry):
				
				if debug:
					print('source is a list')
					
				if conf['source']['merge'] == 'append':
					exec('self.content.dataObj%s.append(self.content.data)' %entry)
					
				else:
					# merge with top item
					exec('self.content.dataObj%s.extend(self.content.data)' %entry)
				
			if eval('isinstance(self.content.dataObj%s, str)' %entry):
				
				if debug:
					print('source is a str')				
				
				# merge with top item
				exec('self.content.dataObj%s += self.content.data' %entry)
			
		else:
			# replace data
			
			exec('self.content.dataObj%s = self.content.data' %entry)
		
		
		return True


class Delete(classes.processor.Processor):
	
	def run(self):


		conf = self.conf
		debug = False
		
		if conf.get('debug'):
		
			print('lib.processors.dataObj.Delete')
			debug = True

		if not conf.get('data'):
			
			print('data not in conf')
			return False
			
		if not conf['data'].get('store'):
			
			print('data:store not in conf')
			return False
			
		
		# load dataObj into self.content.data
		try:
			exec('self.top.%s = None'%conf["data"]["store"])
		
		except:
			
			print('Error: dataObj %s not found'%conf["data"]["store"])
			
			return False
		
		return True
