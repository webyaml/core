# path: lib/elements/
# filename: tabs.py
# description: Bootstrap Tabs element

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
import copy

''' internal imports
'''
import classes.element

class Tabs(classes.element.Element):

	def __init__(self,content):
		
		# vars
		self.tabs = []
		
		# super class Element
		super(Tabs, self).__init__(content)
		
		# search for tabs (one level)
		for item in content:
			
			self.tabs.append(item)
			
		#print('self.tabs'+str(self.tabs))
		
		# change the wrap for each tab
		
		class_ = ' active in'
		
		for tab in self.tabs:
			
			name = tab.attributes.get('name','')
			id = tab.attributes.get('id',name)			
			
			tab.attributes['wrap'] = '<div class="tab-pane fade'+class_+'" id="'+id+'">|</div>'
			
			class_ = ''
		
		return None
	

	def render(self):
		
		style = 'nav-%s' %self.content.attributes.get('style','tabs') 
		
		# this needs some work.  it should use the wrap not kill it
		# perhapps coupling this with an element library would solve this problem
		wrap = ''
		
		class_ = " active"
		
		for tab in self.tabs:
			
			name = tab.attributes.get('name','')
			id = tab.attributes.get('id',name)
			
			wrap += '<li class="'+class_+'"><a href="#'+id+'" data-toggle="tab">'+name+'</a></li>'
			
			class_ = ''
	
		self.content.attributes['wrap'] = '<ul class="nav '+style+'">'+wrap+'</ul><div class="tab-content">|</div>'

		return ''
