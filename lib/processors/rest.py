# path: lib/processors
# filename: rest.py
# description: WSGI application ReSTful processors

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
import json
import requests
import xmltodict
import yaml

''' internal imports
'''
import classes.processor

''' classes
'''

class Rest(classes.processor.Processor):

	# collect duplicated parts here

	pass



class GET(Rest):
	
	
	def run(self):

		print('lib.processors.rest.GET')

		#vars
		conf = self.conf
		
		# Target URL
		if 'url' not in conf:
			print("'url' not in conf")
			return False

		# Headers
		conf.setdefault('headers',{})
		
		# Args (URL Markers)
		conf.setdefault('args',{})
		
		# Markup Args
		for arg in conf['args']:
			conf['args'][arg] = self.element.fnr(conf['args'][arg])
		
		# store args
		#self.store(conf['args'],name='args')
		if conf['args']:
			self.load_data({'format': 'raw', 'store': 'args', 'value': conf['args']})	
		
		# Markup URL
		conf['url'] = self.element.fnr(conf['url'])

		# Auth
		auth = ()
		conf.setdefault('auth',())
		if conf['auth']:
			try:
				auth = (conf['auth']['username'],conf['auth']['password'])
			except:
				pass
		
		# debug
		print("url is '%s'" %conf['url'])
		
		#make request
		
		#debug
		print('making request')
		
		r = requests.get(conf['url'], verify=False, headers=conf['headers'], auth=conf['auth'])

		# debug
		print('request complete')
		print(r)
		
		# handle the returned data
		if conf.get('receive'):
			
			conf['receive']['value'] = r.text
			
			# load data
			if not self.load_data(conf['receive']):
				
				print('failed to send - data failed to load')
					
				return False
		
		#print('GET successful')
		
		return True
		
		
class POST(Rest):
	
	
	def run(self):

		print('lib.processors.rest.POST')

		#vars
		conf = self.conf
		
		# Target URL
		if 'url' not in conf:
			print("'url' not in conf")
			return False

		# Headers
		conf.setdefault('headers',{})
		
		# Args (URL Markers)
		conf.setdefault('args',{})
		
		# Markup Args
		for arg in conf['args']:
			conf['args'][arg] = self.element.fnr(conf['args'][arg])
		
		# store args
		#self.store(conf['args'],name='args')
		self.load_data({'format': 'raw', 'store': 'args', 'value': conf['args']})
		
		# Markup URL
		conf['url'] = self.element.fnr(conf['url'])

		# Auth
		auth = ()
		conf.setdefault('auth',())
		if conf['auth']:
			try:
				auth = (conf['auth']['username'],conf['auth']['password'])
			except:
				pass
		
		# is data being loaded to send?
		if conf.get('send'):
			
			# load data and format it for sending
			
			# load data
			if not self.load_data(conf['send']):
				
				print('failed to send - data failed to load')
					
				return False
				
		''' If this is not working add 
			self.data = self.element.data
		'''
		#debug
		print(self.data)
		
		
		try:
		
			#make request
			r = requests.post(conf['url'], verify=False, headers=conf['headers'], auth=conf['auth'], data=self.data)
				
			# debug
			print(r.text)
		
		except Exception as e:
			
			print(e)
			
			return False
			
		
		# handle the returned data
		if conf.get('receive'):
			
			
			conf['receive']['value'] = r.text
			
			# load data
			if not self.load_data(conf['receive']):
				
				print('failed to send - data failed to load')
					
				return False

		return True				
