import email
#import dateutil.parser

def sanitize_header(text, default_charset):
	header, encoding = email.Header.decode_header(text)[0]
	if encoding:
		return header.decode(encoding)
	else:
		return header.decode(default_charset)

def parse_message(text):
	message = email.message_from_string(text)

	message_charset = 'iso-8859-1' # acts as a fallback FIXME
	for charset in message.get_charsets():
		message_charset = message_charset or charset

	d = { }
	d['from'] = sanitize_header(message['from'], message_charset)
	if 'to' in message:
		d['to'] = sanitize_header(message['to'], message_charset)
	if 'cc' in message:
		d['cc'] = sanitize_header(message['cc'], message_charset)
	if 'bcc' in message:
		d['bcc'] = sanitize_header(message['bcc'], message_charset)
	d['subject'] = sanitize_header(message['subject'], message_charset)
	try:
		d['date'] = dateutil.parser.parse(message['date'])
	except:
		d['date'] = message['date']

	d['parts'] = []
	for part in message.walk():
		if part.get_content_type().startswith('multipart'):
			continue
		p = {
			'content_type' : part.get_content_type(),
		}
		if part.get_content_type().startswith('text'):
			p['charset'] = part.get_content_charset() or message_charset
			p['payload'] = part.get_payload(decode=True).decode(p['charset'], 'ignore')
		else:
			p['payload'] = part.get_payload().replace('\n','')
		if part.get_filename():
			p['filename'] = part.get_filename()
		d['parts'].append(p)
	return d
