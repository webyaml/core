# path: classes/
# filename: processor.py
# description: WSGI application processor

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
#import
import traceback
import datetime
from decimal import Decimal
import copy

''' internal imports
'''
#import

''' classes
'''
class Processor(object):

	def __init__(self,conf,element):
		
		# vars
		self.conf = copy.copy(conf)
		self.element = element
		self.content = self.element.content
		self.top = self.element.content.top
		self.parent = self.element.content.parent
		#self.data = None
		self.data = self.element.data
		
		return None

	# data handling
	def load_data(self,conf):

		return self.element.load_data(conf)
