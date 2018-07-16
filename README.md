# WebYAML
WebYAML is a Rapid Application Development (RAD) tool that allows designers and developers to rapidly build attractive web applications and RESTful APIs for their projects. Applications are authored as simple configuration files in YAML syntax

## Requirements
- Python
- Webpy
- PyYAML
- xmltodict
- requests (for REST client support)
- oursql (for MySQL support)
- pymongo (for MongoDB support)
- sqlite3 (for SQLite support)

## Getting Started : First Application

Pre built example sites can be found in the webyaml/sites repo.  The easiest way to create a new site is download the repo into your WebYAML folder.

	$ cd /path-to/WebYAML/
	$ git clone https://github.com/webyaml/sites.git
	
This will create a new folder called sites in your WebYAML directory.  Start building your application by copying the sites/blank directory to make a new directory for your application. This example creates a new folder for the application 'hello'.

	$ cd /path-to/WebYAML/sites/
	$ cp -rfp blank hello
	
An application requires a minimum of two configuration files, conf/urls.cfg and at least one content configuration. These configuration files, and all other files used by your application should be stored in the application directory.

### conf/urls.cfg

The URL configuration is stored in the file conf/urls.cfg. This file defines the available URLs/views for an application.

Using a text editor, create the file conf/urls.cfg with the following content:

	# filename: conf/urls.cfg

	# Example Format
	#-
	#	/url/path/:
	#		conf: conf/path/filename.cfg

	-
		/:
			conf: conf/hello.cfg
			
			
	# Include Documetnation (/docs)
	include conf/docs/urls.cfg

			
(Note: YAML syntax uses spaces for indentation. However, you may use tabs if you prefer. Tabs will be converted to spaces when the configurations are loaded.)

### Content Configuration

In the URL configuration file above we declared that the content configuration file conf/hello.cfg should be used to produce views for the URL "/". Create a new text document containing the following content block:


	# filename: conf/hello.cfg
	# hello world content

	value: Hello World!
	
### Testing the Application

Start the application 'hello' with the following commands:

	$ cd /path-to/WebYAML/sites/hello/
	$ ./app.py
	
Visit your site at http://localhost:8080

See the docs at http://localhost:8080/docs
