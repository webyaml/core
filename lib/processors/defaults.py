# path: lib/processors
# filename: defaults.py
# description: WSGI application data defauts processors

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
class Defaults(classes.processor.Processor):
	
	def run(self):
		
		fields = self.conf.get('fields',{})
		
		if not fields:
			
			return True
		
		if not self.element.data:
			
			return True
			
		# set defaults if fields are missing in data
		for record in self.element.data:
			
			for field in fields:
				
				if field not in record:
					
					record[field] = fields[field]
					
		return True
		

