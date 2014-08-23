from authentication import check_user, create_user, get_user
import database as db

class NotAutheticatedError(Exception):
	pass

class matomat_factory(object):
	def __init__(self,engine):
		self.Session=db.create_sessionmaker(engine)

	def get(self):
		return matomat(self.Session())

def require_auth(fun):
	def inner(self,*args,**kwargs):
		if not self.is_auth():
			raise NotAutheticatedError('Not authenticated')
		return fun(self,*args,**kwargs)
	return inner


class matomat(object):
	def __init__(self, dbsession):
		self._user=None
		self.session=dbsession

	def is_auth(self):
		return not self._user is None

	def auth(self,user,password):
		user=check_user(self.session,user,password)
		if user is None:
			return False
		self._user=user
		return True

	@require_auth
	def balance(self):
		money_in=sum((x.amount for x in self.session.query(db.Pay).filter(db.Pay.user==self._user)))
		money_out=sum((x.amount for x in self.session.query(db.Sale).filter(db.Sale.user==self._user)))
		res=money_in-money_out
		return res

	@require_auth
	def details(self):
		money_in=self.session.query(db.Pay).filter(db.Pay.user==self._user).all()
		money_out=self.session.query(db.Sale).filter(db.Sale.user==self._user).all()
		money=sorted(money_in+money_out,key=lambda x:x.time)
		data=[]
		for m in money:
			d={"amount":m.amount,"time":m.time.isoformat()}
			if isinstance(m,db.Sale):
				d["amount"]*=-1
				d["Item"]=m.item.name
			data.append(d)
		return data

	@require_auth
	def username(self):
		return self._user.name

	@require_auth
	def create_user(self,username,password):
		if not create_user(self.session,username,password,self._user.id):
			raise ValueError("Cannot change different user's password")

	@require_auth
	def pay(self,amount):
		p=db.Pay(user=self._user,amount=int(amount))
		self.session.add(p)
		self.session.commit()
	
	@require_auth
	def buy(self,item):
		if isinstance(item,int):
			item=self.lookup_item(item)
		sale=db.Sale(user=self._user,item=item,amount=item.price)
		self.session.add(sale)
		self.session.commit()

	@require_auth
	def undo(self):
		last_in=self.session.query(db.Pay).filter(db.Pay.user==self._user).order_by(db.Pay.time.desc()).first()
		last_out=self.session.query(db.Sale).filter(db.Sale.user==self._user).order_by(db.Sale.time.desc()).first()
		if last_in is None:
			if last_out is None:
				raise ValueError('Nothing to undo')
			else:
				self.session.delete(last_out)
		else:
			if last_out is None:
				self.session.delete(last_in)
			else:
				self.session.delete(last_in if last_in.time>last_out.time else last_out)
		self.session.commit()

	def lookup_item(self,item_id):
		item=self.session.query(db.Item).filter(db.Item.id==item_id).one()
		return item

	def items(self):
		items_q=self.session.query(db.Item)
		items=[{"id":x.id,"name":x.name,"price":x.price} for x in items_q]
		return items

