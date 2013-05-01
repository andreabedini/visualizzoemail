from __future__ import with_statement

import jinja2
import os

from email_parsing import parse_message

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import webapp2
import cgi

from google.appengine.api import files, urlfetch

def save_to_blob(data, mime_type):
	file_name = files.blobstore.create(mime_type=part['content_type'])
	with files.open(file_name, 'w') as f:
		f.write(data)
	files.finalize(file_name)
	blob_key = files.blobstore.get_blob_key(file_name)

class MainPage(webapp2.RequestHandler):
	def view_email(self, url):
		result = urlfetch.fetch(url)
		if result.status_code == 200:
			d = parse_message(result.content)
			for part in d['parts']:
				if not part['content_type'].startswith('text'):
					print part
			d['url'] = url
			template = JINJA_ENVIRONMENT.get_template('index.html')
			self.response.write(template.render(d))

	def get(self):
		url = cgi.escape(self.request.get('url'))
		if url:
			self.view_email(url)
		else:
			template = JINJA_ENVIRONMENT.get_template('index.html')
			self.response.write(template.render())

app = webapp2.WSGIApplication(
	[ ('/', MainPage) ], debug=True)
