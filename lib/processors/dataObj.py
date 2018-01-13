# path: lib/processors
# filename: dataObj.py
# description: WSGI application data store processors

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

''' internal imports
'''
import classes.processor

''' classes
'''
class Create(classes.processor.Processor):
	
	def run(self):
		
		print('lib.processors.dataObj.Create')
		
		conf = self.conf

		if not conf.get('data'):
			
			print('data not in conf')
			return False
			
		# load data
		if not self.load_data(conf['data']):
			
			print('data failed to load')
			
			return False
	
		return True
		
		
class Modify(classes.processor.Processor):
	
	def run(self):
		
		print('lib.processors.dataObj.Modify')
		
		conf = self.conf

		if not conf.get('source'):
			
			print('source not in conf')
			return False

		if not conf.get('data'):
			
			print('data not in conf')
			return False
		
		# load dataObj into self.data
		try:
			exec('self.dataObj = self.top.%s'%conf["source"]["dataObj"])
			
		except AttributeError:
			
			print('Error: dataObj %s not found'%conf["source"]["dataObj"])
			
			return False
		
		# debug
		#print(self.dataObj)
		
		
		# load the new data
		if not self.load_data(conf['data']):
			
			print('data failed to load')
			
			return False
		
		
		# get the entry point
		entry = ''
		if conf["source"].get('entry'):
		
		
			if conf["source"]['entry'].startswith('{{') and conf["source"]['entry'].endswith('}}'):
				
				entry = self.element.colon_seperated_to_brackets(conf["source"]['entry'].lstrip('{{').rstrip('}}'))
			else:
				print('Error: entry not in the form of a marker')
				return False
			
			#print(entry)
		
		
		# do we replace or append new data?
		
		if 'merge' in conf['source']:
			
			print('merge')
			
			if eval('isinstance(self.dataObj%s, dict)' %entry):
			
				# merge with top item
				exec('self.dataObj%s.update(self.data)' %entry)
				
			if eval('isinstance(self.dataObj%s, list)' %entry):
				# merge with top item
				exec('self.dataObj%s.extend(self.data)' %entry)
				
			if eval('isinstance(self.dataObj%s, str)' %entry):
				# merge with top item
				exec('self.dataObj%s += self.data' %entry)
			
		else:
			# replace data
			
			exec('self.dataObj%s = self.data' %entry)
		
		
		return True
