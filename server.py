#!/usr/bin/env python3
from http import server
import shutil
import os
import json
import database as db
from authentication import check_user

class MatoHTTPRequestHandler(server.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.startswith('/api'):
			self.path=self.path[4:]
			if self.path.endswith('/balance'):
				self.balance()
			elif self.path.endswith('/items'):
				self.items()
			elif self.path.endswith('/details'):
				self.details()
			else:
				self.not_found()
		else:
			if self.path=='/':
				self.path='/index.html'
			if self.path.find('..')!=-1:
				return self.forbidden()
			self.servefile()

	def do_POST(self):
		if self.path.startswith('/api'):
			self.path=self.path[4:]
		else:
			return self.not_found()
		if self.path.endswith('/pay'):
			self.pay()
		elif self.path.endswith('/buy'):
			self.buy()
		elif self.path.endswith('/undo'):
			self.undo()
		else:
			self.not_found()

	def see_other(self):
		self.send_response(303)
		self.end_headers()

	def conflict(self):
		self.send_response(409)
		self.end_headers()

	def created(self):
		self.send_response(201)
		self.end_headers()

	def forbidden(self):
		self.send_response(403)
		self.end_headers()

	def not_found(self):
		self.send_response(404)
		self.end_headers()

	def bad_request(self):
		self.send_response(400)
		self.end_headers()

	def auth(self):
		username=self.path.split('/')[1]
		password=self.headers.get('pass',None)
		return check_user(username,password)


	def servefile(self):
		filename=os.path.join(os.getcwd(),'client','html',self.path[1:])
		print(filename)
		try:
			with open(filename,'rb') as f:
				size=f.seek(0,2)
				f.seek(0,0)
				self.send_response(200)
				self.send_header("Content-Length", size)
				self.end_headers()
				shutil.copyfileobj(f,self.wfile)#.write(bytes(f.read(),'ASCII'))
		except FileNotFoundError:
			return self.not_found();

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
		money_out=s.query(db.Sale).filter(db.Sale.user==user).all()
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

	def undo(self):
		if not self.auth(): return self.forbidden()
		username=self.path.split('/')[1]
		s=db.Session()
		user=s.query(db.User).filter(db.User.name==username).one()
		last_in=s.query(db.Pay).filter(db.Pay.user==user).order_by(db.Pay.time.desc()).first()
		last_out=s.query(db.Sale).filter(db.Sale.user==user).order_by(db.Sale.time.desc()).first()
		if last_in is None:
			if last_out is None:
				return self.conflict()
			else:
				s.delete(last_out)
		else:
			if last_out is None:
				s.delete(last_in)
			else:
				s.delete(last_in if last_in.time>last_out.time else last_out)
		s.commit()
		return self.created();


	def pay(self):
		if not self.auth(): return self.forbidden()
		length=self.headers.get('Content-Length',None)
		if length is None:
			return self.bad_request()
		try:
			d=(self.rfile.read(int(length)).decode('ASCII'))
			data=json.loads(d)
		except ValueError as ex:
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
		return self.created()

	def buy(self):
		if not self.auth(): return self.forbidden()
		length=self.headers.get('Content-Length',None)
		if length is None:
			return self.bad_request()
		try:
			d=(self.rfile.read(int(length)).decode('ASCII'))
			data=json.loads(d)
		except ValueError as ex:
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
		return self.created()

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
