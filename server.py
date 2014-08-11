from http import server
import json
import database as db
from authentication import check_user

class MatoHTTPRequestHandler(server.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path=='/':
			self.index()
		elif self.path.endswith('/balance'):
			self.balance()
		else:
			self.not_found()

	def do_POST(self):
		if self.path.endswith('/pay'):
			self.pay()
		else:
			self.not_found()

	def see_other(self):
		print('see_other')
		self.send_response(303)
		self.end_headers()

	def forbidden(self):
		print('forbidden')
		self.send_response(403)
		self.end_headers()

	def not_found(self):
		print('notfound')
		self.send_response(404)
		self.end_headers()

	def bad_request(self):
		print('bad request')
		self.send_response(400)
		self.end_headers()

	def auth(self):
		username=self.path.split('/')[1]
		password=self.headers.get('pass',None)
		return check_user(username,password)


	def index(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes("test\n",'UTF-8'))

	def balance(self):
		if not self.auth(): return self.forbidden()
		index()

	def pay(self):
		if not self.auth(): return self.forbidden()
		try:
			d=(self.rfile.read().decode('ASCII'))
			print(repr(d))
			data=json.loads(d)
		except ValueError as ex:
			print(ex)
			return self.bad_request()
		try:
			amount=data['amount']
		except KeyError:
			return self.bad_request()
		username=self.path.split('/')[1]
		s=db.Session()
		user=s.query(db.User).filter(db.User.name==username).one()
		p=db.Pay(user=user,amount=amount)
		s.add(p)
		s.commit()
		return self.see_other()

if __name__=='__main__':
	s=server.HTTPServer(('',8000),MatoHTTPRequestHandler)
	s.serve_forever()
