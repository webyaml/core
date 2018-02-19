# path: lib/processors
# filename: fiddle.py
# description: WSGI application fiddle processor

# make python2 strings and dictionaries behave like python3
from __future__ import unicode_literals

try:
	from builtins import dict, str
except ImportError:
	from __builtin__ import dict, str
	
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
import yaml

''' internal imports
'''
import classes.processor

''' classes
'''
class Fiddle(classes.processor.Processor):

	'''
	Description:
		
		Loop over a set of data to do more processing
	
	Usage:
	
		type: lib.processors.fiddle.Fiddle
	'''
	
	def run(self):
		
		print('lib.processors.fiddle.Fiddle')
		
		conf = self.conf

		if not conf.get('conf'):
			
			print('conf not in conf')
			return False
		
		# fnr
		conf['conf'] = self.content.fnr(conf['conf'])
		
		# handle includes
		# unset the includes list
		self.top.cache['includes'] = []
		# add the core processors conf for shortcut syntax
		conf['conf'] = 'include conf/processors/core.cfg\n%s' %conf['conf']
		# preform the includes
		conf['conf'] = self.top.includes(conf['conf'])
		
		print(conf['conf'])
		
		# simple anchors
		conf['conf'] = self.top.simple_anchor_syntax(conf['conf'])
		
		
		# convert conf to dict
		try:
			fiddle_conf = yaml.load(conf['conf'])
			
			self.content.tree({'content': fiddle_conf})
			
			return True
		
		except yaml.parser.ParserError as e:
			
			self.content.tree({'content': {'value': str(e)}})
			
			return False
			
		except yaml.composer.ComposerError as e:
			
			self.content.tree({'content': {'value': str(e)}})
			
			return False
			
		except yaml.scanner.ScannerError as e:
			
			self.content.tree({'content': {'value': str(e)}})
			
			return False	
		
		
		
		
		
		return True