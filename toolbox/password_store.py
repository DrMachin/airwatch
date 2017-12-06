try:
	import keyring
except ImportError:
	print("\nKeyring is required, run: 'pip3 install keyring'\n")
	quit()

import getpass
from base64 import b64encode

class keychain:

	__SERVICE_NAME = ''

	def __init__(self, service):
		self.data = []
		self.__SERVICE_NAME = service

	def encode_auth(self, username, passwd):

		credentials = username + ':' + passwd
		return b64encode(credentials.encode('utf-8')).decode()
	
	def login(self, username = None, password = None, key=False):

	    if username is None:
	    	username = input('Username: ')

	    passwd = keyring.get_password(self.__SERVICE_NAME, username)

	    if passwd is None:
	    	if password is None:
	    		if not key:
	    			passwd = getpass.getpass()
	    		else:
	    			passwd = input('Enter API Key: ')
	    	else:
	    		passwd = password
	    	self.set_password(username, passwd, key)

	    return username

	def set_password(self, username = None, passwd = None, key = False):

	    if username is None:
	    	username = input('Username: ')

	    if not key:
	    	auth = self.encode_auth(username, passwd)
	    else:
	    	auth = passwd

	    keyring.set_password(self.__SERVICE_NAME, username, auth)

	def change_password(self, username, current_password = None, new_password = None):

		auth = keyring.get_password(self.__SERVICE_NAME, username)

		if auth is not None:
			for _ in range(3):
				if current_password is None:
					current_password = getpass.getpass('Current Password: ')
				inauth = self.encode_auth(username, current_password)
				if inauth == auth:
					if new_password is None:
						new_password = getpass.getpass('New Password: ')
					self.set_password(username, current_password)
					print('Password Changed.')
					break
				current_password = None

	def get_password(self, username, key=False):

		passwd = keyring.get_password(self.__SERVICE_NAME, username)
		if passwd is None:
			self.login(username=username, key=key)
			return keyring.get_password(self.__SERVICE_NAME, username)
		else:
			return passwd

