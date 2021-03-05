# path: lib/processors
# filename: shell.py
# description: WSGI application shell processors
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
import os
import subprocess

''' internal imports
'''
import classes.processor

''' classes
'''
class Shell(classes.processor.Processor):

	def run(self):
		
		#vars
		conf = self.conf
		debug = False

		if conf.get('debug'):
			
			print('lib.processors.shell.Shell')
			debug = True		
		
		# config checks
		cmd = conf.get('cmd')
		if not cmd:
			print('Shell command not found')
			
			return False
			
		cmd = self.content.fnr(cmd)
		
		if debug:
			print('running command: %s' %cmd)
		
		
		if conf.get('background'):
			
			try:
				
				subprocess.Popen(cmd, shell=True)
				
				return True
				
			
			except subprocess.CalledProcessError as e:

				self.top.cache['stdout'] = e
				
				if debug:
					print('stderr')
					print(e)
			
				# handle the stdout
				if conf.get('stderr'):
					
					conf['stderr']['value'] = e
					
					conf['stderr']['format'] = conf['stderr'].get('format','string')
					
					# load data
					if not self.content.load_data(conf['stderr']):
						
						print('failed to save - data failed to load')
							
						return False

				return False			
			
		else: 
			try:	
				result = subprocess.check_output(cmd, shell=True)
				
				# debug
				if debug:
					print('stdout')
					print(result)
				
				# handle the stdout
				if conf.get('stdout'):
					
					conf['stdout']['value'] = result
					
					conf['stdout']['format'] = conf['stdout'].get('format','string')
					
					# load data
					if not self.content.load_data(conf['stdout']):
						
						print('failed to save - data failed to load')
							
						return False
				
				return True
				
			except subprocess.CalledProcessError as e:

				self.top.cache['stdout'] = e
				
				if debug:
					print('stderr')
					print(e)
			
				# handle the stdout
				if conf.get('stderr'):
					
					conf['stderr']['value'] = e
					
					conf['stderr']['format'] = conf['stderr'].get('format','string')
					
					# load data
					if not self.content.load_data(conf['stderr']):
						
						print('failed to save - data failed to load')
							
						return False

				return False
		
		return False
