#!/usr/bin/python
# path: core/
# filename: content.py
# description: WSGI application content tree

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
import os.path
import sys
import imp
import traceback

''' internal imports
'''
#import functions

''' classes
'''
class Content(list):

	def __init__(self,conf,parent=None):
		
		# super class list
		super(Content, self).__init__()
		
		# vars
		self.attributes = {}
		self.elementObj = None
		
		# parent object
		self.parent = parent
		
		# top object
		if 'top' not in dir(self.parent):
			self.parent.top = self.parent
			
		self.top = self.parent.top
		
		# recurse - Build a tree of Content Objects (a list of lists)
		self.tree(conf)
		
		# Dynamically load elements	
		element_type = self.attributes.get('type','classes.element.Element') # type/class of element or default
		m = ".".join(element_type.split('.')[:-1]) # module name and path
		c = ".".join(element_type.split('.')[-1:]) # class name
		
		#debug 
		#print('module: %s, class: %s' %(m,c))
		
		# import module

		# does the module exist in site directory
		if os.path.isfile("%s.py" %m.replace('.','/')):
			
			print('found a local module - importing')
			
			try:
				''' This is the new way to load modules.  
				'''		
				_module = imp.load_source(m,"%s.py" %m.replace('.','/'))
				
			except: traceback.print_exc()
			
		# does the module exist in core directory
		elif os.path.isfile("core/%s.py" %m.replace('.','/')):
			
			try:
				''' 	This is the traditional way to load modules.
				'''
				__import__(m)
				_module = sys.modules[m]  #load module
				
			except: traceback.print_exc()
			
		else:
			print("Could not find the the module '%s'." %m)
			
			return None

		# load class
		try:
			_class = getattr(_module,c)  
			
		except AttributeError:
			
			print("Could not find the class '%s' in the module '%s'." %(c,m))
			
			return None
		
		except: traceback.print_exc()
		
		
		# instanciate element object
		# The elementObj is where the output is constructed
		# a copy of this object is pased into elementObj
		self.elementObj = _class(self)
			
		return None


	def tree(self,conf):
		
		''' Create Content And Element Objects
		'''
		
		# Vars		
		if not self.attributes:
			self.attributes = conf
			'''
			This allows for configuration files to be parsed normally
			But let processors or content elements add new content
			without changing the attributes of the parent.
			
			To continue a content tree using this function the 
			conf should be sent in this format
			
			content: # will be ignored
				-
					#new content block
				-
					# another new content block
					
			If content is a dict it will be converted into a list.
			'''
		else:
			print(conf)
			
		
		if conf.get('content'):

			# convert dict to list
			if isinstance(conf['content'],dict):
				conf['content'] = [conf['content']]
			
			# recurse
			for item in conf['content']:
				try:
					self.append( type(self)(item,self) )
				except: traceback.print_exc()
		
		return None			

	
	def render(self):
		
		''' Render Element objects in tree
		'''
		
		#vars
		output = ''
		
		# render child elements
		for item in self:
			if isinstance(item, type(self)):
				output += item.render() #recurse
		
		# log entry if requested
		if 'log' in self.attributes:
			print(self.elementObj.fnr(self.attributes['log']))
		
		# render this element
		output = self.elementObj.render()+output
		
		# split wrap
		wrap = self.attributes.get('wrap','|').split("|",1)
		if len(wrap) == 1:
			wrap.append('')
		
		# Helpers for API formating

		if 'nomarkup' in self.attributes:
			
			#print('nomarkup')
			
			return  wrap[0]+output+wrap[1]

		if 'singlemarkup' in self.attributes:
			
			#print('singlemarkup')
			
			return  self.elementObj.fnr(wrap[0]+output+wrap[1])
		
		if 'noindent' in self.attributes or 'noindent' in self.top.attributes:
			
			#print('noindent')
			
			# double markup
			return  self.elementObj.fnr(self.elementObj.fnr(wrap[0]+output+wrap[1]))
		
		# Indent the output and wrap
		#print('indent')
		
		# double markup with indent
		return  self.elementObj.fnr(self.elementObj.fnr(self.indent("%s\n%s\n%s" %(wrap[0],output,wrap[1]))))
	

	def indent(self,input,prefix="  "):
		
		# vars
		output = ''
		
		if self.top == self.parent:
			return input
		
		for line in input.split('\n'):
			output += prefix+str(line)+"\n"		
		
		return output.rstrip("\n")	
