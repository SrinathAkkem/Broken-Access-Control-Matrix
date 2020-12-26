import sys
import sqlite3
import string
import os

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

def query():
	return "2%"


def main(argv):
	user_id = sys.argv[1]
	conn = sqlite3.connect(DEFAULT_PATH)
	cursor = conn.cursor()
	response = cursor.execute("SELECT iban FROM pages_account WHERE owner_id='%s' and balance LIKE '%%%s%%'" % (user_id, query())).fetchall()
	print('Found entries:')
	for r in response:
		print(r[0])

if __name__ == "__main__": 
	if len(sys.argv) != 3:
		print('usage: python %s username database' % sys.argv[0])
	else:
		main(sys.argv)