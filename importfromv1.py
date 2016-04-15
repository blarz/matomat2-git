#!/usr/bin/python3

import sys
import sqlite3

import authentication
import config
import database

DEFAULT_PASSWORD = "foobar"

if len(sys.argv) != 2:
	print("Usage: " + sys.argv[0] + " old_database.db")
	sys.exit(0)

matomat2_session = database.create_sessionmaker(config.dbengine)()
old_connect = sqlite3.connect(sys.argv[1])

# import drinks
for item in old_connect.execute("select name, price from drinks"):
	print("Adding item " + item[0])
	matomat2_session.add(database.Item(name=item[0], price=item[1]))

# import users
for user in old_connect.execute("select username, credits from user"):
	name = user[0]
	credits = user[1]

	print("Adding user " + name + " with default password \"" + DEFAULT_PASSWORD + "\" and " + str(credits) + " credits")
	success = authentication.create_user(matomat2_session, name, DEFAULT_PASSWORD, None)
	if not success:
		print("!! User creation failed for " + name)
		continue

	try:
		db_user = authentication.get_user(matomat2_session, name)
		payment = database.Pay(user=db_user, amount=credits)
		matomat2_session.add(payment)
	except ValueError:
		print("!! Could not set initial credits for user " + user)

matomat2_session.commit()
