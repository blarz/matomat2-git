#!/usr/bin/env python3
from http import server
import shutil
import os
import json
import database as db
from authentication import check_user, create_user, get_user
import config
from matomat import NotAutheticatedError, matomat_factory

try:
	fnfError=FileNotFoundError
except NameError:
	fnfError=IOError

class MatoHTTPRequestHandler(server.BaseHTTPRequestHandler):
	def __init__(self,*args):
		self.matomat=args[2].matomat.get()
		super().__init__(*args)

	def init(self):
		parts=self.path.split('/')
		if parts[1]!='api':
			return None
		if len(parts)>3:
			password=self.headers.get('pass',None)
			self.matomat.auth(parts[2],password)
		return parts[-1]

	def do_GET(self):
		cmd=self.init()
		if cmd is None:
			if self.path=='/':
				self.path='/index.html'
			if self.path.find('..')!=-1:
				return self.forbidden()
			return self.servefile()

		try:
			if cmd=='balance':return self.balance()
			elif cmd=='items':return self.items()
			elif cmd=='details':return self.details()
			elif cmd=='user':return self.user_get()
			return self.not_found()
		except NotAutheticatedError:
			return self.forbidden()

	def do_POST(self):
		cmd=self.init()
		if cmd is None:
			return self.not_found()

		try:
			if cmd=='pay': return self.pay()
			elif cmd=='buy': return self.buy()
			elif cmd=='undo': return self.undo()
			elif cmd=='user': return self.user()
			elif cmd=='transfer': return self.transfer()
			return self.not_found()
		except NotAutheticatedError:
			return self.forbidden()

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

	def json_response(self,data):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(bytes(json.dumps(data),'UTF-8'))

	def servefile(self):
		filename=os.path.join(os.getcwd(),'client','html',self.path[1:])
		try:
			with open(filename,'rb') as f:
				size=f.seek(0,2)
				f.seek(0,0)
				self.send_response(200)
				self.send_header("Content-Length", size)
				self.end_headers()
				shutil.copyfileobj(f,self.wfile)#.write(bytes(f.read(),'ASCII'))
		except fnfError:
			return self.not_found();

	def balance(self):
		self.json_response(self.matomat.balance())

	def details(self):
		self.json_response(self.matomat.details())

	def undo(self):
		try:
			self.matomat.undo()
		except ValueError:
			return self.conflict()
		self.created()

	def load_json(self):
		length=self.headers.get('Content-Length',None)
		if length is None:
			return None
		try:
			d=(self.rfile.read(int(length)).decode('ASCII'))
			data=json.loads(d)
		except ValueError as ex:
			return None
		return data

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

	def user_get(self):
		self.json_response({'username':self.matomat.username()})

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


	def items(self):
		items=self.matomat.items()
		self.json_response(items)

if __name__=='__main__':
	s=server.HTTPServer(('',8000),MatoHTTPRequestHandler)
	s.matomat=matomat_factory(config.dbengine)
	s.serve_forever()
