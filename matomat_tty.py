import os
import config
from matomat import matomat_factory
import banner
from getpass import getpass
from time import sleep
import cmd


class MainCmd(cmd.Cmd):
	prompt = "matomat> "
	ruler = ""
	doc_header = "List of supported commands:"
	misc_header = ""
	undoc_header = ""
	intro = ""

	def _credits(self):
		return str(matomat.balance()) + " credits"

	def do_quit(self, value):
		return True

	do_EOF = do_quit

	def help_quit(self):
		print("Quit the matomat session")

	def do_loscher(self, value):
		l = LoscherCmd()
		l.cmdloop()

	def help_loscher(self):
		print("Admin interface (add users, change password, ...)")

	def do_pay(self, coins):
		try:
			matomat.pay(coins)
		except ValueError:
			print("Error: Could not pay amount \'" + coins + "\' coins")
			return

		print("New credit amount: " + self._credits())

	def do_credits(self, args):
		print("You have " + self._credits() + "\n")

	def help_credits(self):
		print("Your current credit count")

	def help_pay(self):
		print("Pay money into your matomat account")
		print("Usage: pay amount")

	def do_buy(self, args):
		split_args = args.split(" ")
		if len(split_args) != 2:
			print("Wrong number of arguments. See \'help buy\'")
			return

		amount = split_args[0]
		item = split_args[1]

		try:
			_amount = int(amount)
		except ValueError:
			print("Incorrect amount " + amount)
			return

		possible_items = [item['name'] for item in matomat.items()]
		if item.lower() not in [x.lower() for x in possible_items]:
			print("Unknown item \'" + item + '\'')
			print("Possible items: " + ", ".join(possible_items))
			return

		item_id = [i['id'] for i in matomat.items() if i['name'].lower() == item.lower()]
		for _ in range(_amount):
			matomat.buy(int(item_id[0]))

		print("New credit amount: " + self._credits())

	def help_buy(self):
		print("Buy a certain amount of a specific item")
		print("Example: buy 1 Mate")

	def help_EOF(self):
		print()

	def preloop(self):
		print_banner()
		print("Hi " + matomat.username() + " ... you have\n\n" + str(matomat.balance()) + " credits\n")
		print("The following items are available:\n")
		for item in matomat.items():
			print("** " + item['name'] + " (" + str(item['price']) + " credits)")
		self.do_help(None)

	def postloop(self):
		print_banner()


class LoscherCmd(cmd.Cmd):
	prompt = "matomat:Loscher> "

	def preloop(self):
		print_banner()

	def postloop(self):
		print_banner()

	def do_quit(self, value):
		return True

	def do_arsch(self):
		pass

	def do_end(self, args):
		return True

	def do_back(self, args):
		return True

	do_EOF = do_end

def print_logo():
	os.system('/usr/bin/clear')
	print(banner.logo)

def print_banner():
	os.system('/usr/bin/clear')
	print(banner.banner)

def login():
	user = input("Login: ")
	passwd = getpass("Password: ")

	if not matomat.auth(user, passwd):
		print("Login failed!")
		sleep(1)
		return False

	return True

if __name__ == '__main__':
	matomat = matomat_factory(config.dbengine).get()
	print_logo()
	if login():
		MainCmd().cmdloop()
