# path: lib/processors/
# filename: ftp.py
# description: WSGI application sugar api processors

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
import ftplib
import os

''' internal imports
'''
import classes.processor

class Upload(classes.processor.Processor):

	def run(self):
	
		#debug
		print('lib.processors.ftp.Upload')
		
		
		# FTP connection settings
		conf = self.conf['conf']

		if 'host' not in conf:
			print('missing smtp host')
			
			return False
		
		conf['port'] = int(conf.get('port',"21"))
			
		if 'user' not in conf:
			
			print('missing smtp user')
			
			return False			

		if 'pass' not in conf:
			
			print('missing smtp pass')
			
			return False
			
		# debug
		#print(self.content.fnr(conf['user']),self.content.fnr(conf['pass']))

		ftp = ftplib.FTP(self.content.fnr(conf['host'])) #,self.content.fnr(conf['port'])
		ftp.login(self.content.fnr(conf['user']),self.content.fnr(conf['pass']))
		
		if 'remotepath' in self.conf:
			ftp.cwd(self.content.fnr(self.conf['remotepath']))
		
		
		ftp.storbinary("STOR " + self.content.fnr(os.path.split(self.conf['file'])[1]), open(self.content.fnr(self.conf['file']), "rb"), 8192)
		
		
		return True


class Download(classes.processor.Processor):

	def run(self):
	
		#debug
		print('lib.processors.ftp.Download')
		
		
		# FTP connection settings
		conf = self.conf['conf']

		if 'host' not in conf:
			print('missing smtp host')
			
			return False
		
		conf['port'] = int(conf.get('port',"21"))
			
		if 'user' not in conf:
			
			print('missing smtp user')
			
			return False			

		if 'pass' not in conf:
			
			print('missing smtp pass')
			
			return False
			
		# debug
		#print(self.content.fnr(conf['user']),self.content.fnr(conf['pass']))

		ftp = ftplib.FTP(self.content.fnr(conf['host'])) #,self.content.fnr(conf['port'])
		ftp.login(self.content.fnr(conf['user']),self.content.fnr(conf['pass']))
		
		if 'remotepath' in self.conf:
			ftp.cwd(self.content.fnr(self.conf['remotepath']))

		localpath = self.content.fnr(self.conf.get('localpath','.'))	
		
		ftp.retrbinary("RETR " +  self.content.fnr(self.conf['file']) ,open("%s/%s"%(localpath,self.content.fnr(os.path.split(self.conf['file'])[1])), 'wb').write)
		
		return True

 

