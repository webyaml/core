# path: lib/processors
# filename: logic.py
# description: WSGI application logic processors

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

''' internal imports
'''
import classes.processor

''' classes
'''
class Evaluate(classes.processor.Processor):
	
	def run(self):
		
		expression = self.conf.get('expression')

		if expression:
			
			expression = self.element.fnr(expression)
			
			#debug
			print(expression)
			
			if 'messages' not in self.top.session:				
				self.top.session.messages = []
			
			if eval(expression):
				
				#debug
				print("True")

				if self.conf.get('messages'):
					
					if 'true' in self.conf['messages']:
						
						for message in self.conf['messages']['true']:
						
							msg = self.element.fnr(self.conf['messages']['true'][message])
					
							self.element.messages.append([message,msg])
							
							self.top.session.messages.append([message,msg])
				
				return True
				
			else:
				
				#debug
				print("False")
				
				if self.conf.get('messages'):
					
					if 'false' in self.conf['messages']:
					
						for message in self.conf['messages']['false']:
						
							msg = self.element.fnr(self.conf['messages']['false'][message])
					
							self.element.messages.append([message,msg])
				
				return False
