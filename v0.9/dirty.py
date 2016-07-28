import logic
import api
import time
import datetime
import pokemon_pb2
import location
import json
import config
from multiprocessing import Process

multi=False
show_pok=True
try_item=False

def start_private_show(access_token,ltype,loc):
	#try:
	location.set_location(loc)
	print '[+] Token:',access_token[:40]+'...'
	prot1=logic.gen_first_data(access_token,ltype)
	local_ses=api.get_rpc_server(access_token,prot1)
	try:
		new_rcp_point='https://%s/rpc'%(local_ses.rpc_server,)
	except:
		print '[-] rpc bad'
		start_private_show(access_token,ltype,loc)
	if try_item:
		work_stop(local_ses,new_rcp_point)
	else:
		while(True):
			work_stop(local_ses,new_rcp_point)
	#except:
	#	start_private_show(access_token,ltype,loc)
		
def walk_random():
	COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE=location.get_location_coords()
	COORDS_LATITUDE=location.l2f(COORDS_LATITUDE)
	COORDS_LONGITUDE=location.l2f(COORDS_LONGITUDE)
	COORDS_ALTITUDE=location.l2f(COORDS_ALTITUDE)
	COORDS_LATITUDE=COORDS_LATITUDE+config.steps*25
	COORDS_LONGITUDE=COORDS_LONGITUDE+config.steps*25
	location.set_location_coords(COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE)
	
def walk_random_l(pok):
	COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE=location.get_location_coords()
	COORDS_LATITUDE=location.l2f(pok[1])
	COORDS_LONGITUDE=location.l2f(pok[1])
	COORDS_ALTITUDE=location.l2f(COORDS_ALTITUDE)
	location.set_location_coords(COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE)
	
def split_list(a_list):
	half = len(a_list)/2
	return a_list[:half], a_list[half:]
	
def work_half_list(part,local_ses,new_rcp_point):
	for t in part:
		if config.debug:
			print '[!] farming pokestop..'
		work_with_stops(t,local_ses.ses,new_rcp_point)
	
def get_pok_name(pok):
	with open('pokemon.json') as data_file:    
		data = json.load(data_file)
		for u in data:
			print str(u['Number'])
		
def get_map(local_ses,new_rcp_point):
	proto_all=logic.all_stops(local_ses)
	all_stops=api.use_api(new_rcp_point,proto_all)
	if all_stops is not None:
		return all_stops
	else:
		return get_map(local_ses,new_rcp_point)
		
def catch(maps,local_ses,new_rcp_point):
	data_list=location.get_near_p(maps)
	data_list = sorted(data_list, key = lambda x: x[5])
	if len(data_list)>0:
		print
		print '[!] found %s pokemon'%(len(data_list),)
		for idx, e in enumerate(data_list):
			if(e[0] not in config.list_banned_Pokemon): #Banned Pokemon
				print '[!] %s Type:%s its %s m away'%(idx,e[0],e[len(e)-1],)
		print 
		for idx, pok in enumerate(data_list):
			if(pok[0] not in config.list_banned_Pokemon): #Banned Pokemon
				#print '[!] %s Type:%s its %s m away'%(idx,pok[0],pok[len(pok)-1],)
				#if pok[0] < 22:
				if pok[len(pok)-1] < 600:
					print '[!] Trying to catch Type:%s its %s m away'%(pok[0],round(location.get_distance(location.get_lat(),location.get_lot(),pok[1],pok[2]),3),)
					lat1=location.l2f(location.get_lat())
					lot1=location.l2f(location.get_lot())
					lat2=location.l2f(pok[1])
					lot2=location.l2f(pok[2])
					#print location.l2f(lat1),location.l2f(lot1),location.l2f(lat2),location.l2f(lot2)
					if (lat1>lat2):
						while(lat1<lat2):
							lat1=lat1-config.steps
							location.set_lat(lat1)
							location.set_lot(lot1)
							info_prot= logic.get_info(local_ses.ses,pok)
							tmp_api=api.use_api(new_rcp_point,info_prot)
							time.sleep(2)
					else:
						while(lat1<lat2):
							lat1=lat1+config.steps
							location.set_lat(lat1)
							location.set_lot(lot1)
							info_prot= logic.get_info(local_ses.ses,pok)
							tmp_api=api.use_api(new_rcp_point,info_prot)
							time.sleep(2)
					if (lot1>lot2):
						while(lot1>lot2):
							lot1=lot1-config.steps
							location.set_lat(lat1)
							location.set_lot(lot1)
							info_prot= logic.get_info(local_ses.ses,pok)
							tmp_api=api.use_api(new_rcp_point,info_prot)
							time.sleep(2)
					else:
						while(lot2>lot1):
							lot1=lot1+config.steps
							location.set_lat(lat1)
							location.set_lot(lot1)
							info_prot= logic.get_info(local_ses.ses,pok)
							tmp_api=api.use_api(new_rcp_point,info_prot)
							time.sleep(2)
					#catch_prot= logic.catch_it(local_ses.ses,pok)
					#tmp_api=api.use_api(new_rcp_point,catch_prot)
					tmp_api=catch_t(local_ses,pok,new_rcp_point)
					if tmp_api is not None:
						catch_status = pokemon_pb2.catch_status()
						catch_status.ParseFromString(tmp_api)
						if catch_status.sess[0].status:
							print "[+] " + datetime.datetime.now().strftime("%H:%M:%S")+ " caught pok... %s"%(catch_status.sess[0].status,)
					else:
						print '[-] catch data is none'
					#exit()
				#exit()
				#walk_random()
	walk_random()
		
def catch_t(local_ses,pok,new_rcp_point):
	catch_prot= logic.catch_it(local_ses.ses,pok)
	return api.use_api(new_rcp_point,catch_prot)
		
def work_stop(local_ses,new_rcp_point):
	all_stops=get_map(local_ses,new_rcp_point)
	#maps = pokemon_pb2.maps()
	maps = pokemon_pb2.maps_1()
	#try:
	maps.ParseFromString(all_stops)
	#except:
	#	print '[-] map bad'
	#	work_stop(local_ses,new_rcp_point)
	if try_item:
		print '[+] deleting 9 pokeballs'
		info_prot= logic.delete_items(local_ses.ses,1,9)
		tmp_api=api.use_api(new_rcp_point,info_prot)
		exit()
	else:
		if show_pok:
			catch(maps,local_ses,new_rcp_point)
		else:
			data_list=location.get_near(maps)
			data_list = sorted(data_list, key = lambda x: x[3])
			if len(data_list)>0:
				print '[+] found: %s Pokestops near you'%(len(data_list),)
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
							#print t[0]
							#print t[1],t[2]
							#print location.get_lat(),location.get_lot()
							#print location.l2f(t[1]),location.l2f(t[2])
							#print location.l2f(location.get_lat()),location.l2f(location.get_lot())
							#print location.get_distance(location.get_lat(),location.get_lot(),t[1],t[2])
							print
							print '[!] %s m away'%(round(location.get_distance(location.get_lat(),location.get_lot(),t[1],t[2]),3),)
							if config.debug:
								print '[!] farming pokestop..'
							work_with_stops(t,local_ses.ses,new_rcp_point)
			else:
				walk_random()
				#work_stop(local_ses,new_rcp_point)
		
def work_with_stops(current_stop,ses,new_rcp_point):
	lat1=location.l2f(location.get_lat())
	lot1=location.l2f(location.get_lot())
	lat2=location.l2f(current_stop[1])
	lot2=location.l2f(current_stop[2])
	#print location.l2f(lat1),location.l2f(lot1),location.l2f(lat2),location.l2f(lot2)
	walk_to_s=True
	if walk_to_s:
		if (lat1>lat2):
			while(lat1<lat2):
				lat1=lat1-config.steps*5
				location.set_lat(lat1)
				location.set_lot(lot1)
				info_prot= logic.gen_stop_data_pre(ses,current_stop)
				tmp_api=api.use_api(new_rcp_point,info_prot)
				time.sleep(1)
		else:
			while(lat1<lat2):
				lat1=lat1+config.steps*5
				location.set_lat(lat1)
				location.set_lot(lot1)
				info_prot= logic.gen_stop_data_pre(ses,current_stop)
				tmp_api=api.use_api(new_rcp_point,info_prot)
				time.sleep(1)
		if (lot1>lot2):
			while(lot1>lot2):
				lot1=lot1-config.steps*5
				location.set_lat(lat1)
				location.set_lot(lot1)
				info_prot= logic.gen_stop_data_pre(ses,current_stop)
				tmp_api=api.use_api(new_rcp_point,info_prot)
				time.sleep(1)
		else:
			while(lot2>lot1):
				lot1=lot1+config.steps*5
				location.set_lat(lat1)
				location.set_lot(lot1)
				info_prot= logic.gen_stop_data_pre(ses,current_stop)
				tmp_api=api.use_api(new_rcp_point,info_prot)
				time.sleep(1)
	Kinder= logic.gen_stop_data(ses,current_stop)
	tmp_api=api.use_api(new_rcp_point,Kinder)
	try:
		if tmp_api is not None:
			map = pokemon_pb2.map()
			map.ParseFromString(tmp_api)
			st= map.sess[0].status
			if map.sess[0].amt is not None:
				config.earned_xp+=map.sess[0].amt
			if st==4:
				print "[!] " + datetime.datetime.now().strftime("%H:%M:%S") + " bag full +%s (%s)"%(map.sess[0].amt,config.earned_xp)
			elif st==3:
				print "[!] " + datetime.datetime.now().strftime("%H:%M:%S")+ " cooldown"
			elif st==2:
				print "[!] " + datetime.datetime.now().strftime("%H:%M:%S")+ " charging"
			elif st==1:
				print "[!] " + datetime.datetime.now().strftime("%H:%M:%S")+ " +%s (%s)"%(map.sess[0].amt,config.earned_xp)
				#work_with_stops(current_stop,ses,new_rcp_point)
			else:
				print "[?]:",st
		else:
			print '[-] tmp_api empty'
	except:
		print '[-] error work_with_stops'
