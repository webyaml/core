# path: lib/elements/
# filename: field.py
# description: WSGI application html form fields

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
import web
import traceback

''' internal imports
'''
import classes.element
import field_dropdown
import field_radio

''' Base Form Field Class
'''
class Input(classes.element.Element):
	
	def __init__(self,content,definition="web.form.Textbox(name,*validators,**attrs)"):
		
		#print('lib.elements.field.Input')
		
		# super class Element
		super(Input, self).__init__(content)
		
		# vars
		self.definition = definition

		# name
		self.name = self.conf.setdefault('name')
		
		if not self.name:
			print('ERROR - field name not given')
		
		# args (values)
		self.args = self.conf.setdefault('values',[])

		# args (data)
		if self.conf.get('data'):
			
			self.conf['data'].setdefault('format','list')
			self.conf['data'].setdefault('value',[])
			
			# debug
			#print('loading data')
			
			if not self.content.load_data(self.conf['data']):
				print('data failed to load')
				
			else:
				
				# debug
				#print(self.content.data)
					
				if not isinstance(self.content.data,list):
					print('warning - data is not a list')
					
				else:
					self.args.extend(self.content.data)
		
		'''	Needed by dropdown, hope to find a better solution
		'''
		# args (valuesObj)
		values_obj = self.conf.get('valuesObj')
		if values_obj:
			try:
				self.args.extend(eval('self.top.%s' %values_obj))
			except:
				pass

		# validators
		self.validators = self.conf.get('validators', [])
		
		if 'required' in self.conf:
			self.conf.setdefault('required_indicator', '*')
			self.validators.append("web.form.notnull")
			
		else:
			# unset required indicator
			self.conf['required_indicator'] = ''
		
		# convert (eval) validators for web.py
		validators = []
		
		for validator in self.validators:
			validators.append(eval(validator))
		
		self.validators = validators
		
		# attrs (attributes)
		self.attrs = self.conf.get('attributes', {})
		
		# attrs hacks	
		if 'class' in self.attrs:
			self.attrs['class_'] = self.attrs['class']
			del self.attrs['class']
		
		if 'class' in self.conf:
			self.attrs['class_'] = self.conf['class']
		
		if not self.attrs.get('class_'):
			self.attrs['class_']  = ""
		
		if 'baseclass' in self.conf:
			self.attrs['class_'] = "%s %s" %(self.conf['baseclass'], self.attrs['class_'])
		
		
		# value hacks
		if 'value' in self.conf:
			self.attrs['value'] = self.conf['value']

		# markup value
		if 'value' in self.attrs:
			self.attrs['value'] = self.content.fnr(self.attrs['value'])
		
		return None

	
	def fieldObj(self):
		
		#debug
		#print('lib.elements.field.Input fieldObj()')
		
		# vars
		name = self.name
		args = self.args
		validators = self.validators
		attrs = self.attrs
		
		# make fieldObj
		self.content.fieldObj = eval(self.definition)
		self.content.fieldObj.content = self.content
		
		return self.content.fieldObj
	
	
	def render(self):
		
		#debug
		#print('lib.elements.field.Input render()')
		
		''' 	This is an interesting use of fnr_types.  This concept could be used a lot more.
		'''
		# add {{field:$attr}} to fnr_types
		self.content.fnr_types.update({'field': 'self.fieldObj.attrs'})
		
		# is this field in an error state?
		if self.content.fieldObj.note:
			
			# this field has an error push note
			self.conf['note'] = self.content.fieldObj.note
			
			# set error class default bootstrap has-error
			self.conf.setdefault('error_class', 'has-error')
			
		else:
			
			# clear values for non error state
			self.conf['error_class'] = ''
			self.conf['note'] = ''
		
		# render field using webpy method
		return self.content.fieldObj.render()


''' Form Field Classes
'''
class Button(Input):
	
	def __init__(self,content):
		
		#debug
		#print('lib.elements.field.Button')
		
		# super class Input
		super(Button, self).__init__(content,"web.form.Button(name,*validators,**attrs)")
		
		# instanciate fieldObj
		try:
			self.fieldObj()
			
		except: traceback.print_exc()		
		
		return None


class Hidden(Input):
	
	def __init__(self,content):
		
		#debug
		#print('lib.elements.field.Hidden')
		
		# super class Input
		super(Hidden, self).__init__(content,"web.form.Hidden(name,**attrs)")
		
		# instanciate fieldObj
		try:
			self.fieldObj()
			
		except: traceback.print_exc()		

		return None

	
class Textbox(Input):
	
	def __init__(self,content):
		
		#debug
		#print('lib.elements.field.Textbox')
		
		# super class Input
		super(Textbox, self).__init__(content,"web.form.Textbox(name,*validators,**attrs)")
		
		# instanciate fieldObj
		try:
			self.fieldObj()
			
		except: traceback.print_exc()		
		
		return None


class Textarea(Input):
	
	def __init__(self,content):
		
		#debug
		#print('lib.elements.field.Textarea')
		
		# super class Input
		super(Textarea, self).__init__(content,"web.form.Textarea(name,*validators,**attrs)")
		
		# instanciate fieldObj
		try:
			self.fieldObj()
			
		except: traceback.print_exc()		

		return None


class Password(Input):
	
	def __init__(self,content):
		
		#debug
		#print('lib.elements.field.Password')
		
		# super class Input
		super(Password, self).__init__(content,"web.form.Password(name,*validators,**attrs)")
		
		# instanciate fieldObj
		try:
			self.fieldObj()
			
		except: traceback.print_exc()		
		
		return None


class Dropdown(Input):
	
	def __init__(self,content):
		
		#debug
		#print('lib.elements.field.Dropdown')
		
		# super class Input
		super(Dropdown, self).__init__(content,"field_dropdown.Dropdown(name,args,*validators,**attrs)")
		
		# instanciate fieldObj
		try:
			self.fieldObj()
			
		except: traceback.print_exc()		
		
		return None


class Radio(Input):
	
	def __init__(self,content):
		
		#debug
		#print('lib.elements.field.Radio')
		
		# super class Input
		super(Radio, self).__init__(content,"field_radio.Radio(name,args,*validators,**attrs)")
		
		if 'innerwrap' in self.conf:
			self.attrs['wrap'] = self.conf['innerwrap']		
		
		# instanciate fieldObj
		try:
			self.fieldObj()
			
		except: traceback.print_exc()		
		
		return None


class Checkbox(Input):
	
	def __init__(self,content):
		
		#debug
		#print('lib.elements.field.Checkbox')
		
		# var
		self.conf = content.attributes
		
		# set value to True if not set
		self.conf.setdefault('attributes',{})
		self.conf['attributes'].setdefault('value', 'True')
		
		# super class Input
		super(Checkbox, self).__init__(content,"web.form.Checkbox(name,*validators,**attrs)")
		
		# instanciate fieldObj
		try:
			self.fieldObj()
			
		except: traceback.print_exc()		
		
		return None
	

class File(Input):
	
	def __init__(self,content):
		
		#debug
		#print("lib.elements.field.File")

		# super class Input
		super(File, self).__init__(content,"web.form.File(name,*validators,**attrs)")
		
		# instanciate fieldObj
		try:
			self.fieldObj()
			
		except: traceback.print_exc()		
		
		# upload?
		if self.top.post_vars and self.name in self.top.post_vars:
			
			if 'multiple' in self.attrs:
				
				# single or many?
				'''
				# single
				FieldStorage('files', 'file1.txt', 'file1content')
				'''
				
				'''
				# many
				[
					FieldStorage('files', 'file1.txt', 'file1content'), 
					FieldStorage('files', 'file2.txt', 'file2content')
				]
				'''
				# Convert single to many
				if not isinstance(self.top.post_vars[self.name],list):
					
					self.top.post_vars[self.name] = [self.top.post_vars[self.name]]
				
				data = []
				filenames = []
				for item in self.top.post_vars[self.name]:				
					data.append({
						"name": item.filename,
						"value": item.value,
					})
					
					filenames.append(item.filename)
				
				# save filename and file in session
				self.top.session.vars[self.name] = data

				# replace value from postvars with just filename
				self.top.post_vars[self.name] = ",".join(filenames)
				
				# add filename to attributes
				self.conf.setdefault('filename','<label>Uploaded Filename:</label> %s'%self.top.post_vars[self.name])
			
			else:
		
				if self.top.post_vars[self.name].filename and self.top.post_vars[self.name].value:
					
					#debug
					#print('found filename and value')
					
					# store filename and file
					data = {
						"name": self.top.post_vars[self.name].filename,
						"value": self.top.post_vars[self.name].value,
					}
					
					# save filename and file in session
					self.top.session.vars[self.name] = data

					# replace value from postvars with just filename
					self.top.post_vars[self.name] = self.top.post_vars[self.name].filename

					# add filename to attributes
					self.conf.setdefault('filename','<label>Uploaded Filename:</label> %s'%self.top.post_vars[self.name])
				
				'''#debug
				else:
					print('filename and value not found')
				'''
		
		return None


''' this must have been an expirement.  should really go
'''

class Generic(Input):
	
	def __init__(self,content):
		
		#debug
		#print("lib.elements.field.File")

		# super class Input
		super(Generic, self).__init__(content,"web.form.File(name,*validators,**attrs)")
		
		# instanciate fieldObj
		try:
			self.fieldObj()
			
		except: traceback.print_exc()		
		
		# upload?
		if self.top.post_vars and self.name in self.top.post_vars:
			self.conf['attributes'].setdefault('value', self.top.post_vars[self.name])
			
		return None
			
