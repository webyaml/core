# path: lib/elements/
# filename: form.py
# description: WSGI application html form elements
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
import traceback

''' internal imports
'''
import classes.element


''' Form Element
'''
class Form(classes.element.Element):

	def __init__(self,content):
		
		#print('lib.elelments.form.Form')
		
		# super class Element
		super(Form, self).__init__(content)

		# vars
		#self.conf = self.content.attributes
		
		
		self.fields = []
		self.elements = []

		# defaults
		self.conf.setdefault('name', 'default_form_name')
		self.conf.setdefault('id', self.conf['name'])
		self.conf.setdefault('method', 'post')
		self.conf.setdefault('action', '')
		
		# search for form fields in the tree
		self.fields = self.field_search(self.content)
		
		# evaluate validators
		validators = []
		for validator in self.conf.get('validators', []):
			#validators.append(eval(validator))
			validators.append(eval(self.content.fnr(validator)))
	
		print(validators)
	
		# instanciate form object with validators
		self.formObj = web.form.Form(*self.fields, validators=validators)	
		
		''' do no futher actions unless this form was submitted
		'''
		
		# Was this form submited?
		if self.top.post_vars.get('form_name') == self.conf['name']:
			
			for i in range(0,len(self.fields)):
				
				# remove validtors from non required fields if they are empty
				'''	The code below allows values to valdated only when the input is given.
					For instance a optional email field with a regex validator.
				'''				
				if 'required' not in self.elements[i].attributes and self.fields[i].name not in self.top.post_vars:
					self.fields[i].validators = []
					continue
					
				# remove validtors from disabled fields
				'''	Disabled fields do not submit post vars.  If a disabled field has a valaditor 
					then this form will never valdate.  The code below fixes that problem. 
				'''				
				if self.elements[i].attributes.get('attributes') and self.elements[i].attributes['attributes'].get('disabled'):
					self.fields[i].validators = []
			
			# Does the form validate
			if self.formObj.validates(source=self.top.post_vars):
				
				print('Form validates')
				
				# do processing here
				self.content.process(self.conf.get('postprocess',{}))
				
			else:
				
				print('Form does not validate')
				
				# Add form note to attributes
				if self.formObj.note:
					self.conf['note'] = self.formObj.note
				
				# reset fields if neccessary
				for field in self.fields:

					if 'reset' in field.content.attributes:
						field.value = None
		
		return None
	

	def field_search(self,content=[]):
		
		# debug
		#print('lib.elelments.form.Form field_search()')
		
		for item in content:
			
			# debug
			#print('recurse')
			
			try:
				self.field_search(item) # recurse
				
			except: traceback.print_exc()
			
			if 'fieldObj' in dir(item):
				
				self.fields.append(item.fieldObj)
				self.elements.append(item)
			
		return self.fields
	
	
	def render(self):
		
		# debug
		#print('lib.elelments.form.Form render()')
		
		return '<input type="hidden" name="form_name" value="%s">\n' % self.conf['name']



		