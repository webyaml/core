# path: lib/processors
# filename: image.py
# description: WSGI application image file processors

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
import os
import time
import shutil

from PIL import Image
from resizeimage import resizeimage

'''
install these packages for ubuntu 
libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk

then run 
pip install Pillow
pip install python-resize-image

'''


''' internal imports
'''
import classes.processor

''' classes
'''
class Resize(classes.processor.Processor):

	'''
	Description:
		
		Resize an image
	
	Usage:
	
		type: lib.processors.image.Resize
		path: 
		width:
		height:
		suffix:
	'''
	
	def run(self):
		
		print('lib.processrs.image.Resize')
		
		conf = self.conf
	
		# config checks
		if not conf.get('path'):
			print('no path given')
			
			return False

		if not conf.get('width'):
			print('no width given')
			
			return False

		if not conf.get('height'):
			print('no height given')
			
			return False

		if not conf.get('suffix'):
			print('no suffix given')
			
			return False
		
		# markup path
		
		#print(conf['path'])
		
		path = self.element.fnr(conf['path'])
		
		#print(path)
		
		fd_img = open(path, 'r')
		img = Image.open(fd_img)	
		img = resizeimage.resize_cover(img, [conf['width'],conf['height']] )
		
		filename = '%s%s.%s' %("".join(path.split('.')[:-1]),conf['suffix'],path.split('.')[-1])
		
		img.save(filename, img.format, quality=conf.get('quality',80))
		fd_img.close()
		
		
		# debug
		print('image filename')
		
		# handle the stdout
		if conf.get('result'):
			
			conf['result']['value'] = filename
			conf['result']['format'] = 'string'
			
			# load data
			if not self.load_data(conf['result']):
				
				print('failed to save - data failed to load')
					
				return False
		
		return True	
