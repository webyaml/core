# path: lib/processors/
# filename: redirect.py
# description: WSGI application redirect processors
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
import web
import re

''' internal imports
'''
import classes.processor

''' classes
'''
class Redirect(classes.processor.Processor):
	
	def run(self):
		
		conf = self.conf
		
		
		
		if not conf.get('url'):
			
			print('Redirect url not found')
			return False
		
		conf['url'] = self.content.fnr(conf['url'])
		
		# Remove any markers from output before returning
		if 'keepmarkers' not in conf:
			
			pattern = re.compile(r'({{[\w|\(|\)|\.|\:|\-]+}})')
			markers = list(set(pattern.findall(output)))

			for marker in markers:
				output = unicode(output.replace(marker,''))		
		
		raise web.seeother(conf['url'])
		
		return True  # this should never execute
		

	
