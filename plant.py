from __future__ import division
import os
import shutil
import datetime
import time
import log
import urllib
import urllib2
import hashlib
import socket
from iniparser import IniParser

def get_hash(f):
	log.log('get_hash function called')
	
	input = open(f, 'rb')

	md5 = hashlib.md5()

	buffer = input.read(2 ** 20)
	while buffer:
		md5.update(buffer)
		buffer = input.read(2 ** 20)
	#endwhile

	input.close()

	return md5.hexdigest()
#enddef

def isfile(fn):
	t = './temp'

	log.log('asking for %s' % fn)
	for d in sorted(os.listdir(t)):
		if os.path.isfile('%s/%s/%s' % (t, d, fn)): return '%s/%s/%s' % (t, d, fn)
	#endfor
	
	log.log('no %s' % fn)
	
	return False
#enddef

def prepare_temp(mj):
	log.log('prepare_temp function called')

	t = './temp'
	a = '../../incoming/%s/archive' % mj
	if not os.path.isdir(a):
		a = './incoming/%s/archive' % mj
	#endif
	
	log_counter = 1
	ret = None
	l = None
	
	if os.path.isdir(t): shutil.rmtree(t)

	os.mkdir(t)

	if not os.path.isdir(a):
		log.log('no archive for %s' % mj)
		return None, 0
	#endif
	
	l = sorted(os.listdir(a), reverse=True)
	
	for f in l:
		if 'log' in f and log_counter <= 3:
			unpack('%s/%s' % (a, f), '%s/%s' % (t, log_counter))

			if log_counter == 1: ret = f

			log_counter += 1
		# TODO kdyz se ini najde jako prvni, tak mi to nevezme zadny log
		elif 'ini' in f:
			unpack('%s/%s' % (a, f), '%s/ini' % t)
			
			return ret, os.path.getmtime('%s/%s' % (a, f))
		#endif
	#endfor
	
	return ret, 0
#enddef

def unpack(s, d):
	log.log('unpacking %s' % s)
	
	os.system('7z x %s -o%s' % (s, d))
#enddef

def give_lines(fn, source):
	log.log('asked for lines %s, %s' % (fn, source))
	
	t = './temp'
	
	if source == 'ini':
		f = open('%s/ini/%s' % (t, fn))
		#for l in f.readlines():
		for l in f:
			yield l
		#endfor
		
		return
	#endif
		
	while source:
		if not os.path.isfile('%s/%i/%s' % (t, source, fn)):
			source -= 1
			continue
		#endif
		
		f = open('%s/%i/%s' % (t, source, fn))
		#for l in f.readlines():
		for l in f:
			yield l
		#endfor
		
		f.close()
		
		source -= 1
	#endwhile
#enddef

def get_datetime_from_log(l):
	#TODO tohle vylepsit az bude jedina verze logu casu
	try: ret = datetime.datetime.strptime(l.split(': ')[0], '%Y-%m-%d %H:%M:%S')
	except:
		try: ret = datetime.datetime.strptime(l.split(': ')[0], '%Y-%m-%d %H:%M:%S.%f')
		except:
			try: ret = datetime.datetime.strptime(l.split('[')[1].split(': ')[0], '%Y/%m/%d %H:%M:%S]')
			except:
				try: ret = datetime.datetime.strptime(l.split(': ')[0], '[%Y/%m/%d %H:%M:%S]')
				except:
					try: ret = datetime.datetime.strptime(l.split(']')[0], '[%Y-%m-%d %H:%M:%S.%f')
					except:
						try: ret = datetime.datetime.strptime(' '.join(l.split()[0:2]), '%Y-%m-%d %H:%M:%S.%f:')
						except:
							try: ret = datetime.datetime.strptime(' '.join(l.split()[0:2]), '[%Y-%m-%d %H:%M:%S]')
							except:
								try: ret = datetime.datetime.strptime(' '.join(l.split()[0:2]), '[%Y/%m/%d %H:%M:%S]')
								except:
									try: ret = datetime.datetime.strptime(' '.join(l.split()[0:2]), '%Y/%m/%d %H:%M:%S.%f')
									except:
										#log.info('%s' % l)
										ret = datetime.datetime.strptime('1970/01/01 %s' % l.split()[0], '%Y/%m/%d %H:%M:%S.%f')
									#endtry
								#endtry
							#endtry
						#endtry
					#endtry
				#endtry
			#endtry
		#endtry
	#endtry
	
	return ret
#enddef


def get_adaptivity(mj):
	log.log('get_adaptivity function called')
	
	class Adaptivity():
		def __init__(self, silo, scale, coefficient):
			self.silo = silo
			#log.info('creating new class for %s' % self.silo)
		
			self.scale = scale
			self.coefficient = coefficient
			self.first = None
		#enddef
		def check_line(self, line):
			if not self.scale in line: return
	
			if not self.first and self.first != 0:
				self.first = int(line.split('=')[1])
				#log.info('%s first %s' % (self.silo, self.first))
			else:
				self.adaptivity = (int(line.split('=')[1]) - self.first) * self.coefficient
				self.time = get_datetime_from_log(line)
				
				return 'all done'
			#endif
		#enddef
	#enclass
	
	ret = {} # ret[silo] = [(time, adaptivity), ...]
	materials = {'AGG': 'Aggregate', 'CEM': 'Cement', 'ADM': 'Admixture', 'WTR': 'Water'}
	cache = {} # cache[silo] = {'Scale': scale, 'Coefficient': coefficient}
	incompletes = [] # incompletes = [Adativity(), ...]

	f = './temp/ini/base.ini'
	if not os.path.isfile(f): return ret
	base = IniParser()
	base.read(f)

	f = './temp/ini/settings.ini'
	if not os.path.isfile(f): return ret
	settings = IniParser()
	settings.read(f)
	
	fn = 'recordedsignals.log'
	
	for l in give_lines(fn, 3):
		for m in materials:
			if m in l and 'O_' in l and 'intoBin' in l and ')=0' in l:
				silo = '%s%s' % (m, l.split(m)[1].split('into')[0]) # for example AGG5
				
				if not silo in cache:
					bin = 'Bin%s' % l.split('intoBin')[1].split(')=')[0]
					scale = '%s_Scale%s' % (materials[m], base.get('%s_%s' % (materials[m], bin), 'CorrespondingScale'))
					signal = base.get('AnalogInput_Signals', scale)
					coefficient = settings.getfloat('AnalogInput_Coefficients', 'Coefficient%s' % signal)
					
					cache[silo] = {}
					cache[silo]['Scale'] = scale
					cache[silo]['Coefficient'] = coefficient
				#endif
				
				if not silo in ret: ret[silo] = []
				
				# Adding new adaptivities to list
				incompletes.append(Adaptivity(silo, cache[silo]['Scale'], cache[silo]['Coefficient']))
				
				break
			#endif
		#endfor
		
		if 'Scale' in l:
			for i in incompletes:
				if i.check_line(l):
					ret[i.silo].append((i.time, i.adaptivity))
					incompletes.remove(i)
				#endif
			#endfor
		#endif
	#endfor

	# read alternately adaptivity from info.txt
	fn = 'control.log'

	materials = {'aggregate': 'AGG', 'cement': 'CEM', 'admixture': 'ADM', 'water': 'WTR'}

	for l in give_lines(fn, 3):
		if not 'adaptivity for' in l: continue

		material_type = materials[l.split(' for ')[1].split(' bin ')[0]]
		silo_number = l.split(' silo ')[1].split(':')[0]
		adaptivity = l.split(': ')[-1].strip()
		time = get_datetime_from_log(l)

		silo = '%s%s' % (material_type, silo_number)
		if not silo in ret: ret[silo] = []

		ret[silo].append((time, float(adaptivity)))
	#endfor
	
	# create output files
	for silo in ret:
		log.info('creating file for silo %s' % silo)
		
		a = '../public_html_incoming'
		if not os.path.isdir(a):
			a = './public_html_incoming'
		#endif
		f = open('%s/%s%s.csv' % (a, mj, silo), 'w')
		
		for x,y in ret[silo]:
			f.write('%s;%i\n' % (x.strftime('%Y-%m-%d %H:%M:%S'), y))
		#endfor
		
		f.close()
	#endfor
	
	return ret
#enddef

def assign_materials_to_silos(adaptivity):
	log.info('assign_materials_to_silos function called')
	pom = {'AGG': 'Aggregate', 'CEM': 'Cement', 'ADM': 'Admixture', 'WTR': 'Water'}
	ret = {}
	
	f = './temp/ini/placemnt.ini'
			
	if not os.path.isfile(f): return ret
			
	i = IniParser()
	i.read(f)
	
	for silo in adaptivity:
		base = silo[0:3]
		number = silo[3:]
	
		for s in i.sections():
			if pom[base] in s and 'Silo%s' % number in s:
				ret[silo] = i.get(s, 'Name')
			#endif
		#endfor
	#endfor
	
	return ret
#enddef

def get_wiki(mj):
	log.log('get_wiki function called')
	
	d = {}
	d['action'] = 'login'
	d['name'] = 'ApplicationAnalyser'
	d['password'] = 'atx43872298'
	d['action'] = 'raw'
	d['login'] = 'xx'

	txheaders = {'User-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

	url = 'http://wiki.asterix.cz/MixingPlants'
	
	req = urllib2.Request(url, urllib.urlencode(d), txheaders)
	
	r = None
	while not r:
		try: r = urllib2.urlopen(req)
		except:
			log.log('unable to get r1')
			time.sleep(60)
		#endtry
	#endwhile
	
	time.sleep(5) #pokus
	
	wiki_list = r.read()
		
	url = 'http://wiki.asterix.cz/%s' % mj.upper()
		
	req = urllib2.Request(url, urllib.urlencode(d), txheaders)
	
	r = None
	while not r:
		try: r = urllib2.urlopen(req)
		except:
			log.log('unable to get r2')
			time.sleep(60)
		#endtry
	#endwhile
	wiki_mj = r.read()
		
	return wiki_list, wiki_mj
#enddef

def get_io_communication_failures():
	log.log('get_io_communication_failures function called')
	
	skip = datetime.datetime.now()
	ret = {}
	
	messages = ['[c200]', '[c201]', '[c202]', '[c203]']
	
	fn = 'control.log'

	if not isfile(fn):
		return ret
	#endif
		
	for l in give_lines(fn, 3):
		#TODO - vyresit nejak, ze kdyz to odklepnou, tak se to nezaznamena 2x
		if '[C300]' in l or '[C301]' in l or '[C302]' in l: skip = get_datetime_from_log(l)
	
		for e in messages:
			if e in l.lower() and get_datetime_from_log(l) == skip:
				if not e in ret: ret[e] = []	
				ret[e].append(get_datetime_from_log(l))
			#endif
		#endfor
	#endfor
		
	return ret
#enddef

def get_lan_settings():
	log.log('get lan settings function called')
	
	name = ''
	domain = ''
	ret = []
	
	fn = 'adapters.txt'

	if not isfile(fn):
		return name, domain, ret
	#endif
	
	class Adapter():
		def __init__(self):
			self.adapter = ''
			self.address = ''
			self.subnet = ''
			self.gateway = ''
			self.dns = []
			self.dhcp = 0
			self.wins1 = ''
			self.wins2 = ''
		#enddef
		
		def process(self, lines):
			dns_watch = 0
			
			for l in lines:
				if 'adapt' in l.lower() and 'Ethernet ' in l and l.strip().endswith(':'):
					pom = ''
					try: pom = l.split(' adapter ')[1]
					except: pass
					
					if pom: self.adapter = pom[0:-1]
					else:
						pom = l.split('Ethernet ')[1]
						if pom: self.adapter = pom[0:-1]
					#endis
				elif ' DHCP ' in l:
					self.dhcp = 1
					if ' Ne' in l or ' No' in l: self.dhcp = 0
				elif ('Adresa IP' in l or 'IPv4 Address' in l) and not self.address:
					self.address = l.split()[-1]
					if '(' in self.address: self.address = self.address.split('(')[0]
				elif 'Maska pods' in l or 'Subnet Mask' in l:
					self.subnet = l.split()[-1]
				elif ('choz' in l and 'br' in l) or 'Default Gateway' in l:
					self.gateway = l.split()[-1]
					if not '.' in self.gateway: self.gateway = ''
				elif 'Servery DNS' in l or 'DNS Servers' in l:
					dns_watch = 1
					pom = l.split()[-1]
			
					if '.' in pom: self.dns.append(pom)
					else: dns_watch = 0
				elif ('Pri' in l and 'server WINS' in l) or 'Primary WINS Server' in l:
					dns_watch = 0
					self.wins1 = l.split()[-1]
				elif 'Sekund' in l and 'server WINS' in l or 'Secondary WINS Server' in l:
					self.wins2 = l.split()[-1]
				elif dns_watch == 1:
					pom = ''
					
					try: pom = l.split()[-1]
					except: pass
					
					if '.' in pom:
						self.dns.append(pom)
					#endif
				#endif
			#endfor
		#enddef
	#endclass

	counter = 0
	lines = {}
	
	for l in give_lines(fn, 1):
		if not l.startswith('   ') and 'adapt' in l.lower():
			counter += 1
		#endif

		if not counter in lines: lines[counter] = []
		lines[counter].append(l)

		if 'hostitele' in l or 'Host Name' in l:
			name = l.split()[-1]
		elif ('Prim' in l and 'pona DNS' in l) or ('Primary Dns Suffix' in l):
			pom = l.split()[-1]
			if not ':' in pom: domain = pom
		#endif
	#endfor
	
	for i in sorted(lines):
		x = Adapter()
		x.process(lines[i])
		
		if x.adapter:
			ret.append(x)
	#endfor
	print name, domain, ret
	return name, domain, ret
#enddef

def get_last_state():
	log.log('get_state function called')
	
	ret = 'undetermined'
	
	fn = 'loader.log'

	if not isfile(fn):
		return
	#endif
		
	for l in give_lines(fn, 3):
		if 'unload_mode=\'True\'' in l: ret = ''
		elif 'unload_mode=\'False\'' in l and 'reset_mode=\'False\'' in l: ret = 'running'
		elif 'unload_mode=\'False\'' in l and 'reset_mode=\'True\'' in l: ret = 'restart'
	#endfor
		
	return ret
#enddef

class Plant():
	def __init__(self, mj):
		self.mj = mj

		log.log('Processing %s' % self.mj)
	
		#self.temp = './temp2'
	
		self.archive = './archive'
		
		self.cemex = {'mj143': '10.140.66.52',
		'mj04': '10.140.8.52',
		'mj101': '10.140.38.52',
		'mj18': '10.140.23.52',
		'mj125': '10.140.34.52',
		'mj148': '10.140.36.52',
		'mj22': '10.140.42.52',
		'mj48': '10.140.44.52',
        'mj107': '10.140.73.52',
        'mj126': '10.140.74.52',
		'mj36': '10.140.47.52', 
		'mj151': '10.140.62.52'}
		
		self.now = datetime.datetime.now()
		
		#self.latest_logs = get_latest_logs('%s/%s' % (self.mj, self.archive), self.now)
		#log.log('latest logs: %s' % self.latest_logs)

		#self.latest_ini = get_latest_ini('%s/%s' % (self.mj, self.archive))
		#log.log('latest ini: %s' % self.latest_ini)
	#enddef
	
	def process(self):
		self.latest_log, self.ini_created = prepare_temp(self.mj)
		
		self.wiki_list, self.wiki_mj = get_wiki(self.mj)
		
		self.adaptivity = get_adaptivity(self.mj)
		
	
		self.materials_assignment = assign_materials_to_silos(self.adaptivity)
		
		
		
		self.io_communication_failures = get_io_communication_failures()
		
		self.last_state = get_last_state()
		
		self.lan_name, self.lan_domain, self.lan_adapters = get_lan_settings()
		
		self.get_tasks()
		self.ports = self.get_open_ports()
		self.get_last_restart()
		self.get_bin_versions()
		self.get_ini_hashes()
		self.get_sizes()
		self.get_cpu_usage()
		self.get_app_name()
		self.get_wiki_data()
		self.get_hardware()
		self.get_structure()
		self.get_coefficients()
		self.get_little_amounts()
		self.get_smart()
		self.get_router_errors()
		self.get_libsh_errors()
		self.get_control_errors()
		self.get_control_messages()

		self.get_aggregate_close_times()
		#self.get_unauthorized_operations()
		self.get_unhandled_exeptions()
	#enddef
	
	def get_little_amounts(self):
		log.info('little amounts function called')
		
		silo = {}
		self.little_amounts_fails = {}
		
		doba = None
		vaha = None
		navazeno = None
		analog = None
		adaptivita = None
		pozadavek = None
		zasobnik = 99 # can delete this line after three month (bacuse of error in info txt from Piestany)
	
		fn = 'control.log'
		
		for l in give_lines(fn, 3):
			if 'poddavkovani ' in l.lower():
				zasobnik = int(l.split()[-1])
				vaha = None
				navazeno = None
				pozadavek = None
			elif 'dobaotevreni ' in l.lower():
				pom = float(l.split()[-1])
				if pom > 3 or pom < 0: continue  # filtrace demetskych hodnot v milisekundach a zapornych hodnot
				doba = pom
			elif 'mezistav1 ' in l.lower():
				vaha = float(l.split()[-1])
			elif 'NejblizsiCil2' in l and vaha:
				pozadavek = float(l.split()[-1]) - vaha
			elif 'PrumernaHodnotaAI[CisloAnalogu] - VychoziVaha' in l:
				analog = float(l.split()[-1])
			elif 'frakcenamereno2 ' in l.lower() and vaha:
				navazeno = float(l.split()[-1]) - vaha
			#endif
		
			if doba and navazeno:
				log.info('%i, %0.2f, %i' % (navazeno, doba, zasobnik))
				
				if navazeno < 30 or navazeno > 500:
					log.info('little amount fail: %i, %0.2f, %i' % (navazeno, doba, zasobnik))
					
					if not zasobnik in self.little_amounts_fails:
						self.little_amounts_fails[zasobnik] = []
					#endif
					
					self.little_amounts_fails[zasobnik].append('%i, %0.2f' % (navazeno, doba))
					doba = None
					continue
				#endif
				
				if analog: adaptivita = navazeno - analog + vaha
				if not zasobnik in silo: silo[zasobnik] = []		
				silo[zasobnik].append((doba, navazeno, pozadavek, adaptivita))

				doba = None
				vaha = None
				navazeno = None
				analog = None
				adaptivita = None
			#endif
		#endfor

		#log.info('%s' % silo)

		self.silo = {}

		self.little_amounts_error = False
		
		f = './temp/ini/adapt.ini'
		if not os.path.isfile(f): return
		adapt = IniParser()
		adapt.read(f)

		f = './temp/ini/parameters.ini'
		if not os.path.isfile(f): return
		parameters = IniParser()
		parameters.read(f)

		for k in silo:
			self.little_amounts_error = adapt.has_option('Aggregate', 'VelocityOfFilling1-%s' % k)
			
			param_velocity = 0
			param_offset = 0
			
			if parameters.has_option('Aggregate_Bin1_Silo%s' % k, 'Velocity_Base'):
				param_velocity = parameters.getint('Aggregate_Bin1_Silo%s' % k, 'Velocity_Base')
				param_offset = parameters.getfloat('Aggregate_Bin1_Silo%s' % k, 'Additional_Time')
			else:
				self.little_amounts_error = True
			#endif
		
			x = 0
			sez = {}
	
			while x < 1.5:
				if not x in sez: sez[x] = []
				for doba, navazeno, pozadavek, adaptivita in silo[k]:
					if doba-x == 0: continue #I dont know why
					sez[x].append(navazeno/(doba - x))
				#endfor
				x = x + 0.01
			#endwhile

			minimum = None
			
			for x in sorted(sez):

				sqr_sum = 0
				avg = 0
				dev = 0
			
				avg = sum(sez[x]) * 1.0 / len(sez[x])

				for velocity in sez[x]:
					sqr_sum += ((velocity - avg) ** 2) / len(sez[x])
				#endfor

				dev = sqr_sum ** 0.5
				
				if not minimum or dev < minimum:
					#print dev
					minimum = dev
					self.silo[k] = (x, avg, len(sez[x]), dev, param_velocity, param_offset)
				#endif
			#endfor
		#endfor
	#enddef
	
	def get_tasks(self):
		log.log('get_tasks function called')
		
		self.tasks = []
		self.important_task = False
	
		focus = False
		
		for l in self.wiki_mj.split('\n'):
			if 'koly ==' in l: focus = True
			elif '==' in l: focus = False
			elif '*' in l and focus:
				if '!' in l: self.important_task = True
				self.tasks.append(l.strip())
			#endif
		#endfor
		
		log.log('%s' % self.tasks)	
	#enddef
	
	def get_open_ports(self):
		log.log('get_open_ports function called')
		
		ports = []

		try:
			soc_family = socket.getaddrinfo('%s.asterix.cz' % self.mj, 0)[0][0]
		except:
			log.exception('socket.getaddrinfo exception')
			soc_family = None
		#endtry

		if self.mj in self.cemex:
			log.info('cemex')

			f = os.popen('nmap -Pn -p 22,3389,5900 %s' % self.cemex[self.mj])
		elif soc_family == socket.AF_INET:
			log.info('IPv4')

			f = os.popen('nmap -Pn -p 22,3389,5900 %s.asterix.cz' % self.mj)
		elif soc_family == socket.AF_INET6:
			log.info('IPv6')

			f = os.popen('nmap -6 -Pn -p 22,3389,5900 %s.asterix.cz' % self.mj)
		else:
			log.error('unknown address family: %s' % soc_family)
			return ports
		#endif

		for l in f.read().split('\n'):
			log.info(l)
		
			if '22/tcp' in l and 'open' in l:
				ports.append('22')
			elif '3389/tcp' in l and 'open' in l:
				ports.append('3389')
			elif '5900/tcp' in l and 'open' in l:
				ports.append('5900')
			#endif
		#endfor
		
		return ports
	#enddef	
	
	def get_smart(self):
		log.log('get_smart function called')
		
		list_of_zero_attributes = (1, 5, 10, 184, 188, 196, 197, 198, 201, 250, 254, 199) #199 is not important marker

		focus = False
		
		self.smart_created = 0		
		self.count_of_smart_attributes = 0
		self.smart_faults = []
		self.last_long = 0
		self.last_short = 0
		self.power_on_hours = 0
		self.smart_supported = 1
		self.smart_log = []
		
		restart = 0
	
		fn = 'smart.log'

		try: self.smart_created = os.path.getmtime(isfile(fn))
		except: return
		#endtry

		for l in give_lines(fn, 1):
			if 'ID' in l: focus = True
			elif len(l) < 3: focus = False
			elif 'Self-test Log not supported' in l: self.smart_supported = 0
			elif 'Short offline' in l and 'Completed without error' in l and not self.last_short:
				self.smart_log.append(l.strip())
				
				self.last_short = int(l.split()[-2])
				if self.last_short + restart <= self.power_on_hours: self.last_short = self.last_short + restart #because of restart counting every 65536 minutes
			elif 'Extended offline' in l and 'Completed without error' in l and not self.last_long:
				self.smart_log.append(l.strip())
				
				self.last_long = int(l.split()[-2])
				if self.last_long + restart <= self.power_on_hours: self.last_long = self.last_long + restart #because of restart counting every 65536 minutes
			#endif
				
			if not focus: continue
				
			x = l.split()
				
			try: 
				ident = int(x[0])
				
				if ident == 9:
					self.smart_log.append(l.strip())				

					self.power_on_hours = int(x[-1])
					restart = self.power_on_hours*60//65536*65536//60 # time of counter restart for self-test log
				#endif
				
				if ident in list_of_zero_attributes:
					self.smart_log.append(l.strip())				

					self.count_of_smart_attributes += 1
					
					raw = int(x[-1])
					if raw != 0:
						self.smart_faults.append([ident, x[1], raw])
					#endif
				#endif
			except: pass
			#endtry
		#endfor
	#enddef

	def get_bin_versions(self):
		log.log('get_bin_versions function called')
		
		fn = 'versions.txt'
		
		self.versions_created = 0
		self.versions = {}

		try: self.versions_created = os.path.getmtime(isfile(fn))
		except: return
		#endtry
		
		for l in give_lines(fn, 1):
			app = l.split('.')[0]
			ver = l.split()[1]
			hash = l.split()[2]
		
			self.versions[app] = (ver, hash)
		#endfor
		
		log.log('%s' % self.versions)
	#enddef
	
	def get_coefficients(self):
		log.log('get_coefficients function called')
		
		self.coefficients = {}
		converter = 8192
		if self.mj in ('mj04', 'mj22', 'mj36'): converter = 4096
		l = []

		f = './temp/ini/base.ini'
			
		if not os.path.isfile(f): return
			
		i = IniParser()
		i.read(f)
		
		for s in i.options('AnalogInput_Signals'):
			if 'scale' in s.lower() and i.get('AnalogInput_Signals', s) != 'x': l.append((s, i.getint('AnalogInput_Signals', s)))
		#endfor
		
		f = './temp/ini/parameters.ini'
			
		if not os.path.isfile(f): return
			
		i = IniParser()
		i.read(f)
				
		for s, a in l:
			self.coefficients[s] = i.getfloat(s, 'Range')
		#endfor
		
		f = './temp/ini/settings.ini'
			
		if not os.path.isfile(f): return
			
		i = IniParser()
		i.read(f)
		
		for s, a in l:
			print s, a
			print self.coefficients[s]
			print i.getfloat('AnalogInput_Coefficients', 'Coefficient%i' % a)
			print type(self.coefficients[s])
			print type(i.getfloat('AnalogInput_Coefficients', 'Coefficient%i' % a))
			capacity = self.coefficients[s]
			difference = (i.getfloat('AnalogInput_Coefficients', 'Coefficient%i' % a) / (capacity/converter) - 1) * 100
			offset = i.getint('AnalogInput_Offsets', 'Offset%i' % a)
			
			self.coefficients[s] = (capacity, difference, offset)
		#endfor
	#enddef
	
	def get_structure(self):
		log.log('get_structure function called')
		
		self.structure = []

		f = './temp/ini/parameters.ini'
			
		if not os.path.isfile(f): return
			
		i = IniParser()
		i.read(f)
			
		self.structure.append(('mixer', i.get('Mixer', 'Volume')))
			
		f = './temp/ini/base.ini'
			
		if not os.path.isfile(f): return
			
		i = IniParser()
		i.read(f)
			
		if i.getint('General', 'WeighingConveyer') > 0: self.structure.append(('weighing conv', i.getint('General', 'WeighingConveyer')))
		if i.getint('Structure', 'Lifts') > 0: self.structure.append(('lifts', i.getint('Structure', 'Lifts')))
		if i.getint('Structure', 'Conveyers') > 0: self.structure.append(('convs', i.getint('Structure', 'Conveyers')))
		if i.getint('Structure', 'Reservoirs') > 0: self.structure.append(('reservoirs', i.getint('Structure', 'Reservoirs')))
			
		for sec in ('Aggregate_Bin', 'Cement_Bin', 'Water_Bin', 'Admixture_Bin'):
			silos = 0
			
			#goes through up to 10 possible bins
			for num in range(1, 10):
				pom = i.getint('%s%i' % (sec, num), 'Silos', 0)
				if pom > silos: silos = pom
			#endfor
				
			abr = sec.split('_')[0]
			self.structure.append(('%s' % abr.lower(), '%i -> %i -> %i' % (silos, i.getint(abr, 'Bins'), i.getint(abr, 'Scales'))))
		#endfor
			
		x = i.get('BinaryInput_Signals', 'I_Bin1CEMclosed', 'x').strip()
		if not x in ('x', '255'): self.structure.append(('cement_bin1 limit switch signal', x))
		x = i.get('BinaryInput_Signals', 'I_Bin2CEMclosed', 'x').strip()
		if not x in ('x', '255'): self.structure.append(('cement_bin2 limit switch signal', x))

		if i.getint('Hardware', 'IND-1') > 2: self.structure.append(('hardware', 'old'))
		else: self.structure.append(('hardware', 'new'))
		
		x = i.get('Hardware', 'PointerCounts', 'x').strip()
		self.structure.append(('pointercounts', x))
	#enddef
	
	def get_ini_hashes(self):
		log.log('get_ini_hashes function called')
		
		self.ini_hashes = {}
		
		t = './temp/ini'
		
		if not os.path.isdir(t): return
		
		for f in os.listdir(t):
			self.ini_hashes[f] = get_hash('%s/%s' % (t, f))
		#endfor
	#enddef
	
	def get_sizes(self):
		log.log('get_sizes function called')
		
		fn = 'sizes.txt'
		
		self.sizes = {}

		self.sizes['created'] = 0
		self.sizes['files'] = 0
		self.sizes['size'] = 0 		

		try: self.sizes['created'] = os.path.getmtime(isfile(fn))
		except: return
		#endtry
		
		for l in give_lines(fn, 1):
			if ' ..\\archive' in l: continue #excludes archive folder in root
			if ' ..\\visual\\data\\' in l: continue #excludes visual data folder
			
			
			
			files = l.split('files: ')[-1].split(';')[0]
			if files: files = int(files)
			else: files = 0
			#endif
				
			#size = l.split('size: ')[-1].split(';')[0].split(' ')[0] #TODO: This is because of error in sizes file, can be fixed after month
			size = l.split('size: ')[-1].split(';')[0]
			if size: size = int(size)
			else: size = 0
			#endif
		
			self.sizes['files'] = self.sizes['files'] + files
			self.sizes['size'] = self.sizes['size'] + size 		
		#endfor
	#enddef
	
	def get_app_name(self):
		log.log('get_app_name function called')
	
		self.app_name = ''
		for l in self.wiki_list.split('\n'):
			if '%s]' % self.mj in l.lower():
				for x in l.split()[2:]:
					self.app_name += '%s ' % x
				#endfor

				break
			#endif
		#endfor
	#enddef
	
	def get_cpu_usage(self):
		log.log('get_cpu_usage function called')
		
		self.cpu_usage = {}
	
		fn = 'management.log'
	
		for l in give_lines(fn, 3):
			if 'cpu:' in l:
				date = get_datetime_from_log(l)
						
				self.cpu_usage[date] = []
						
				l = l.split(': ', 1)[1]
				if 'INFO' in l: l = l.split(': ', 1)[1] #because of new log function
				for x in l.split('; '):
					self.cpu_usage[date].append((x.split(': ')[0], float(x.split(': ')[1])))
				#endfor
			#endif
		#endfor
	#enddef
	
	def get_libsh_errors(self):
		log.log('get_libsh_errors function called')
		
		self.libsh = {}
	
		fn = 'libsh.log'
		
		if not isfile(fn):
			self.libsh[0] = 'libsh.log not found'
			return
		#endif
	
		for l in give_lines(fn, 1):
			if 'non-existing' in l:
				self.libsh[os.path.getmtime(isfile(fn))] = l.split('variable')[1].strip()
					
				break
			#endif
		#endfor
	#enddef
	



	def get_adaptivity_old_unsed(self):
		log.log('get_adaptivity function called')


		
		fn = 'recordedsignals.log'



		materials = ('AGG', 'CEM', 'WTR', 'ADM')
		check = {}
		self.adaptivity = {}
		delete = False
		
		if not isfile(fn):
			return
		#endif
		
		for l in give_lines(fn, 3):
			for x in check:
				#print x
				if len(check[x]) == 2 and check[x][0] in l:
					#print 'line 2  ' + x + l
					#time.sleep(1)
					if check[x][0] in l:
						if not x in self.adaptivity: self.adaptivity[x] = []
						self.adaptivity[x].append(int(l.split('=')[1]) - check[x][1])
						delete = x
					#endif
				#endif

				if len(check[x]) == 0 and 'Scale' in l:
					#print 'line 0  ' + x + l
					#time.sleep(1)
					check[x].append(l.split('(')[1].split(')')[0])
					check[x].append(int(l.split('=')[1]))
				#endif
			#endfor
			
			if delete:
				del check[delete]
				delete = False
			#endif
			
			for m in materials:
				if 'O_%s' % m in l and 'intoBin' in l and '=0' in l:
					mat = '%s%i' % (m, int(l.split(m)[1][0]))
					#print mat + ' found'
					#time.sleep(1)
					check[mat] = []
				#endif
			#endfor
		#endfor
	#enddef
	
	def get_aggregate_close_times(self):
		log.log('get_aggregate_close_time function called')
		
		fn = 'recordedsignals.log'

		aggregates = {}
		self.close_times = {}
		delete = False
		
		if not isfile(fn):
			return
		#endif
		
		for l in give_lines(fn, 3):
			for silo in aggregates:
				if 'stop' in aggregates[silo] and 'I_AGG%i' % silo in l and 'intoBin' in l and '=1' in l:
					aggregates[silo]['closed'] = get_datetime_from_log(l)

					if not silo in self.close_times: self.close_times[silo] = []

					if aggregates[silo]['stop'] - aggregates[silo]['start'] > datetime.timedelta(seconds=4):
						delta = aggregates[silo]['closed'] - aggregates[silo]['stop']
					
						if delta.total_seconds() < 3:
							self.close_times[silo].append((delta, aggregates[silo]['stop'], aggregates[silo]['closed']))
						#endif
					#endif
					
					delete = silo
				#endif
			#endfor
			
			if delete:
				del aggregates[delete]
				delete = False
			#endif
			
			if 'O_AGG' in l and 'intoBin' in l and '=1' in l:
				silo = int(l.split('AGG')[1][0])
				if not silo in aggregates: aggregates[silo] = {}
				
				aggregates[silo]['start'] = get_datetime_from_log(l)
			#endif
			
			if 'O_AGG' in l and 'intoBin' in l and '=0' in l:
				silo = int(l.split('AGG')[1][0])
				
				if not silo in aggregates: continue
				#endif
				#if agg in check: del check[agg][0]
				
				#aggregates[silo] = {}
				aggregates[silo]['stop'] = get_datetime_from_log(l)
			#endif
		#endfor
	#enddef

	def get_control_messages(self):
		log.log('get_control_messages function called')
		
		self.batch_count = 0
		self.message_count = 0
		self.messages_counter = {}
		message_list = []
		self.most_frequent = 'XXX'
		maximum = 0
		skip = datetime.datetime.now()
	
		messages = [' mimo ', 'limit', 'porucha', ' nen', 'nez']
		fn = 'control.log'

		if not isfile(fn):
			self.control[datetime.datetime.fromtimestamp(0)] = 'control.log not found'
			return
		#endif
		
		manual = False
		
		for l in give_lines(fn, 3):
			if '[C300]' in l or '[C301]' in l or '[C302]' in l: skip = get_datetime_from_log(l)
			
			if '[C315]' in l or '[C321]' in l: manual = False
			if '[C311]' in l or '[C313]' in l or '[C319]' in l: manual = True
				
			if 'p\xf8ijata' in l or 'prijat' in l: self.batch_count += 1
		
			for e in messages:
				if e in l.lower() and get_datetime_from_log(l) == skip and not manual:
					self.message_count += 1
					try: message_list.append(l.split('  ')[2].split('(')[0]) #this shit is because of old control
					except: message_list.append('unknown')
					#endtry
				#endif
			#endfor
		#endfor
		
		self.messages_counter = dict((i, message_list.count(i)) for i in message_list)
		self.messages_counter = sorted([(v, k) for (k, v) in self.messages_counter.items()])
		self.messages_counter.reverse()
	#enddef
	
	def get_control_errors(self):
		log.log('get_control_errors function called')
		
		self.control = {}
	
		errors = ['chyba', 'error', 'thread', 'bad', 'nelze', 'nenale', 'not found', 'malformed']
		fn = 'control.log'

		if not isfile(fn):
			self.control[datetime.datetime.fromtimestamp(0)] = 'control.log not found'
			return
		#endif
		
		for l in give_lines(fn, 3):
			for e in errors:
				if e in l.lower():
					if 'debug' in l.lower(): continue
					
					date = get_datetime_from_log(l)
							
					if self.now - date < datetime.timedelta(days = 30):
						self.control[date] = l.split('  ', 3)[2].strip()
					#endif
				#endif
			#endfor
		#endfor
	#enddef
	
	def get_unhandled_exeptions(self):
		log.log('get_unhandled_exceptions function called')
	
		log_files = []
		self.exceptions = []
	
		t2 = './temp/2'
		if os.path.isdir(t2): log_files = os.listdir(t2)

		t1 = './temp/1'
		if not os.path.isdir(t1): return
		for f in os.listdir(t1):
			if not f in log_files: log_files.append(f)
		#endfor
		
		#TOHLE REMOVNE NEJAKY SOUBORY z listu
		for x in ('control.log', 'recordedsignals.log'):
			try: log_files.remove(x)
			except: pass
		#endfor
		
		traceback_start = None
		exception = []
		
		for fn in log_files:				
			for line in give_lines(fn, 2):
				line = line.strip()
				
				#TODO this is because of old nsupdate and ipv6listen - vylepsit, az bude vsude opravena verze nsupdateu
				#try: date = datetime.datetime.strptime(line[0:18], '%Y-%m-%d %H:%M:%S')
				#except: pass

				if 'Traceback' in line:
					traceback_start = line.split('Traceback')[0]
				#endif
				
				#Vygrebne chybu
				if traceback_start:
					if line.startswith(traceback_start):
						exception.append(line[len(traceback_start):])
					else:
						self.exceptions.append((get_datetime_from_log(traceback_start), fn, exception))
						traceback_start = None
						exception = []
					#endif
				#endif
			#endfor
		#endfor
	#enddef
	
	def get_last_restart(self):
		log.log('get_last_restart function called')
		
		self.last_restart = None
		
		fn = 'loader.log'
	
		for l in give_lines(fn, 3):
			if 'reset mode' in l.lower(): self.last_restart = get_datetime_from_log(l)
		#endfor
	#enddef

	def get_unauthorized_operations(self):
		log.log('get_unauthorizes_operations function called')
	
		self.batches = {}
		self.unauthorized_operations = []
		self.authorized_operations = []
		
		d = {'.brq' : 'start', '.be2': 'end'}
		
		fill_analog = False
		
		manual_panel = False
		
		self.faulty_batches = []
		self.signalsrecorder = []
		
		fn = 'control.log'
		
		for l in give_lines(fn, 3):
			for k in d.keys():
				if k in l:
					try: date = get_datetime_from_log(l)
					except: continue
					#endtry

					if self.now - date > datetime.timedelta(60): continue
						
					batch = l.split(k)[0].split()[-1]
							
					if not batch in self.batches:
						self.batches[batch] = {}
					#endif
							
					self.batches[batch][d[k]] = date
				#endif
			#endfor
		#endfor

		for k in self.batches.keys():
			if len(self.batches[k]) < 2:
				log.log('found faulty batch: %s' % k)
				self.faulty_batches.append(k)
				del self.batches[k]
			#endif
		#endfor

		#for l in self.latest_logs:
			#os.system('7z e %s -o%s signalsrecorder.log' % (l, self.temp))
					
			#if not os.path.isfile('%s/signalsrecorder.log' % self.temp): continue
				
			#f = open('%s/signalsrecorder.log' % (self.temp), 'r')
						
			#for line in f.readlines():
				#if '*****' or 'Exiting' in line:
					#parse = line.split()
					#date = datetime.datetime.strptime(' '.join(parse[0:2]), '%Y-%m-%d %H:%M:%S:')
					#self.signalsrecorder.append(date)
				#endif
			#endfor
						
			#f.close()
					
			#if os.path.isdir(self.temp): shutil.rmtree(self.temp)
		#endfor
		
		fn = 'recordedsignals.log'

		for l in give_lines(fn, 3):
			if 'I_PC' in l:
				if fill_analog: #vymaze vse, kde neni scale
					if last: del self.authorized_operations[-1]
					else: del self.unauthorized_operations[-1]
					#endif
				#endif
					
				fill_analog = False
					
				manual_panel = False
					
				if '0' in l.split('=')[1]: manual_panel = True
			elif 'I_Bin1CEMclosed' in l or 'I_Bin2CEMclosed' in l:
			#nasledujici radka zneplatni pohyb kameniva
			#elif 'I_Bin1AGGclosed' in line or 'I_Bin1CEMclosed' in line or 'I_Bin2CEMclosed' in line or 'I_Lft1bottom' in line:
				if fill_analog: #vymaze vse, kde neni scale
					if last: del self.authorized_operations[-1]
					else: del self.unauthorized_operations[-1]
				#endif
				
				fill_analog = False
				
				date = get_datetime_from_log(l)
							
				if self.now - date > datetime.timedelta(60): continue
						
				matched = False
							
				material = 'cem'
				if 'I_Bin1AGGclosed' in l: material = 'agg'
				elif 'I_Lft1bottom' in l: material = 'agg-lift'

				for k in self.batches.keys():
					if date > self.batches[k]['start'] and date < self.batches[k]['end']:
						#log.log('matching %s to %s' % (date, k))
						matched = True
						break
					#endif
				#endfor
							
				#if not matched:
					#for x in self.signalsrecorder:
						#if (date >= x and date - x < datetime.timedelta(seconds=5)) or ((date < x and x - date < datetime.timedelta(seconds=5))):
							#matched = True
							#break
						#endif
					#endfor
				#endif
							
							
				if not matched:
					fill_analog = True
						
					if not manual_panel:
						self.authorized_operations.append('%s: %s, %s' % (date.strftime('%Y-%m-%d %H:%M:%S'), material, l.split('=')[1]))
						last = True
					else:
						self.unauthorized_operations.append('%s: %s, %s' % (date.strftime('%Y-%m-%d %H:%M:%S'), material, l.split('=')[1]))
						last = False
					#endif
				#endif
			elif 'Scale' in l:
				if fill_analog:
					date = get_datetime_from_log(l)
						
					sc = int(l.split('=')[1])
					if sc < 200:
						if not manual_panel:
							del self.authorized_operations[-1]
						else:
							del self.unauthorized_operations[-1]
						#endif
							
						fill_analog = False				
						continue
					#endif
						
					if not manual_panel:
						self.authorized_operations[-1] = '%s, %s' % (self.authorized_operations[-1], sc)
					else:
						self.unauthorized_operations[-1] = '%s, %s' % (self.unauthorized_operations[-1], sc)
					#endif
				#endif
					
				fill_analog = False						
			#endif
		#endfor
	#enddef

	def get_wiki_data(self):
		log.log('get_wiki_data function called')
		
		self.telephone = ''
		self.installation_date = ''
		self.warranty_date = ''
		self.gps = ''
		self.betonserver = ''
		self.contacts = ''

		for l in self.wiki_mj.split('\n'):
			l_orig = l.strip()
			l = l.lower().strip()
			
			if 'tel' in l and not self.telephone: 
				if "'''" in l: self.telephone = l.split("'''")[1]
			elif 'ruka do' in l and not self.warranty_date:
				try: self.warranty_date = datetime.datetime.strptime(l.split('do ')[-1].split()[0], '%d.%m.%Y')
				except: log.error('invalid warranty until format on wiki %s' % self.mj)
				#endtry
			elif 'nstalace:' in l and not self.installation_date:
				try: self.installation_date = datetime.datetime.strptime(l.split(': ')[-1].split()[0], '%d.%m.%Y')
				except: log.error('invalid installation date format on wiki %s' % self.mj)
				#endtry
			elif 'gps1' in l and not self.gps: self.gps = l.split(': ')[-1]
			elif 'betonserver' in l and not self.betonserver: self.betonserver = l.split('[[')[-1].split('|')[0]
			elif 'kontakty' in l and not self.contacts: self.contacts = l_orig.split('[[')[-1].split('|')[0]
		#endfor
	#enddef

	def get_hardware(self):
		log.log('get_hardware function called')
		
		self.motherboard = ''
		self.power_supply = ''
		self.communication = ''
		self.disk = ''
		self.operating_system = ''
		self.bios = ''
		self.testing_procedure = ''
		self.installation_procedure = ''

		for l in self.wiki_mj.split('\n'):
			l = l.lower()
		
			if 'cold lake' in l and not self.motherboard: self.motherboard = 'Cold Lake'
			elif 'nobletown' in l and not self.motherboard: self.motherboard = 'Nobletown'
			elif 'rogers city' in l and not self.motherboard: self.motherboard = 'Rogers City'
			elif 'avalon' in l and not self.motherboard: self.motherboard = 'Avalon'
			elif 'rocklake' in l and not self.motherboard: self.motherboard = 'Rock Lake'
			elif 'rock lake' in l and not self.motherboard: self.motherboard = 'Rock Lake'
			elif 'maryville' in l and not self.motherboard: self.motherboard = 'Maryville'
			elif 'garibaldi' in l and not self.motherboard: self.motherboard = 'Garibaldi'
			elif 'coolermaster 400w elite power' in l and not self.power_supply: self.power_supply = 'Coolermaster'
			elif 'corsair cx430' in l and not self.power_supply: self.power_supply = 'Corsiar'
			elif 'ide' in l and '80' in l and not self.disk: self.disk = '80GB IDE'
			elif 'sata' in l and '160' in l and not self.disk: self.disk = '160GB SATA'
			elif 'ssd' in l and '60' in l and not self.disk: self.disk = '60GB SSD'
			elif 'windows xp' in l:
				if not self.operating_system: self.operating_system = 'Windows XP'
				if not self.motherboard: self.motherboard = 'xxx'
				if not self.power_supply: self.power_supply = 'xxx'
			elif 'windows 7' in l:
				if not self.operating_system: self.operating_system = 'Windows 7'
				if not self.motherboard: self.motherboard = 'xxx'
				if not self.power_supply: self.power_supply = 'xxx'
			elif 'bios' in l and not self.bios: self.bios = l.split('||')[2]
			elif 'postup testov' in l and not self.testing_procedure: self.testing_procedure = l.split('||')[2]			
			elif 'postup instalace' in l and not self.installation_procedure: self.installation_procedure = l.split('||')[2]
			elif 'communication' in l and 'nif' in l and not self.communication: self.communication = 'NIF'
			elif 'communication' in l and 'net' in l and not self.communication: self.communication = 'NET'
			elif 'communication' in l and 'nut' in l and not self.communication: self.communication = 'NUT'
			elif 'communication' in l and 'sif' in l and not self.communication: self.communication = 'SIF'
			#endif
		#endfor
	#enddef
	
	def get_router_errors(self):
		log.log('get_router_errors function called')
		
		fn = 'router.log'

		date_start = None
		date_stop = None
		buffer_count = 0
		max_buffer_lenght = 0
		max_lastcontact = 0
		max_lastdata = 0
		last_lastcontact = 0
		last_lastdata = 0
		errors_in = None
		errors_out = None
		
		self.router = []
		
		for l in give_lines(fn, 3):
			if ('router' in l and 'starting' in l) or '- Start -' in l:
				date_start = get_datetime_from_log(l)
			elif not date_start:
				continue
			elif 'Counters cleared' in l:
				max_lastcontact = 0
				max_lastdata = 0
				last_lastcontact = 0
				last_lastdata = 0
			elif 'buffer length is ' in l:
				buffer_count += 1
				if max_buffer_lenght < int(l.split('buffer length is ')[1].strip()): max_buffer_lenght = int(l.split('buffer length is ')[1].strip())
			elif 'new lastcontact' in l:
				lastcontact = int(l.split('new lastcontact_max is ')[1].strip())

				if lastcontact > max_lastcontact and abs(lastcontact - last_lastcontact) > 20:
					max_lastcontact = lastcontact
				#endif
				last_lastcontact = lastcontact
			elif 'new lastdata' in l:
				lastdata = int(l.split('new lastdata_max is ')[1].strip())

				if lastdata > max_lastdata and abs(lastdata - last_lastdata) > 20:
					max_lastdata = lastdata
				#endif
				last_lastdata = lastdata				
			elif 'maximal LastContact' in l:
				lastcontact = int(l.split('maximal LastContact is ')[1].strip())
				lastdata = int(l.split('Maximal LastPacket is ')[1].split(',')[0].strip())
				
				if lastcontact > max_lastcontact and abs(lastcontact - last_lastcontact) > 20:
					max_lastcontact = lastcontact
				#endif
				last_lastcontact = lastcontact
				
				if lastdata > max_lastdata and abs(lastdata - last_lastdata) < 20:
					max_lastdata = lastdata
				#endif
				last_lastdata = lastdata				
			elif 'errors in' in l:
				date_stop = get_datetime_from_log(l)
				errors_in = int(l.split('errors in: ')[1].split(',')[0].strip())
				errors_out = int(l.split('errors out: ')[1].strip())
			elif 'Input errors' in l:
				date_stop = get_datetime_from_log(l)
				errors_in = int(l.split('Input errors: ')[1].split(',')[0].strip())
				errors_out = int(l.split('Output errors: ')[1].strip())
			elif 'Router.__del__' in l:
				date_stop = get_datetime_from_log(l)
			#endif
														
			if date_start and date_stop:
				self.router.append((date_start, date_stop, errors_in, errors_out, max_lastcontact, max_lastdata, buffer_count, max_buffer_lenght))			
					
				date_start = None
				date_stop = None
				buffer_count = 0
				max_buffer_lenght = 0
				max_lastcontact = 0
				max_lastdata = 0
				last_lastcontact = 0
				last_lastdata = 0
				errors_in = None
				errors_out = None
			#endif
		#endfor
	#enddef
#endclass
