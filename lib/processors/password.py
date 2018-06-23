# path: lib/processors
# filename: password.py
# description: WSGI application password hashing processors
''' 
# make python2 strings and dictionaries behave like python3
from __future__ import unicode_literals

try:
	from builtins import dict, str
except ImportError:
	from __builtin__ import dict, str
	

	Copyright 2018 Jordan Howell and Mark Madere

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
import uuid
import hashlib

''' internal imports
'''
import classes.processor

''' classes
'''
class Hash(classes.processor.Processor):

	'''
		process:
			type: lib.processors.password.Hash
			function: sha256 # sha256 is the default.  other options are : sha512, sha1024
			salt: '{{uuid()}}' # default is a random uuid
			data:
				value: '{{password}}'
				store: 'hash'
	'''
	
	def run(self):
		
		# vars
		conf = self.conf
		debug = False		

		functions = {
			'sha256': hashlib.sha256,
			'sha512': hashlib.sha512,
			}

		
		if conf.get('debug'):
			
			print('lib.processors.password.Hash')
			debug = True

		# conf checks
		
		if 'data' not in conf:

			# conf['data'] does not exist
			print('Error: data not given')
			return False

		if not 'value' in conf['data']:

			#conf['data']['value'] does not exist
			print('Error: data:value not given')
			return False


		if not 'store' in conf['data']:
			
			#conf['data']['store'] does not exist
			print('Error: data:store not given')
			return False
	
		# hash algorithm 
		
		function = conf.get('function', 'sha256')

		if function not in functions:
			
			print("Error: the hash algorithm '%s' is invalid." %function)
			return False
		
		# salt

		if 'salt' in conf:
			salt = self.content.fnr(conf['salt'], 1)
		else:
			salt = uuid.uuid4().hex

		# make the hash
		
		input = salt.encode() + self.content.fnr(conf['data']['value']).encode()
		conf['data']['value'] = functions[function](input).hexdigest() + ':' + salt
		conf['data']['format'] = 'string'

		# debug output
		
		if debug:
			
			print('salt: %s' %str(salt))
			print('hash: %s' %str(conf['data']['value']))
		
		# store the hash
		if not self.content.load_data(conf['data']):
			
			print('failed to store hash')	
			return False

		# success
		
		return True	


