# path: lib/
# filename: functions.py
# description: WSGI application marker functions
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

''' internal imports
'''

# marker attributes and functions
marker_map = {

	# FUNCTIONS
	
	'exists': 'self.view.mmethods.mm_exists',
	#'count': 'self.view.mmethods.mm_count',
	'len': 'self.view.mmethods.mm_len',
	'sum': 'self.view.mmethods.mm_sum',
	'random': 'self.view.mmethods.mm_random',
	
	# sanitizing
	'escape': 'self.view.mmethods.mm_escape',
	'escape_breaks': 'self.view.mmethods.mm_escape_breaks', #undocumented
	'html_breaks': 'self.view.mmethods.mm_html_breaks', #undocumented
	'escape_markers': 'self.view.mmethods.mm_escape_markers', #undocumented
	'html_markers': 'self.view.mmethods.mm_html_markers', #undocumented
	'html_escape': 'self.view.mmethods.mm_html_escape',
	'escape_script': 'self.view.mmethods.mm_escape_script',
	'space2p20': 'self.view.mmethods.mm_space2p20',

	# URI
	'url_quote': 'self.view.mmethods.mm_url_quote',
	'url_unquote': 'self.view.mmethods.mm_url_unquote',

	# decoration
	'keyword': 'self.view.mmethods.mm_keyword',
	'truncate': 'self.view.mmethods.mm_truncate',
	'last4': 'self.view.mmethods.mm_last4',
	'strip': 'self.view.mmethods.mm_strip',
	'singleline': 'self.view.mmethods.mm_singleline',
	#'remove': 'self.view.mmethods.mm_remove', #undocumented
	'dollar': 'self.view.mmethods.mm_dollar', #undocumented
	
	#'tab': 'self.view.mmethods.mm_tab',
	
	'lower': 'self.view.mmethods.mm_lower',
	'upper': 'self.view.mmethods.mm_upper',
	'title_case': 'self.view.mmethods.mm_title_case',
	
	'us_phone': 'self.view.mmethods.mm_us_phone',
	'us_ssn': 'self.view.mmethods.mm_us_ssn',
	
	# object formating
	'uuid': 'self.view.mmethods.mm_uuid',
	'date': 'self.view.mmethods.mm_date',
	'int': 'self.view.mmethods.mm_int',
	'string': 'self.view.mmethods.mm_string',
	
	'key_val_list': 'self.view.mmethods.mm_key_val_list',

	# hashing
	'sha256': 'self.view.mmethods.mm_sha256',
	'md5': 'self.view.mmethods.mm_md5',
	
	# object conversion
	'json': 'self.view.mmethods.mm_json',
	'yaml': 'self.view.mmethods.mm_yaml',
	#'csv': 'self.view.mmethods.mm_csv',
	
	# god only knows
	'join': 'self.view.mmethods.mm__join',
	'split': 'self.view.mmethods.mm_split',
	'list': 'self.view.mmethods.mm_list',
	#'cleanup': 'self.view.mmethods.mm_cleanup', # clean chinese crap			

}



def mm_int(self,obj):

	#debug
	#print('int')
	
	if isinstance(obj, basestring) and obj.strip().isdigit():
		return int(obj)
		
	return obj


def mm_split(self,obj):

	#debug
	#print('split')
	
	if isinstance(obj, basestring):
	
		delimiter = self.attributes.get('delimiter', " ")
		return obj.split(delimiter)
		
	return obj

def mm_space2p20(self,obj):

	#debug
	#print('space2p20')
	
	if isinstance(obj, basestring):
	
		return obj.replace(" ","%20")
		
	return obj


def mm_sha256(self,password):
	
	if not password:
		return password
	
	#debug
	#print('sha256')
	
	import crypt
	#import random
	#import string
	
	password = crypt.crypt(password, '$5$')
	
	return password


def mm_md5(self,password):
	
	if not password:
		return password		
	
	#debug
	#print('md5')
	
	import hashlib
	password = password.strip()
	return hashlib.md5(password).hexdigest()


def mm_dollar(self,f):
	
	''' Note: Needs to be a number formatter not specifc to USD
	'''

	#debug
	#print('dollar')
	
	if not isinstance(f,float):
		
		return 'fix me - dollar was not float'
		
	return "%.2f" %f


def mm_key_val_list(self,d):
	
	#debug
	#print('key_val_list')
	
	if not isinstance(d,dict):
		return d
	
	output = []
	for key in d:
		
		output.append({'key': key, 'val': d[key]})
	
	return output


def mm_len(self,l):
	
	#debug
	#print('marker:method:len')
	
	if not isinstance(l,list):
		
		#debug
		#print('not a list')
		
		
		# goad into list
		l = eval(l)
		if not isinstance(l,list):
			#debug
			#print("could not gaod into list")
			return l
	
	return len(l)

def mm_sum(self,l):
	
	#debug
	#print('sum')
	
	if not isinstance(l,list):
		return l
	
	return sum(l)


def mm_exists(self,obj):
	
	# debug
	#print('exists')
	#print('obj:'+str(obj))
	
	if isinstance(obj, basestring) and obj != '':
		return 'True'
		
	if obj:
		return 'True'
		
	return 'False'


def mm_singleline(self,obj):

	# debug
	#print('singleline')
	
	if not isinstance(obj,basestring):
		
		return ''
		
	output = []
	for line in obj.split('\n'):
		
		output.append(line.strip())
	
	return ' '.join(output)


def mm_escape_breaks(self,obj):
	
	''' needs to be merged with mm_singleline
	'''

	# debug
	#print('escape_breaks')
	
	if not isinstance(obj,basestring):
		
		return obj
		
	return obj.replace("\n",r"\\n").replace('\r',r'\\n')


def mm_strip(self,obj):

	# debug
	#print('strip')

	char = self.attributes.get('char', " ")

	#print(char)
	#print(type(obj))

	if not isinstance(obj,unicode):

		obj = unicode(obj)

	#obj =  obj.strip("\n").strip("\r").strip(char).strip()
	obj =  obj.strip("\n\r%s"%char)

	''' #consider adding the following
	if isinstance(obj,list):
	'''

	#print(obj)

	return obj



def mm_escape(self,obj):
	
	''' escape single and double qoutes in strings.
	'''

	# debug
	#print('escape')
	
	if isinstance(obj,list):
		string = ", ".join(obj)
	
	if isinstance(obj,basestring):
		obj = obj.replace("'",r"\'").replace('"',r'\"') #.replace(u'\u2019', r"\\u2019")
	
	return obj





def mm_html_breaks(self,obj):
	
	''' convert line breaks to html breaks
	'''

	# debug
	#print('convert_breaks')
	#print(type(obj))
	
	if not isinstance(obj,basestring):
		
		return obj
		
	return obj.replace("\n","</br>")


def mm_escape_markers(self,obj):
	
	''' escape braces in strings.
		this was added for dcoumetnation - it may not be needed
		
		Also it does not seem to be working.  the slashes are showing 
		on page.  expected marker without markup and no visible slashes.
		It does seem to work fine with ace editor
	'''

	# debug
	#print('escape_markers')
	
	if isinstance(obj,basestring):
		obj = obj.replace("{{","\{\{").replace('}}','\}\}')
	
	return obj


def mm__join(self,obj):

	# debug
	#print('_join')
	
	if isinstance(obj,list):
		
		delimiter = self.attributes.get('delimiter', " ")
		
		obj = delimiter.join(obj)
	
	return obj


def mm_json(self,obj):

	# debug
	#print('_json')	
	#print(obj)
	
	import json
	import decimal
	import datetime
	
	def walk(subobj):
		
		if isinstance(subobj,list):
			
			for i in range(0,len(subobj)):
				
				subobj[i] = walk(subobj[i])
		
		if isinstance(subobj,dict):
			
			for key in subobj:
				
				subobj[key] = walk(subobj[key])
		
		if isinstance(subobj,basestring):
			
			subobj = self.fnr(subobj)
		
		# Hack
		if isinstance(subobj,datetime.datetime):
			
			# uses the local date function to convert to string
			subobj = self.view.mmethods.mm_date(self,subobj)

		# Hack
		if isinstance(subobj,decimal.Decimal):
			
			subobj = unicode(subobj)
		
		return subobj
	
	obj = walk(obj)
	
	return  json.dumps(obj)


def mm_yaml(self,obj):
	
	# debug
	#print('_yaml')	
	#print(obj)
	
	import decimal
	import json
	import yaml		

	# tweak for utf-8
	def my_unicode_repr(self, data):
		return self.represent_str(data.encode('utf-8'))
	
	yaml.representer.Representer.add_representer(unicode, my_unicode_repr)
	
	obj = json.loads(self.view.mmethods.mm_json(self,obj))
	
	return yaml.dump(obj, allow_unicode=True, default_flow_style=False)


def mm_truncate(self,obj):

	# debug
	#print('truncate')	
	
	if isinstance(obj, basestring) or isinstance(obj,list):		
	
		# length attribute
		length = int(self.attributes.get('length',50))
		
		return obj[:length]

	return obj


def mm_html_escape(self,obj):

	# debug
	#print('html_escape')
	
	import cgi
	
	if isinstance(obj, basestring):
		
		return cgi.escape(obj,quote=True).replace("{","&#123;").replace("}","&#125;").replace('\\','') #.replace('/','\/')
	
	return obj


def mm_html_markers(self,obj):

	# debug
	#print('html_markers')

	if isinstance(obj, basestring):
	
		return obj.replace("{","&#123;").replace("}","&#125;")
	
	return obj		
	

def mm_uuid(self,obj):

	# debug
	#print('uuid')
	
	import uuid
	
	# random uuid
	return unicode(uuid.uuid4().hex) #any obj will be ignored


def mm_url_quote(self,obj):

	# docs - https://docs.python.org/2/library/urllib.html#urllib.quote_plus

	# debug
	#print('url_quote')	
		
	if isinstance(obj,basestring):
	
		import urllib
		obj = urllib.quote_plus(obj)
	
	return obj


def mm_url_unquote(self,obj):

	# debug
	#print('url_unquote')	

	import urllib

	if isinstance(obj,basestring):

		return urllib.unquote_plus(obj)

	return obj	


def mm_date(self,obj):

	# debug
	#print('date')	
	
	import datetime
	
	format = self.attributes.get('format', "%Y-%m-%d")
	
	# no object, current time
	if not obj:
		
		obj =  datetime.datetime.now()
	
	# datetime object
	if isinstance(obj,datetime.datetime):
		
		try:
		
			return datetime.datetime.strftime(obj,format)
		except:
			return obj
	
	# unix timestamp
	if isinstance(obj,basestring):
		
		if not obj.isdigit():
			
			return obj
			
		obj = int(obj)
	
	if isinstance(obj,int):
		
		return datetime.datetime.fromtimestamp(obj).strftime(format)

	return obj


def mm_last4(self,obj):

	# debug
	#print('last4')	
	
	if isinstance(obj,int):
		obj = str(obj)
	
	if isinstance(obj,basestring):		
		
		return "*"*(len(obj)-4)+ obj[-4:]
	
	return obj


def mm_keyword(self,obj):

	# debug
	#print('keyword')	
	
	if isinstance(obj,basestring):		
		
		return '<mark>%s</mark>'%obj
	
	return obj


def mm_string(self,obj):

	# debug
	#print('string')
	
	return unicode(obj)


def mm_upper(self,obj):

	# debug
	#print('string')
	
	return unicode(obj).upper()


def mm_lower(self,obj):

	# debug
	#print('string')
	
	return unicode(obj).lower()


def mm_title_case(self,obj):

	# debug
	#print('title_case')	
	
	if isinstance(obj,basestring):
	
		# split the string on spaces
		parts = obj.split()
		
		obj = []
		for part in parts:
			obj.append("%s%s" %(part[0].upper(),part[1:].lower()))
		
		return " ".join(obj)
	
	return obj


def mm_list(self, obj):
	
	# if the obj is not a list, make it the first element of a list
	if not isinstance(obj, list):
		obj = [obj]
	
	return obj


def mm_us_phone(self,obj):
	
	if not isinstance(obj,basestring):
		
		obj = unicode(obj)
	
	out = obj
	if obj != "":
	
		out = "(%s) %s-%s"%(obj[0:3],obj[3:6],obj[6:10])
	
	return out


def mm_us_ssn(self,obj):
	
	if not isinstance(obj,basestring):
		
		obj = unicode(obj)
	
	out = "%s-%s-%s"%(obj[0:3],obj[3:5],obj[5:9])
	
	return out


def mm_random(self,obj):
	
	if not isinstance(obj,list):
		return obj

	import random
	
	return random.choice(obj)


# wtf - was this really needed?
def mm_tab(self,obj):
	
	return '\t'


def mm_escape_script(self,obj):
	
	#print('escape_script')
	#print(type(obj))
	
	if isinstance(obj,basestring):
		
		return obj.replace('</script>','<\\/script>')
	
	#print('return default')
	#print(obj)
	return obj