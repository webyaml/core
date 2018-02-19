# make python2 strings and dictionaries behave like python3
from __future__ import unicode_literals

try:
	from builtins import dict, str
except ImportError:
	from __builtin__ import dict, str

# This is a replacement for web.form.Dropdown
# https://github.com/webpy/webpy/blob/master/web/form.py
# web.py is in the public domain; it can be used for whatever purpose with absolutely no restrictions.


from web.form import Input
from web.form import AttributeList
import web.net as net
import web.utils as utils

class Dropdown(Input):
	r"""Dropdown/select input.
	
		>>> Dropdown(name='foo', args=['a', 'b', 'c'], value='b').render()
		u'<select id="foo" name="foo">\n  <option value="a">a</option>\n  <option selected="selected" value="b">b</option>\n  <option value="c">c</option>\n</select>\n'
		>>> Dropdown(name='foo', args=[('a', 'aa'), ('b', 'bb'), ('c', 'cc')], value='b').render()
		u'<select id="foo" name="foo">\n  <option value="a">aa</option>\n  <option selected="selected" value="b">bb</option>\n  <option value="c">cc</option>\n</select>\n'
	"""
	def __init__(self, name, args, *validators, **attrs):
		
		#print("Dropdown")
		
		self.args = args
		super(Dropdown, self).__init__(name, *validators, **attrs)

	def render(self):
		attrs = self.attrs.copy()
		attrs['name'] = self.name
		
		x = '<select %s>\n' % attrs
		
		for arg in self.args:
			x += self._render_option(arg)

		x += '</select>\n'
		return x

	def _render_option(self, arg, indent='  '):
		
		#print("self.value: "+str(self.value))
		
		if isinstance(arg, (tuple, list)):
			
			if len(arg) == 2:
				value, desc, attrs = arg[0], arg[1], None
				
			if len(arg) == 3:
				value, desc, attrs = arg
		else:
			value, desc, attrs = arg, arg, None
			
		# join attrs
		if attrs:
			attrs = AttributeList(attrs)
			
		else:
			attrs = ''
		
		value = utils.safestr(value)
		if isinstance(self.value, (tuple, list)):
			s_value = [utils.safestr(x) for x in self.value]
		else:
			s_value = utils.safestr(self.value)
		
		if s_value == value or (isinstance(s_value, list) and value in s_value):
			select_p = ' selected="selected"'
		else:
			select_p = ''
		
		return indent + '<option%s value="%s" %s>%s</option>\n' % (select_p, net.websafe(value), attrs, net.websafe(desc))
		
