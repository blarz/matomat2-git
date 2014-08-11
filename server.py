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
		elif self.path.endswith('/items'):
			self.items()
		elif self.path.endswith('/details'):
			self.details()
		else:
			self.not_found()

	def do_POST(self):
		if self.path.endswith('/pay'):
			self.pay()
		if self.path.endswith('/buy'):
			self.buy()
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
		username=self.path.split('/')[1]
		s=db.Session()
		user=s.query(db.User).filter(db.User.name==username).one()
		money_in=sum((x.amount for x in s.query(db.Pay).filter(db.Pay.user==user)))
		money_out=sum((x.amount for x in s.query(db.Sale).filter(db.Pay.user==user)))
		data=money_in-money_out
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(bytes(json.dumps(data),'UTF-8'))

	def details(self):
		if not self.auth(): return self.forbidden()
		username=self.path.split('/')[1]
		s=db.Session()
		user=s.query(db.User).filter(db.User.name==username).one()
		money_in=s.query(db.Pay).filter(db.Pay.user==user).all()
		money_out=s.query(db.Sale).filter(db.Pay.user==user).all()
		money=sorted(money_in+money_out,key=lambda x:x.time)
		data=[]
		for m in money:
			d={"amount":m.amount,"time":m.time.isoformat()}
			if isinstance(m,db.Sale):
				d["amount"]*=-1
				d["Item"]=m.item.name
			data.append(d)
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(bytes(json.dumps(data),'UTF-8'))

	def pay(self):
		if not self.auth(): return self.forbidden()
		try:
			d=(self.rfile.read().decode('ASCII'))
			data=json.loads(d)
		except ValueError as ex:
			print(ex)
			return self.bad_request()
		try:
			amount=int(data)
		except KeyError:
			return self.bad_request()
		username=self.path.split('/')[1]
		s=db.Session()
		user=s.query(db.User).filter(db.User.name==username).one()
		p=db.Pay(user=user,amount=amount)
		s.add(p)
		s.commit()
		return self.see_other()

	def buy(self):
		if not self.auth(): return self.forbidden()
		try:
			d=(self.rfile.read().decode('ASCII'))
			data=json.loads(d)
		except ValueError as ex:
			print(ex)
			return self.bad_request()
		try:
			item_id=int(data)
		except KeyError:
			return self.bad_request()
		username=self.path.split('/')[1]
		s=db.Session()
		user=s.query(db.User).filter(db.User.name==username).one()
		item=s.query(db.Item).filter(db.Item.id==item_id).one()
		sale=db.Sale(user=user,item=item,amount=item.price)
		s.add(sale)
		s.commit()
		return self.see_other()

	def items(self):
		s=db.Session()
		items_q=s.query(db.Item)
		items=[{"id":x.id,"name":x.name,"price":x.price} for x in items_q]
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(bytes(json.dumps(items),'UTF-8'))


if __name__=='__main__':
	s=server.HTTPServer(('',8000),MatoHTTPRequestHandler)
	s.serve_forever()
