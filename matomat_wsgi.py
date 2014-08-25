import config
from matomat import NotAutheticatedError, matomat_factory
import json

class matomat_wsgi(object):
	def __init__(self,matomat):
		self.matomat=matomat

	def created(self):
		self.start_response('201 CREATED',[])
		return []

	def bad_request(self):
		self.start_response('400 BAD REQUEST',[])
		return []

	def forbidden(self):
		self.start_response('403 FORBIDDEN',[])
		return []

	def not_found(self):
		self.start_response('404 NOT FOUND',[])
		return []

	def conflict(self):
		self.start_response('409 CONFLICT',[])
		return []

	def json_response(self,data):
		self.start_response('200 OK',[("Content-type", "application/json")])
		return [json.dumps(data).encode('UTF-8')]

	def init(self):
		parts=self.path.split('/')
		if len(parts)>2:
			password=self.environ.get('HTTP_PASS',None)
			self.matomat.auth(parts[1],password)
		return parts[-1]

	def load_json(self):
		length=int(self.environ.get('CONTENT_LENGTH',0))
		if length==0:
			return None
		try:
			d=(self.environ['wsgi.input'].read(length).decode('ASCII'))
			data=json.loads(d)
		except ValueError as ex:
			return None
		return data

	def do_GET(self):
		try:
			if self.cmd=='balance':return self.balance()
			elif self.cmd=='items':return self.items()
			elif self.cmd=='details':return self.details()
			elif self.cmd=='user':return self.user_get()
			return self.not_found()
		except NotAutheticatedError:
			return self.forbidden()

	def do_POST(self):
		try:
			if self.cmd=='pay': return self.pay()
			elif self.cmd=='buy': return self.buy()
			elif self.cmd=='undo': return self.undo()
			elif self.cmd=='user': return self.user()
			elif self.cmd=='transfer': return self.transfer()
			return self.not_found()
		except NotAutheticatedError:
			return self.forbidden()

	def balance(self):
		return self.json_response(self.matomat.balance())

	def items(self):
		return self.json_response(self.matomat.items())

	def details(self):
		return self.json_response(self.matomat.details())

	def user_get(self):
		return self.json_response({'username':self.matomat.username()})

	def pay(self):
		data=self.load_json()
		try:
			amount=int(data)
		except ValueError:
			return self.bad_request()
		self.matomat.pay(amount)
		return self.created()

	def buy(self):
		data=self.load_json()
		try:
			item_id=int(data)
		except ValueError:
			return self.bad_request()
		self.matomat.buy(self.matomat.lookup_item(item_id))
		return self.created()

	def undo(self):
		try:
			self.matomat.undo()
		except ValueError:
			return self.conflict()
		return self.created()

	def user(self):
		data=self.load_json()
		try:
			username=data['username']
			password=data['password']
		except:
			return self.bad_request()
		try:
			self.matomat.create_user(username,password)
		except ValueError:
			return self.bad_request()
		return self.created()

	def transfer(self):
		data=self.load_json()
		try:
			amount=data['amount']
			recipient=data['recipient']
		except:
			return self.bad_request()
		try:
			self.matomat.transfer(amount,recipient)
		except ValueError:
			return self.bad_request()
		return self.created()

	def __call__(self,environ,start_response):
		self.environ=environ
		self.start_response=start_response
		self.method=environ['REQUEST_METHOD']
		self.path=environ['PATH_INFO']
		self.cmd=self.init()
		if self.method=='GET': return self.do_GET()
		if self.method=='POST': return self.do_POST()
		return self.bad_request()

def application(environ,start_response):
	app=matomat_wsgi(matomat_factory(config.dbengine).get())
	return app(environ,start_response)
