# path: lib/processors/
# filename: cache.py
# description: WSGI application cache processors
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
class Cache(classes.processor.Processor):
	
	def run(self):
		
		print('lib.processors.Cache')

		cache = self.conf.get('cache',{})

		for var in cache:
			
			markup = self.content.fnr(cache[var])
			
			print(type(markup))
			
			self.top.cache[var] = markup
	
		return True

