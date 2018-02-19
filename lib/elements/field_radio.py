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


class Radio(Input):
	def __init__(self, name, args, *validators, **attrs):
		self.args = args
		super(Radio, self).__init__(name, *validators, **attrs)

	def render(self):
		
		if 'wrap' not in self.attrs:
			self.attrs['wrap'] = '''
				<div class="form-check">
					<label class="form-check-label">
					|
					</label>
				</div>		
			'''
		
		wrap = self.attrs['wrap'].split("|",1)
		del self.attrs['wrap']
		
		x = ''
		for arg in self.args:
			if isinstance(arg, (tuple, list)):
				value, desc= arg
			else:
				value, desc = arg, arg
			attrs = self.attrs.copy()
			attrs['name'] = self.name
			attrs['type'] = 'radio'
			attrs['value'] = value
			if 'class' in attrs:
				attrs['class'] = "form-check-input %s" %attrs['class']
			if self.value == value:
				attrs['checked'] = 'checked'
			#x += '<input %s/> %s' % (attrs, net.websafe(desc))
			x += "%s<input %s/>%s%s"% (wrap[0], attrs, net.websafe(desc), wrap[1])
		
		
		return x

