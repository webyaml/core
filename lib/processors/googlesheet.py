# filename: lib/processors/googlesheet.py
# description: GoogleSheet datasource processors

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

''' Uses Google Sheets API python library
https://developers.google.com/resources/api-libraries/documentation/sheets/v4/python/latest/index.html
'''

''' external imports
'''
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
import apiclient

''' internal imports
'''
import classes.processor

''' classes
'''
class Read(classes.processor.Processor):

	def auth(self,keyfile):

		scopes = ['https://www.googleapis.com/auth/spreadsheets']

		credentials = ServiceAccountCredentials.from_json_keyfile_name(keyfile, scopes=scopes)

		http_auth = credentials.authorize(Http())
		
		return http_auth


	def run(self):
		
		print('lib.processors.googlesheet.Read')
		
		conf = self.conf
		
		# debug
		#print(conf)
		
		if not conf.get('keyfile'):
		
			print('keyfile not found in conf')
			
			return False

		if not conf.get('sheet'):
		
			print('sheet not found in conf')
			
			return False

		if not conf.get('range'):
		
			print('range not found in conf')
			
			return False

		conf.setdefault('reader', 'list')
		
		# perform auth
		http = self.auth(conf['keyfile'])
		
		# read the sheet
		discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
		service = apiclient.discovery.build('sheets', 'v4', http=http,discoveryServiceUrl=discoveryUrl)
		
		
		try:
		
			result = service.spreadsheets().values().get(spreadsheetId=conf['sheet'], range=conf['range']).execute()
			
		except Exception as e:
			
			print(e)
			
			return False
		
		if result:
			
			# if reader is dict convert output
			if conf['reader'] == 'dict':
				
				headers = result['values'][0]
				
				print(headers)
				
				output = []
				for record in result['values'][1:]:
					
					#ensure the length of each record is correct
					while len(record) < len(headers):
						
						record.append('')

					#convert
					new_record = {}
					for i in range(0,len(headers)):
						
						new_record[headers[i]] = record[i]
						
					output.append(new_record)
			
				conf['result']['format'] = 'raw'
				conf['result']['value'] = output
				conf['result']['entry'] = None
			
			# if reader is list set oputput options
			if conf['reader'] == 'list':
				
				conf['result']['format'] = 'raw'
				conf['result']['value'] = result['values']
				conf['result']['entry'] = None				


			# handle the returned data
			if conf.get('result'):
				
				# load data
				if not self.content.load_data(conf['result']):
					
					print('failed to read - data failed to load')
						
					return False

			return True
		
		# no result
		return False
		
		
class Write(classes.processor.Processor):

	def auth(self,keyfile):

		scopes = ['https://www.googleapis.com/auth/spreadsheets']

		credentials = ServiceAccountCredentials.from_json_keyfile_name(keyfile, scopes=scopes)

		http_auth = credentials.authorize(Http())
		
		return http_auth


	def run(self):
		
		print('lib.processors.googlesheet.Write')
		
		conf = self.conf
		
		# debug
		#print(conf)
		
		if not conf.get('keyfile'):
		
			print('keyfile not found in conf')
			
			return False

		if not conf.get('sheet'):
		
			print('sheet not found in conf')
			
			return False

		if not conf.get('range'):
		
			print('range not found in conf')
			
			return False

		if not conf.get('data'):
		
			print('data not found in conf')
			
			return False

		# load data
		if not self.content.load_data(conf['data']):
			
			print('failed to Write - data failed to load')
			
			return False
		
		# perform auth
		http = self.auth(conf['keyfile'])
		
		# read the sheet
		discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
		service = apiclient.discovery.build('sheets', 'v4', http=http,discoveryServiceUrl=discoveryUrl)
		
		body = {
			'values': self.data
		}		
		
		try:
			result = service.spreadsheets().values().update(
				spreadsheetId=conf['sheet'], range=conf['range'],
				valueInputOption='USER_ENTERED', body=body).execute()
			
		except Exception as e:
			
			print(e)
			
			return False
		
		if result:

			return True
		
		# no result
		return False
		
from apiclient import errors		

class Function(classes.processor.Processor):

	def auth(self,keyfile):

		scopes = ['https://www.googleapis.com/auth/spreadsheets']

		credentials = ServiceAccountCredentials.from_json_keyfile_name(keyfile, scopes=scopes)

		http_auth = credentials.authorize(Http())
		
		return http_auth


	def run(self):
		
		print('lib.processors.googlesheet.Function')
		
		conf = self.conf
		
		# debug
		#print(conf)
		
		if not conf.get('keyfile'):
		
			print('keyfile not found in conf')
			
			return False

		if not conf.get('script'):
		
			print('script not found in conf')
			
			return False

		if not conf.get('request'):
		
			print('request not found in conf')
			
			return False
			
		if not isinstance(conf['request'], dict):
		
			print('request is not a dictionary')
			
			return False			

		conf.setdefault('reader', 'list')
		
		# perform auth
		http = self.auth(conf['keyfile'])
	
		# read the script
		# https://script.googleapis.com/v1/scripts
		discoveryUrl = ('https://script.googleapis.com/$discovery/rest?version=v1')
		service = apiclient.discovery.build('script', 'v1', http=http,discoveryServiceUrl=discoveryUrl)
		
		try:
		
			result = service.scripts().run(body=conf['request'],scriptId=conf['script']).execute()

		except errors.HttpError as e:
			# The API encountered a problem before the script started executing.
			print(e.content)
			
			return False
			
		except Exception as e:
			
			print(e)
			
			return False
		
		if result:
			
			# if reader is dict convert output
			if conf['reader'] == 'dict':
				
				headers = result['values'][0]
				
				print(headers)
				
				output = []
				for record in result['values'][1:]:
					
					#ensure the length of each record is correct
					while len(record) < len(headers):
						
						record.append('')

					#convert
					new_record = {}
					for i in range(0,len(headers)):
						
						new_record[headers[i]] = record[i]
						
					output.append(new_record)
			
				conf['result']['format'] = 'raw'
				conf['result']['value'] = output
				conf['result']['entry'] = None
			
			# if reader is list set oputput options
			if conf['reader'] == 'list':
				
				conf['result']['format'] = 'raw'
				conf['result']['value'] = result['values']
				conf['result']['entry'] = None				


			# handle the returned data
			if conf.get('result'):
				
				# load data
				if not self.content.load_data(conf['result']):
					
					print('failed to read - data failed to load')
						
					return False

			return True
		
		# no result
		return False
		
