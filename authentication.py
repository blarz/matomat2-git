from database import User, Session

def check_user(username,password):
	s=Session()
	user=s.query(User).filter(User.name==username).all()
	if len(user)!=1:
		return False
	if user[0].password==password:
		return True
	return False
