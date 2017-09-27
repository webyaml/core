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