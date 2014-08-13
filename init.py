#!/usr/bin/env python3
import database as db
import authentication as a

a.create_user('admin','admin',None)

s=db.Session()
s.add(db.Item(name='Mate',price='100'))
s.add(db.Item(name='Bier',price='150'))
s.commit()
