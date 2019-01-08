'''
# make python2 strings and dictionaries behave like python3
from __future__ import unicode_literals

try:
	from builtins import dict, str
except ImportError:
	from __builtin__ import dict, str
'''
# This is a replacement for web.form.Dropdown
# https://github.com/webpy/webpy/blob/master/web/form.py
# web.py is in the public domain; it can be used for whatever purpose with absolutely no restrictions.


from web.form import Input
from web.form import AttributeList
import web.net as net
import web.utils as utils

class Number(Input):
	
	"""Number input.

	>>> Number(name='foo', value='bar').render()
	u'<input id="foo" name="foo" type="number" value="bar"/>'
	>>> Textbox(name='foo', value=0).render()
	u'<input id="foo" name="foo" type="number" value="0"/>'
	"""        
	def get_type(self):
		return 'number'	


