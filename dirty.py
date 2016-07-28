import random
import math
import logic
import api
import time
import pokemon_pb2
import location
import config
import main
from multiprocessing import Process

multi=False

argsStored = []
startTime = time.time()
accessToken=None
globalltype=None

def restartProcess():
	global argsStored
	if accessToken is not None and globalltype is not None:
		start_private_show(accessToken,globalltype,argsStored.location)
	else:
		access_token,ltype=main.get_acces_token(argsStored.username,argsStored.password,argsStored.type.lower())
		if access_token is not None:
			start_private_show(access_token,ltype,argsStored.location)
		else:
			print '[-] access_token bad'

def start_private_show(access_token,ltype,loc):
	location.set_location(loc)
	print '[+] Token:',access_token[:40]+'...'
	prot1=logic.gen_first_data(access_token,ltype)
	local_ses=api.get_rpc_server(access_token,prot1)
	new_rcp_point='https://%s/rpc'%(local_ses.rpc_server,)
	while(True):
		proto_all=logic.all_stops(local_ses)
		api.use_api(new_rcp_point,proto_all)
		#walk_circle(120)
		walk_random()
		time.sleep(2)
		work_stop(local_ses,new_rcp_point)
	
def walk_random():
	COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE=location.get_location_coords()
	COORDS_LATITUDE=location.l2f(COORDS_LATITUDE)
	COORDS_LONGITUDE=location.l2f(COORDS_LONGITUDE)
	COORDS_ALTITUDE=location.l2f(COORDS_ALTITUDE)
	random_Angle=random.random()*math.pi*2	
	COORDS_LATITUDE=COORDS_LATITUDE+(config.steps*math.sin(random_Angle))
	COORDS_LONGITUDE=COORDS_LONGITUDE+(config.steps*math.cos(random_Angle))
	print '[+] perform random walk %.7f %.7f'%(COORDS_LATITUDE,COORDS_LONGITUDE)
	location.set_location_coords(COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE)

#edge must be greater than 3
def walk_circle(edge):
	a=2*math.pi/edge
	i=1
	print '[+] circular walk'
	while (edge > 0):		
		COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE=location.get_location_coords()
		COORDS_LATITUDE=location.l2f(COORDS_LATITUDE)
		COORDS_LONGITUDE=location.l2f(COORDS_LONGITUDE)
		COORDS_ALTITUDE=location.l2f(COORDS_ALTITUDE)
		COORDS_LATITUDE=COORDS_LATITUDE+(config.steps*math.sin(a*i))
		COORDS_LONGITUDE=COORDS_LONGITUDE+(config.steps*math.cos(a*i))
		#print '[+] perform circular walk %.7f %.7f'%(COORDS_LATITUDE,COORDS_LONGITUDE)
		location.set_location_coords(COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE)
		edge=edge-1
		i=i+1
		time.sleep(2)
	print '[+] done circle'
	
def split_list(a_list):
	half = len(a_list)/2
	return a_list[:half], a_list[half:]
	
def work_half_list(part,ses,new_rcp_point):
	for t in part:
		if config.debug:
			print '[!] farming pokestop..'
		work_with_stops(t,ses,new_rcp_point)
	
def work_stop(local_ses,new_rcp_point):
	proto_all=logic.all_stops(local_ses)
	all_stops=api.use_api(new_rcp_point,proto_all)
	maps = pokemon_pb2.maps()
	maps.ParseFromString(all_stops)
	data_list=location.get_near(maps)
	data_list = sorted(data_list, key = lambda x: x[1])
	if len(data_list)>0:
		print '[+] found: %s Pokestops near'%(len(data_list))
		if local_ses is not None and data_list is not None:
			print '[+] starting show'
			if multi:
				a,b=split_list(data_list)
				p = Process(target=work_half_list, args=(a,local_ses.ses,new_rcp_point))
				o = Process(target=work_half_list, args=(a,local_ses.ses,new_rcp_point))
				p.start()
				o.start()
				p.join()
				o.join()
				print '[!] farming done..'
			else:
				for t in data_list:
					if config.debug:
						print '[!] farming pokestop..'
					walk_random()
					proto_all=logic.all_stops(local_ses)
					api.use_api(new_rcp_point,proto_all)
					time.sleep(3)
					work_with_stops(t,local_ses.ses,new_rcp_point)
	else:
		walk_random()
		work_stop(local_ses,new_rcp_point)
		
def work_with_stops(current_stop,ses,new_rcp_point):
	COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE=location.get_location_coords()
	TARGET_LATITUDE=location.l2f(current_stop[1])
	TARGET_LONGITUDE=location.l2f(current_stop[2])
	TARGET_ALTITUDE=location.l2f(0x4049000000000000)
	Kinder= logic.gen_stop_data(ses,current_stop)
	tmp_api=api.use_api(new_rcp_point,Kinder)
	#proto_all=logic.all_stops(local_ses)
	#api.use_api(new_rcp_point,proto_all)
	#walk_random()
	#time.sleep(3)
	try:
		#walk_random()
		#time.sleep(3)
		if tmp_api is not None:
			map = pokemon_pb2.map()
			map.ParseFromString(tmp_api)
			st= map.sess[0].status
			config.earned_xp+=map.sess[0].amt
			if st==4:
				print "[!] +%s (%s)"%(map.sess[0].amt,config.earned_xp)
			elif st==3:
				print "[!] used"
				#item full
			elif st==2:
				print "[!] charging"
			elif st==1:
				print "[!] walking.."
				#walk_random()
				expPerHour()
				time.sleep(14)
				work_with_stops(current_stop,ses,new_rcp_point)
			else:
				print "[?]:",st
		else:
			print '[-] tmp_api empty'
	except:
		print '[-] error work_with_stops - Trying to restart process'
		restartProcess()

def expPerHour():
	diff = time.time() - startTime
	minutesRun = diff/60.
	hoursRun = minutesRun/60.
	earned = float(config.earned_xp)
	if hoursRun > 0:
		expHour = int(earned/hoursRun)
	else:
		expHour = "n/a"
	print "[!] Gained: %s (%s exp/h)"%(config.earned_xp,expHour)