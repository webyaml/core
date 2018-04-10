# path: lib/processors
# filename: image.py
# description: WSGI application image file processors
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

''' external imports
'''
import os.path

''' internal imports
'''
import classes.processor

''' classes
'''
class Resize(classes.processor.Processor):

	def run(self):

		'''
		Description: |
			
			Resize an image
			
			from the docs at https://pypi.python.org/pypi/python-resize-image/1.1.3
			
			* `resize_crop` crop the image with a centered rectangle of the specified size.
			* `resize_cover` resize the image the fill the specified area, crop as needed (same behavior as `background-size: cover`).
			* `resize_contain` resize the image to can fit in the specified area, keeping the ratio and without crop (same behavior as `background-size: contain`). 
			* `resize_height` resize the image to the specified height ajusting width to keep the ratio the same.
			* `resize_width` resize the image to the specified width ajusting height to keep the ratio the same.
			* `resize_thumbnail` resize image while keeping the ratio trying its best to match the specified size.			
		'''		

		print('lib.processrs.image.Resize')
		
		conf = self.conf
		
		# config checks
		
		#source
		if not conf.get('source'):
			print('no source given')
			return False

		if not conf['source'].get('path'):
			print('no source path given')
			return False
		
		src_path = self.content.fnr(conf['source']['path'])
		
		if not os.path.isfile(src_path):
			print("source not found: '%s'" %src_path)
			return False
		
		# break down path into components
		src_dir,  src_bn = os.path.split(src_path)
		src_bn_no_ext, src_ext = os.path.splitext(src_bn)
		
		# store
		self.content.load_data({'format': 'string', 'store': 'src_path', 'value': src_path})
		self.content.load_data({'format': 'string', 'store': 'src_dir', 'value': src_dir})
		self.content.load_data({'format': 'string', 'store': 'src_bn', 'value': src_bn})
		self.content.load_data({'format': 'string', 'store': 'src_bn_no_ext', 'value': src_bn_no_ext})
		self.content.load_data({'format': 'string', 'store': 'src_ext', 'value': src_ext.lower()})	

		# Store src_path as specific key
		if conf['source'].get('store'):
			self.content.load_data({'format': 'string', 'store': conf['source']['store'], 'value': src_path})
		
		# dryrun
		if conf.get('dryrun'):
			conf['destination'] = []
		
		#destination
		if not conf.get('destination'):
			print('no destination given')	
			return False

		# open the source image file
		f = open(src_path, 'r')
		src_img = Image.open(f)
		
		# store size
		self.content.load_data({'format': 'string', 'store': 'src_width', 'value': src_img.size[0]})
		self.content.load_data({'format': 'string', 'store': 'src_height', 'value': src_img.size[1]})
		
		# force destination into a list
		if isinstance(conf['destination'], dict):
			conf['destination'] = [conf['destination']]
		
		methods = {
			'crop': resizeimage.resize_crop,
			'cover': resizeimage.resize_cover,
			'contain': resizeimage.resize_contain,
			'height': resizeimage.resize_height,
			'width': resizeimage.resize_width,
			'thumbnail': resizeimage.resize_thumbnail,
		}

		# loop through destinations
		for destination in conf['destination']:
			
			# config checks
			method = destination.get('method', 'cover')
			
			if method not in methods:
				print("resize method '%s' not available.")
				return False
				
			size = None
			
			if method == "height":
				if not destination.get('height'):
					print("resize height requires hieght to be defined.")
					return False
				size = destination['height']
				
			if method == "width":
				if not destination.get('width'):
					print("resize width requires width to be defined.")
					return False
				size = destination['width']

			if not size:
				
				if not destination.get('height') and not destination.get('width'):
					print("resize requires a hieght and width to be defined.")
					return False
					
				size = [destination['width'], destination['height']]
			
			if not destination.get('path'):
				print("resize requires a path for each destination.")
				return False
			
			# Markup path
			dst_path = self.content.fnr(destination['path'])
			
			# Store path
			if destination.get('store'):
				self.content.load_data({'format': 'string', 'store': destination['store'], 'value': dst_path})

			# make sure destination directory exists
			if not os.path.isdir(os.path.dirname(dst_path)):
				os.makedirs(os.path.dirname(dst_path), 0775)	

			# resize and save image
			dst_img = methods[method](src_img, size)
			dst_img.save(dst_path, dst_img.format, quality=conf.get('quality',80))
			
		
		# close the source image file
		src_img.close()

		return True
