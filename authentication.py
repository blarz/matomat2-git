import random
import hashlib
from database import User, Session

def hashpw(salt,password):
	h=hashlib.sha1()
	h.update(salt)
	h.update(password)
	return h.hexdigest()

def check_user(username,password):
	if password is None:
		return False
	s=Session()
	user=s.query(User).filter(User.name==username).all()
	if len(user)!=1:
		return False
	salt_hashed=user[0].password.split('$',1)
	if len(salt_hashed)!=2:
		return False
	salt,hashed=salt_hashed
	if hashed==hashpw(salt.encode('ASCII'),password.encode('UTF-8')):
		return True
	return False

def genpw(password):
	saltbase=(
		[bytes([x]) for x in range(ord('A'),ord('Z')+1)]+
		[bytes([x]) for x in range(ord('a'),ord('z')+1)]+
		[bytes([x]) for x in range(ord('0'),ord('9')+1)]
		)
	salt=b''.join(random.sample(saltbase,10))
	return ''.join([salt.decode('ASCII'),'$',hashpw(salt,password.encode('UTF-8'))])

def create_user(username,password,creator):
	s=Session()
	user=s.query(User).filter(User.name==username).all()
	if len(user)==0:
		u=User(name=username,password=genpw(password),creator=creator)
		s.add(u)
		s.commit()
		return True
	if len(user)==1:
		u=user[0]
		if u.id==creator:
			u.password=genpw(password)
			s.merge(u)
			s.commit()
			return True
	return False

