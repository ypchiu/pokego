import base64
import time
import re
import random
from datetime import datetime
import threading
import argparse
import os
import platform
import sys

import config
import login
import public
from getpass import getpass
import public_proto_pb2
try:
	import pokemon_pb2
	import logic
	import dirty
	import api
	config.pub=False
except:
	config.pub=True

def get_acces_token(usr,pws,type):
	access_token=None
	ltype=None
	if 'goo' in type:
		print '[!] Using google as login..'
		google_data=None
		if platform.system() == 'Windows':
			google_data= login.login_google(usr,pws)
			if google_data is not None:
				access_token=google_data['id_token']
		else:
			access_token= login.login_google_v2(usr,pws)
		if access_token is not None:
			ltype='google'
	else:
		print '[!] I am a poketrainer..'
		access_token= login.login_pokemon(usr,pws)
		ltype='ptc'
	return access_token,ltype
	
def main():
	if platform.system() == 'Windows':
		os.system("title Pokemon GO API Python")
		os.system("cls")
	else:
		# Catches "Lunux" and "Darwin" (OSX), among others
		os.system("clear")
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--username", help="Login", default=None)
	parser.add_argument("-p", "--password", help="Password", default=None)
	parser.add_argument("-t", "--type", help="Google/PTC", required=True)
	parser.add_argument("-l", "--location", help="Location", required=True)
	#parser.add_argument("-d", "--distance", help="Distance", required=True)
	args = parser.parse_args()
	if not args.username:
		args.username = getpass("Username: ")
	if not args.password:
		args.password = getpass("Password: ")
	if 'ptc' in args.type.lower() or 'goo' in args.type.lower():
		#config.distance=args.distance
		access_token,ltype=get_acces_token(args.username,args.password,args.type.lower())
		if access_token is not None:
			if config.debug:
				print '[!] using:',config.pub
			if config.pub:
				public.start_work(access_token,ltype,args.location)
			else:
				dirty.start_private_show(access_token,ltype,args.location)
		else:
			print '[-] access_token bad'
	else:
		print '[!] used type "%s" only Google or PTC valid'%(args.type.lower())
	
if __name__ == '__main__':
	sys.dont_write_bytecode = True
	main()