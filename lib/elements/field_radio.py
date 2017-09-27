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
			x += '''
				<div class="form-check">
				  <label class="form-check-label">
				    <input %s/>
				    %s
				  </label>
				</div>
			''' % (attrs, net.websafe(desc))			
			
			
		return x

