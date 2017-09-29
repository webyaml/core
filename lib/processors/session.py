# path: lib/processors/
# filename: session.py
# description: WSGI application session processors

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
import datetime

''' internal imports
'''
import classes.processor

''' classes
'''
class Cache(classes.processor.Processor):
	
	def run(self):
		
		print('lib.processors.session.Cache')

		cache = self.conf.get('cache',{})

		for var in cache:
			
			markup = self.element.fnr(cache[var])
			
			if markup.startswith('|'):
				
				try:
					markup = eval(markup.strip('|'))
				except Exception as e:
					print(e)
					markup = cache[var]
			
			self.top.session.vars[var] = markup
	
		return True


class Kill(classes.processor.Processor):
	
	def run(self):
		
		print('lib.processors.session.Kill')

		self.top.session.kill()
		
		return True
		
		
class Remove(classes.processor.Processor):
	
	def run(self):
		
		print('lib.processors.session.Remove')

		items = self.conf.get('items',[])

		for item in items:
			
			self.top.session.vars[item] = None
	
		return True