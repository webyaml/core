# path: lib/processors
# filename: wifi.py
# description: WSGI application file processors
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

''' internal imports
'''
import classes.processor

''' classes
'''
class Write(classes.processor.Processor):

	'''
	Description:
		
		Read the config and write the marked up value to the path
	
	Usage:
	
		type: lib.processors.file.Write
		value: |
			file content
			...
		path: '/some/path/'
		
	'''
	
	def run(self):
		
		print('lib.processrs.file.Write')
	
		# config checks
		value = self.conf.get('value')
		if not value:
			print('no value given')
			
			return False
		
		path = self.conf.get('path')
		if not path:
			print('no path given')
			
			return False
			
		
		# markup file
		if isinstance(value,str) and 'nomarkup' not in self.conf:
		
			if 'singlemarkup' in self.conf:
		
				value = self.content.fnr(value,1,binary=True)
			else:
				
				value = self.content.fnr(value,binary=True)
		
		# markup path
		path = self.content.fnr(path)
		
		# backup file if it already exists
		if os.path.isfile(path) and 'nobackup' not in self.conf:
			shutil.move(path,path+"."+str(int(time.time()))+".bak")
		
		# create directories if they do not exist
		directory = "/".join(path.split('/')[:-1])
		
		if directory:
		
			if not os.path.isdir(directory):
				os.makedirs(directory, 0775)
		else:
			path = "./%s"%path
		
		# write
		file_obj = open(path, "w+")
		file_obj.write(value.strip()) #.encode('utf-8')
		file_obj.close()
				
		return True


class Read(classes.processor.Processor):
	
	def run(self):
		
		# debug
		print("lib.processrs.file.Read")
		
		# vars
		conf = self.conf
		
		if not conf.get('path'):
			
			print('path not in conf')
			return False
		
		# markup filename	
		conf["path"] = self.content.fnr(conf["path"])
		'''
		if conf["path"].startswith("./"):
			
			print("found ./")
			
			conf["path"] = conf["path"].replace("./","")
		'''
		# debug
		#print(conf["path"])
		
		if not os.path.isfile(conf["path"]):
			
			# debug
			print("file not found '%s'." %conf["path"])
			
			return False
			
		# debug
		print("found file '%s'." %conf["path"])


		if conf.get('backup'):
		
			# keep a copy of opened file with timestamp.
			shutil.copy(conf["path"],conf["path"]+"."+str(int(time.time()))+".bak")
			
		f = open(conf["path"], 'r')
		contents = f.read()
		f.close()
		
		# debug
		#print(contents)
		
		# handle the returned data
		if conf.get('data'):
			
			conf['data']['value'] = contents
			
			# load data
			if not self.content.load_data(conf['data']):
				
				print('failed to save - data failed to load')
					
				return False

		return True


class Delete(classes.processor.Processor):
	
	def run(self):
		
		# debug
		print("lib.processrs.file.Delete")
		
		# vars
		conf = self.conf
		
		if not conf.get('path'):
			
			print('path not in conf')
			return False
		
		# markup filename	
		conf["path"] = self.content.fnr(conf["path"])
		'''
		if conf["path"].startswith("./"):
			
			print("found ./")
			
			conf["path"] = conf["path"].replace("./","")
		'''
		# debug
		#print(conf["path"])
		
		if not os.path.isfile(conf["path"]):
			
			# debug
			print("file not found '%s'." %conf["path"])
			
			return False
			
		# debug
		print("found file '%s'." %conf["path"])
		
		# backup file if it already exists
		if 'nobackup' not in self.conf:
			shutil.move(conf["path"],conf["path"]+"."+str(int(time.time()))+".bak")		
		
		os.remove(conf["path"])
		
		return True
		

class List(classes.processor.Processor):
	
	def run(self):
		
		# debug
		print("lib.processrs.file.List")
		
		# vars
		conf = self.conf
		
		if not conf.get('path'):
			
			print('path not in conf')
			return False
		
		# markup filename	
		conf["path"] = self.content.fnr(conf["path"])
		
		# debug
		#print(conf["path"])
		
		#basename = os.path.basename(conf["path"])
		#relpath = os.path.dirname(conf["path"])		

		#debug
		#print(relpath, basename)
		
		#if relpath == "":			
		#	relpath = "."

		#debug
		#print(relpath, basename)
		
		
		if not os.path.isdir(conf["path"]):
			
			# debug
			print("path '%s' is not a directory." %conf["path"])
				
			return False
			
			
		# debug
		print("found dir '%s'." %conf["path"])
		
		ls = os.listdir(conf["path"])
		ls.sort()
		
		dirs = []
		files = []
		output = []
		
		for item in ls:
			
			tmp_item = {}
			tmp_item['name'] = item

			if os.path.islink('%s/%s'%(conf["path"],item)):
				
				tmp_item['link'] = True
			else:
				tmp_item['link'] = False
			
			
			if os.path.isdir('%s/%s'%(conf["path"],item)):
				
				tmp_item['type'] = 'dir'
				dirs.append(tmp_item)
				continue
				
				
			if os.path.isfile('%s/%s'%(conf["path"],item)):
				
				tmp_item['type'] = 'file'
				files.append(tmp_item)
				
		output.extend(dirs)
		output.extend(files)	
		
		
		# debug
		#print(contents)
		
		# handle the returned data
		if conf.get('result'):
			
			conf['result']['value'] = output
			conf['result']['format'] = 'raw'
			
			# load data
			if not self.content.load_data(conf['result']):
				
				print('data failed to save')
					
				return False

		return True


class Mkdir(classes.processor.Processor):

	'''
	Description:
		
		Create a new directory
	
	Usage:
	
		type: lib.processors.file.Mkdir
		path: '/some/path/'
		
	'''
	
	def run(self):
		
		print('lib.processrs.file.Mkdir')
	
		# config checks
		
		path = self.conf.get('path')
		if not path:
			print('no path given')
			
			return False
		
		# markup path
		path = self.content.fnr(path)
		
		print(path)
		
		# create directories if they do not exist
		directory = "/".join(path.split('/'))
		
		if directory:
		
			if not os.path.isdir(directory):
				os.makedirs(directory, 0775)
				
		return True