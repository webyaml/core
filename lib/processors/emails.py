# path: lib/processors/
# filename: email.py
# description: WSGI application sugar api processors
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
import datetime
import socket
import smtplib
from email.mime.text import MIMEText

''' internal imports
'''
import classes.processor

class Send(classes.processor.Processor):

	def run(self):
	
		#debug
		print('lib.processors.email.Send')
		
		
		# SMTP connection settings
		conf = self.conf['conf']

		if 'host' not in conf:
			print('missing smtp host')
			
			return False
		
		conf['port'] = str(conf.get('port',"25"))
			
		if 'user' not in conf:
			
			print('missing smtp user')
			
			return False			

		if 'pass' not in conf:
			
			print('missing smtp pass')
			
			return False

		# Message settings


		if 'body' not in self.conf:
			
			print('missing body')
			
			return False
			
		if 'subject' not in self.conf:
			
			print('missing subject')
			
			return False			
	
		if 'from' not in self.conf:
			
			print('missing from')
			
			return False

		if 'to' not in self.conf:
			
			print('missing to')
			
			return False
			
		conf.setdefault('security', 'none')
			
			
		rcptos = self.content.fnr(self.conf['to']).split(',')
			
		msg = MIMEText(self.content.fnr(self.conf['body']), "plain", "utf-8")
		msg['Subject'] = self.content.fnr(self.conf['subject'])
		msg['From'] = self.content.fnr(self.conf['from'])
		msg['To'] = self.content.fnr(self.conf['to'])
		
		if 'cc' in self.conf:
			msg['Cc'] = self.content.fnr(self.conf['cc'])
			
			rcptos.extend(self.content.fnr(self.conf['cc']).split(','))

		if 'bcc' in self.conf:
			msg['Bcc'] = self.content.fnr(self.conf['bcc'])
			
			rcptos.extend(self.content.fnr(self.conf['bcc']).split(','))
		
		msg['Date'] = datetime.datetime.utcnow().strftime( "%a, %d %b %Y %H:%M:%S %z %Z" )
		
		#debug
		#print(rcptos)
		#print(msg)

		if conf['security'] == 'tls':
			
			s = smtplib.SMTP_SSL(self.content.fnr(conf['host']),self.content.fnr(conf['port']),socket.gethostname())
			
		else:
		
			s = smtplib.SMTP(self.content.fnr(conf['host']),self.content.fnr(conf['port']),socket.gethostname())
			
		#s.ehlo()
		
		if conf['security'] == 'starttls':
			
			s.starttls()
		
		s.login(self.content.fnr(conf['user']),self.content.fnr(conf['pass']))
		s.sendmail(self.content.fnr(self.conf['from']), rcptos, msg.as_string())
		s.quit()
		
		
		return True
