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
		self.store(conf['args'],name='args')
		
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
		self.store(conf['args'],name='args')
		
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

# original processors before changing data inputs				
				

class GET_old(Rest):
	
	
	def run(self):

		print('lib.processors.rest.GET')

		#vars
		conf = self.conf
		
		# Name of Object that will store the result
		if 'name' not in conf:
			print("'name' not in conf")
			return False
		conf['name'] = self.element.fnr(conf['name'])

		# Data Format
		format = self.conf.get('format')
		if 'format' not in self.conf:
			
			print('format not in conf')
			print('using json')
			format = 'json'
			
		else:
			print('format is %s' %format)

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
		self.store(conf['args'],name='args')
		
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
		
		#make request
		r = requests.get(conf['url'], verify=False, headers=conf['headers'], auth=auth)
			
		# debug
		#print(r.text)
		
		if format == 'json':
			try:
				self.store(json.loads(r.text))
				return True
				
			except:
				
				return False
			
		elif format == 'xml':
			
			try:
				result = xmltodict.parse(r.text)
				
				if 'topObj' in conf:
					
					self.store(eval("result%s" %conf['topObj']))
					return True
					
				self.store(result)
				return True
				
			except:
				
				return False
			
		else:
			try:
				self.store(r.text)
				return True
				
			except:
				
				return False
		
class POST_old(Rest):
	
	
	def run(self):

		print('lib.processors.rest.POST')

		#vars
		conf = self.conf
		
		# Name of Object that will store the result
		if 'name' not in conf:
			print("'name' not in conf")
			return False
		conf['name'] = self.element.fnr(conf['name'])

		# Data Format
		format = self.conf.get('format')
		if 'format' not in self.conf:
			
			print('format not in conf')
			print('using json')
			format = 'json'
			
		else:
			print('format is %s' %format)

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
		self.store(conf['args'],name='args')
			
		# Data (POST Vars)
		data = conf.get('data',{})
		
		if isinstance(data, str):
			data = self.element.fnr(data)	
		else:
			# Markup Data
			for arg in data:
				data[arg] = self.element.fnr(data[arg])

		# debug
		print(data)

		# Auth
		auth = ()
		conf.setdefault('auth',())
		if conf['auth']:
			try:
				auth = (conf['auth']['username'],conf['auth']['password'])
			except:
				pass
		
		
		# Markup URL
		conf['url'] = self.element.fnr(conf['url'])		
		
		#make request
		r = requests.post(conf['url'], verify=False, headers=conf['headers'], data=data, auth=auth)
		
		# debug
		print(r.text)
		
		if format == 'json':
			try:
				self.store(json.loads(r.text))
				return True
				
			except:
				
				return False
			
		elif format == 'xml':

			try:
				result = xmltodict.parse(r.text)
				
				if 'topObj' in conf:
					
					self.store(eval("result%s" %conf['topObj']))
					return True
					
				self.store(result)
				return True
				
			except:
				
				return False
			
		else:
			try:
				self.store(r.text)
				return True
				
			except:
				
				return False				
				