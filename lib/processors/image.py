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

''' external imports
'''
import os.path

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




class Resize2(classes.processor.Processor):

	def run(self):

		'''
		Description:
			
			Resize an image
		'''

		print('lib.processrs.image.Resize2')
		
		conf = self.conf
		
		# config checks
		
		#source
		if not conf.get('source'):
			print('no source given')
			return False

		if not conf['source'].get('path'):
			print('no source path given')
			return False
		
		src_path = self.element.fnr(conf['path'])
		
		if not os.path.isfile(src_path):
			print("source not found: '%s'" conf['source']['path'] %src_path)
			return False
		
		# break down path into components
		src_dir,  src_bn = os.path.split(src_path)
		src_bn_no_ext, src_ext = os.path.splitext(src_basename)
		
		# store
		self.load_data({'format': 'python', 'store': 'src_path', 'value': src_path})
		self.load_data({'format': 'python', 'store': 'src_dir', 'value': src_dir})
		self.load_data({'format': 'python', 'store': 'src_bn', 'value': src_bn})
		self.load_data({'format': 'python', 'store': 'src_bn_no_ext', 'value': src_bn_no_ext})
		self.load_data({'format': 'python', 'store': 'src_ext', 'value': src_ext.lower()})	
		
		#destination
		if not conf.get('destination'):
			print('no destination given')	
			return False

		# open the source image file
		f = open(path, 'r')
		src_img = Image.open(f)		
		
		# force destination into a list
		if isinstance(conf['destination'], dict):
			conf['destination'] = [conf['destination']]

		'''
		* `resize_crop` crop the image with a centered rectangle of the specified size.
		* `resize_cover` resize the image the fill the specified area, crop as needed (same behavior as `background-size: cover`).
		* `resize_contain` resize the image to can fit in the specified area, keeping the ratio and without crop (same behavior as `background-size: contain`). 
		* `resize_height` resize the image to the specified height ajusting width to keep the ratio the same.
		* `resize_width` resize the image to the specified width ajusting height to keep the ratio the same.
		* `resize_thumbnail` resize image while keeping the ratio trying its best to match the specified size.			
		'''
		
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
			dst_path = self.element.fnr(destination['path'])
			
			# Store path
			if destination.get('store'):
				self.load_data({'format': 'python', 'store': destination['store'], 'value': src_path})

			# resize and save image
			dst_img = methods[method](src_img, size)
			dst_img.save(dst_path, dst_img.format, quality=conf.get('quality',80))
			
		
		# close the source image file
		src_img.close()












