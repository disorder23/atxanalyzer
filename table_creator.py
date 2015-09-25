#!/usr/bin/python2

from __future__ import division

__version__ = '0.0'

import os
import sys
import datetime
import urllib
from iniparser import IniParser
from plant import Plant

import log
sys.excepthook = log.log_exception

def create_tooltip(i):
	return '&#013;%s %s&#013;%s&#013;%s&#013;%s&#013;%s' % (i.mj, i.app_name, i.operating_system, i.motherboard, i.disk, i.communication)
#enddef

def generate_app_name(f, plants):
	f.write('<tr>\n')
	f.write('<th>aplikace</th>\n')
	for i in plants:
		style = ''
		
		if not i.app_name: style = ' class="grey"'
	 
		f.write('<td%s><b><a href=%s.htm>%s</a></b><br>%s</td>\n' % (style, i.mj, i.mj.upper(), i.app_name))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_links(f, plants):
	f.write('<tr>\n')
	f.write('<th>links</th>\n')
	for i in plants:
		f.write('<td><a href=%s.htm>analysis</a><br>\
		<a href=http://wiki.asterix.cz/moin/%s>wiki</a><br>\
		<a href=http://wiki.asterix.cz/moin/%s>contacts</a><br>\
		<a href=%s>betonserver</a><br>\
		<a href=http://mapy.cz/?%s>mapy.cz</a><br>\
		<a href=http://google.com/maps/?%s>maps.google.com</a><br>\
		tel: <b>%s</b>\
		</td>\n' % (i.mj, i.mj.upper(), i.contacts, i.betonserver, urllib.urlencode({'q': i.gps}), urllib.urlencode({'q': i.gps}), i.telephone))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_dates(f, plants):
	f.write('<tr>\n')
	f.write('<th>dates</th>\n')
	for i in plants:
		style = ''
		
		if not i.warranty_date or not i.installation_date: style = ' class="grey"'
	 
		f.write('<td%s>' % style)
		
		if i.warranty_date:
			f.write('Warranty until: %s<br>' % i.warranty_date.strftime('%d.%m.%Y'))
		#endif
		
		if i.installation_date:
			f.write('Installation date: %s<br>' % i.installation_date.strftime('%d.%m.%Y'))
		#endif
		
		f.write('</td>\n')
	#endfor
	f.write('</tr>\n')
#enddef

def generate_tasks(f, plants):
	#tasks
	f.write('<tr>\n')
	f.write('<th>Tasks</th>\n')
	for i in plants:
		tooltip = ' title = \'Tasks%s\'' % create_tooltip(i)

		style = ' class="green"'
		if i.tasks: style = ' class="yellow"'
		if i.important_task: style = ' class="pink"'

		f.write('<td%s%s>' % (tooltip, style))

		for task in i.tasks:
			f.write('%s<br>' % task)
		#endfor
		
		f.write('</td>\n')
	#endfor
	f.write('</tr>\n')
#enddef

def generate_motherboard(f, plants):
	f.write('<tr>\n')
	f.write('<th>Motherboard</th>\n')
	for i in plants:
		tooltip = ' title = \'Motherboard%s\'' % create_tooltip(i)

		style = ''
		
		if not i.motherboard or 'xxx' in i.motherboard: style = ' class="grey"'
		
		f.write('<td%s%s>%s</td>\n' % (tooltip, style, i.motherboard))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_bios(f, plants):
	f.write('<tr>\n')
	f.write('<th>Bios</th>\n')
	for i in plants:
		tooltip = ' title = \'Bios%s\'' % create_tooltip(i)
		
		style = ''
		
		if not i.bios: style = ' class="grey"'

		f.write('<td%s%s>%s</td>\n' % (tooltip, style, i.bios))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_testing_procedure(f, plants):
	f.write('<tr>\n')
	f.write('<th>Testing procedure</th>\n')
	for i in plants:
		tooltip = ' title = \'Testing procedure%s\'' % create_tooltip(i)

		style = ''
		
		if not i.testing_procedure: style = ' class="grey"'

		f.write('<td%s%s>%s</td>\n' % (tooltip, style, i.testing_procedure))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_power_supply(f, plants):
	f.write('<tr>\n')
	f.write('<th>Power Supply</th>\n')
	for i in plants:
		tooltip = ' title = \'Power Supply%s\'' % create_tooltip(i)

		style = ''
		
		if not i.power_supply or 'xxx' in i.power_supply: style = ' class="grey"'

		f.write('<td%s%s>%s</td>\n' % (tooltip, style, i.power_supply))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_disk(f, plants):
	f.write('<tr>\n')
	f.write('<th>Disk</th>\n')
	for i in plants:
		tooltip = ' title = \'Disk%s\'' % create_tooltip(i)

		style = ''
		
		if not i.disk: style = ' class="grey"'

		f.write('<td%s%s>%s</td>\n' % (tooltip, style, i.disk))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_operating_system(f, plants):
	f.write('<tr>\n')
	f.write('<th>OS</th>\n')
	for i in plants:
		tooltip = ' title = \'OS%s\'' % create_tooltip(i)

		style = ''
		
		if not i.operating_system: style = ' class="grey"'

		f.write('<td%s%s>%s</td>\n' % (tooltip, style, i.operating_system))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_installation_procedure(f, plants):
	f.write('<tr>\n')
	f.write('<th>Installation procedure</th>\n')
	for i in plants:
		tooltip = ' title = \'Installation procedure%s\'' % create_tooltip(i)

		style = ''
		
		if not i.installation_procedure: style = ' class="grey"'

		f.write('<td%s%s>%s</td>\n' % (tooltip, style, i.installation_procedure))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_communication(f, plants):
	f.write('<tr>\n')
	f.write('<th>Communication</th>\n')
	for i in plants:
		tooltip = ' title = \'Communication%s\'' % create_tooltip(i)
		
		style = ''
		
		if not i.communication: style = ' class="grey"'

		f.write('<td%s%s>%s</td>\n' % (tooltip, style, i.communication))
	#endfor
	f.write('</tr>\n')
#enddef
	
def generate_structure(f, plants):
	f.write('<tr>\n')
	f.write('<th>Structure</th>\n')
	for i in plants:
		tooltip = ' title = \'Structure%s\'' % create_tooltip(i)
		
		style = ''
		
		if not i.structure: style = ' class="pink"'

		f.write('<td%s%s>' % (tooltip, style))
	
		for x, y in i.structure:
			f.write('%s: %s<br>' %(x, y))
		#endfor
				
		f.write('</td>\n')
	#endfor
	f.write('</tr>\n')
#enddef

def generate_lan_settings(f, plants):
	f.write('<tr>\n')
	f.write('<th>LAN settings</th>\n')
	for i in plants:
		tooltip = ' title = \'LAN settings%s\'' % create_tooltip(i)
		
		style = ''
		
		if not i.lan_adapters or not i.lan_name:
			style = ' class="pink"'
		#endif

		f.write('<td%s%s>' % (tooltip, style))
		
		if not i.lan_adapters or not i.lan_name:
			f.write('</td>\n')
			continue
		#endif
	
		f.write('<b>name</b>: %s<br><b>domain</b>: %s<br>' % (i.lan_name, i.lan_domain))
	
		for x in i.lan_adapters:
			f.write('<br><b>%s</b>:' % x.adapter)
			
			if x.dhcp: f.write(' DHCP')
			
			f.write('<br>')
			
			a = x.address
			if a: f.write('address: %s<br>' % a)
			
			a = x.subnet
			if a: f.write('subnet: %s<br>' % a)
			
			a = x.gateway
			if a: f.write('gateway: %s<br>' % a)
			
			a = x.dns
			if a: f.write('dns:')
			for d in a:
				f.write(' %s<br>' % d)
			#endfor
			
			a = x.wins1
			if a: f.write('wins1: %s<br>' % a)
			
			a = x.wins2
			if a: f.write('wins2: %s<br>' % a)
		#endfor
				
		f.write('</td>\n')
	#endfor
	f.write('</tr>\n')
#enddef

def generate_coefficients(f, plants):
	f.write('<tr>\n')
	f.write('<th>Coefficients</th>\n')
	for i in plants:
		tooltip = ' title = \'Coefficients%s\'' % create_tooltip(i)
		
		style = ''
		
		maximal = 0
		
		if not i.coefficients: style = ' class="pink"'
		
		for x in i.coefficients:
			if abs(i.coefficients[x][1]) > maximal: maximal = abs(i.coefficients[x][1])
		#endfor

		if maximal > 5: style = ' class="pink"'
		elif maximal > 1: style = ' class="yellow"'

		f.write('<td%s%s>' % (tooltip, style))
	
		for x in sorted(i.coefficients):
			log.info('%s' % i.mj)
			log.info('%s' % i.coefficients)
			log.info('%s' % x)
			f.write('<b>%s</b>: difference: %.2f%%, capacity: %i, offset: %i<br>' %(x, i.coefficients[x][1], i.coefficients[x][0], i.coefficients[x][2]))
		#endfor
				
		f.write('</td>\n')
	#endfor
	f.write('</tr>\n')
#enddef

def generate_ports(f, plants):
	f.write('<tr>\n')
	f.write('<th>Ports</th>\n')
	for i in plants:
		tooltip = ' title = \'Ports%s\'' % create_tooltip(i)
		
		style = ''
		
		maximal = 0
		
		if not i.ports or not '5900' in i.ports: style = ' class="pink"'
		elif len(i.ports) == 3: style = ' class="green"'
		else: style = ' class="yellow"'
		

		f.write('<td%s%s>%s</td>\n' % (tooltip, style, i.ports))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_last_state(f, plants):
	f.write('<tr>\n')
	f.write('<th>Last state</th>\n')
	for i in plants:
		tooltip = ' title = \'Last state%s\'' % create_tooltip(i)
		
		style = ''
		
		maximal = 0
		
		f.write('<td%s%s>%s</td>\n' % (tooltip, style, i.last_state))
	#endfor
	f.write('</tr>\n')
#enddef
	
def generate_last_restart(f, plants):
	f.write('<tr>\n')
	f.write('<th>Last restart</th>\n')
	for i in plants:
		tooltip = ' title = \'Last restart%s\'' % create_tooltip(i)
		
		style = ' class="pink"'
		
		now = datetime.datetime.now()
		t = i.last_restart
		
		if not t: t = datetime.datetime(1970, 12, 30)
		
		if t.year == 1970: style = ' class="red"'

		if now - t < datetime.timedelta(20) or i.operating_system == 'Windows 7':
			style = ' class="green"'
		elif now - t < datetime.timedelta(30):			
			style = ' class="yellow"'
		#endif
		
		f.write('<td%s%s>%s</td>\n' % (tooltip, style, t.strftime('%Y-%m-%d %H:%M:%S')))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_current_month_log(f, plants):
	f.write('<tr>\n')
	f.write('<th>Current month log</th>\n')
	for i in plants:
		tooltip = ' title = \'Current month log%s\'' % create_tooltip(i)
		
		style = ' class="pink"'
		
		now = datetime.datetime.now()
		
		if i.latest_log: latest_log = i.latest_log.split('log_')[1].split('.')[0]
		else:
			latest_log = ''
			style = ' class="red"'
		#endif
		
		if latest_log.startswith('%s' % now.year) and latest_log.endswith('%s' % now.month): style = ' class="green"'
		
		f.write('<td%s%s>%s</td>\n' % (tooltip, style, latest_log))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_sizes(f, plants):
	f.write('<tr>\n')
	f.write('<th>Sizes</th>\n')
	for i in plants:
		tooltip = ' title = \'Sizes%s\'' % create_tooltip(i)
		
		style = ' class="pink"'
		
		now = datetime.datetime.now()
		t = datetime.datetime.fromtimestamp(float(i.sizes['created']))
		
		if t.year == 1970: style = ' class="red"'

		if now - t < datetime.timedelta(7) and i.sizes['files'] < 4000 and i.sizes['size'] < 1000000000:
			style = ' class="green"'
		elif now - t < datetime.timedelta(30) and i.sizes['files'] < 4000 and i.sizes['size'] < 1000000000:
			style = ' class="yellow"'
		#endif
		
		f.write('<td%s%s>created: %s<br>files: %i<br>size: %0.2f MB</td>\n' % (tooltip, style, t.strftime('%Y-%m-%d %H:%M:%S'), i.sizes['files'], i.sizes['size']/1000000))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_versions_created(f, plants):
	f.write('<tr>\n')
	f.write('<th>Versions file created</th>\n')
	for i in plants:
		tooltip = ' title = \'Versions file created%s\'' % create_tooltip(i)

		style = ' class="pink"'
		
		now = datetime.datetime.now()
		t = datetime.datetime.fromtimestamp(float(i.versions_created))
		
		if t.year == 1970: style = ' class="red"'

		if now - t < datetime.timedelta(7):
			style = ' class="green"'
		elif now - t < datetime.timedelta(30):			
			style = ' class="yellow"'
		#endif
		
		f.write('<td%s%s>%s</td>\n' % (tooltip, style, t.strftime('%Y-%m-%d %H:%M:%S')))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_versions(f, plants):
	v = IniParser()
	v.read('versions.ini')
	for app in v.sections():
		f.write('<tr>\n')
		f.write('<th>%s</th>\n' % app)
		for i in plants:
			tooltip = ' title = \'%s%s\'' % (app, create_tooltip(i))
		
			o = ('', '')

			if app in i.versions: o = i.versions[app]
			
			ver = o[0]
			hash = o[1]
			current = v.get(app, 'current').split(',' ' ')
			testing = v.get(app, 'testing').split(',' ' ')
			
			if ver in current: style = ' class="green"'
			elif ver in testing: style = ' class="yellow"'
			else: style = ' class="pink"'
			#endif
			
			if hash != v.get(app, 'v%s' % ver): style = ' class="red"'

			if not hash and not ver: style = ' class="grey"'		
		
			f.write('<td%s%s>%s</td>\n' % (tooltip, style, ver))
		#endfor
		f.write('</tr>\n')
	#endfor
#enddef

def generate_router_log(f, plants):
	f.write('<tr>\n')
	f.write('<th>Router errors</th>\n')
	for i in plants:
		tooltip = ' title = \'Router errors%s\'' % create_tooltip(i)
		
		style = ' class="red"'
		
		now = datetime.datetime.now()
		
		intervals = (30, 60, 90)
		
		x_last = 0

		for x in intervals:
			days = {}
			av_ein = {}
			av_eout = {}
			av_bl = {}
			fmt_av_ein = {}
			fmt_av_eout = {}
			fmt_av_bl = {}
			
			days[x] = [datetime.timedelta(0), 0, 0, 0, 0, 0, 0, 0, 0, 0, [], []]
			
			for start, stop, ein, eout, mc, md, bl, max_bl in i.router:
				if now - start < datetime.timedelta(x) and now - start > datetime.timedelta(x_last):
					if (ein or ein == 0) and (eout or eout == 0):
						days[x][0] += stop - start
						days[x][1] += ein
						days[x][2] += eout
						days[x][5] += bl
						days[x][3] += mc
						days[x][4] += md
						if days[x][6] < max_bl: days[x][6] = max_bl
					#endif
					
					if mc > days[x][9]: days[x][9] = mc
					
					if mc > 1000:
						days[x][8] += 1
						days[x][10].append(stop.strftime('%Y-%m-%d %H:%M:%S'))
					#endif
				
					days[x][7] += 1
					days[x][11].append(start.strftime('%Y-%m-%d %H:%M:%S'))
				#endif
			#endfor
			
			try:
				av_ein[x] = days[x][1] * 3600 / days[x][0].total_seconds()
				fmt_av_ein[x] = '%.1f' % av_ein[x]
			except:
				fmt_av_ein[x] = 'N/A'
				av_ein[x] = 'N/A'
			#endtry
		
			try:
				av_eout[x] = days[x][2] * 3600 / days[x][0].total_seconds()
				fmt_av_eout[x] = '%.1f' % av_eout[x]
			except:
				fmt_av_eout[x] = 'N/A'
				av_eout[x] = 'N/A'
			#endtry

			if days[x][3] == 0: days[x][3] = 'N/A'
			if days[x][4] == 0: days[x][4] = 'N/A'
			
			try:
				av_bl[x] = days[x][5] * 3600 / days[x][0].total_seconds()
				fmt_av_bl[x] = '%.1f' % av_bl[x]
			except:
				fmt_av_bl[x] = 'N/A'
				av_bl[x] = 'N/A'
			#endtry
			

			if x_last == 0:
				if av_ein[x] < 5 and av_eout[x] < 5 and days[x][9] < 500: #and av_bl[x] < 5 and days[x][6] < 500:
					style = ' class="green"'
				elif av_ein[x] < 10 and av_eout[x] < 10 and days[x][9] < 750: #and av_bl[x] < 10 and days[x][6] < 750:
					style = ' class="yellow"'
				elif av_ein[x] < 20 and av_eout[x] < 20 and days[x][9] < 1000: #and av_bl[x] < 15 and days[x][6] < 1000:
					style = ' class="pink"'
				#endif		
				
				f.write('<td%s%s>' % (tooltip, style))
			#endif
		
			if days[x][3] == 'N/A': days[x][3] = 0
			if days[x][4] == 'N/A': days[x][4] = 0
			if days[x][7] == 0: days[x][7] = 1
			d = {}
			d[x] = 'in/h: %s, out/h: %s, mc: %s, bl/h: %s, m_bl: %s, start: <a title=\"%s\">%s</a>, timeout: <a title=\"%s\">%s</a>, av_mc/run = %.1f, av_md/run = %.1f' % (fmt_av_ein[x], fmt_av_eout[x], days[x][9], fmt_av_bl[x], days[x][6], days[x][11], days[x][7], days[x][10], days[x][8], days[x][3]/days[x][7], days[x][4]/days[x][7])

			f.write('days %s: %s<br>' % (x, d[x]))
			
			x_last = x
		#endfor
		f.write('</td>\n')
	#endfor
	f.write('</tr>\n')
#enddef

def generate_io_communication_failures(f, plants):
	f.write('<tr>\n')
	f.write('<th>I/O communication failures</th>\n')
	for i in plants:
		tooltip = ' title = \'I/O communication failures%s\'' % create_tooltip(i)

		
		if not i.io_communication_failures:
			style = ' class="green"'
			f.write('<td%s%s>' % (tooltip, style))
			f.write('</td>\n')
			continue
		#endif
		
		style = ' class="yellow"'
		
		f.write('<td%s%s>' % (tooltip, style))
		
		for k in sorted(i.io_communication_failures):
			f.write('%s: %i occurences<br>' %(k, len(i.io_communication_failures[k])))
			for t in i.io_communication_failures[k]:
				f.write('%s<br>' % t)
			#endfor
		#endfor
		
		f.write('</td>\n')
	#endfor
	f.write('</tr>\n')
#enddef

def generate_smart(f, plants):
	f.write('<tr>\n')
	f.write('<th>S.M.A.R.T</th>\n')
	for i in plants:
		tooltip = ' title = \'S.M.A.R.T%s\'' % create_tooltip(i)

		style = ' class="red"'
		
		now = datetime.datetime.now()
		t = datetime.datetime.fromtimestamp(float(i.smart_created))

		if len(i.smart_faults) != 0:
			style = ' class="red"'
		elif i.mj in ('mj04', 'mj18', 'mj22', 'mj36', 'mj48'):
			style = ' class="green"'			
		elif i.smart_supported and (i.power_on_hours - i.last_short > 168 or i.power_on_hours - i.last_long > 744 or not i.power_on_hours or not i.last_short or not i.last_long):
			style = ' class="yellow"'
		elif i.count_of_smart_attributes != 0 and now - t < datetime.timedelta(7) and len(i.smart_faults) == 0:
			style = ' class="green"'
		#endif
		
		f.write('<td%s%s>created: %s<br>' % (tooltip, style, t.strftime('%Y-%m-%d %H:%M:%S')))
		
		f.write('<div title=\'')
		for e in i.smart_log:
			f.write('%s&#013;' % e)
		#endfor
		f.write('\'>')
		
		f.write('count of smart attributes: %i<br>smart faults: %s<br>last short: %i h ago<br>last long: %i h ago</div></td>\n' % (i.count_of_smart_attributes, i.smart_faults, i.power_on_hours - i.last_short, i.power_on_hours - i.last_long))
	#endfor
	f.write('</tr>\n')
#enddef
	
def generate_cpu_usage(f, plants):
	f.write('<tr>\n')
	f.write('<th>Cpu usage</th>\n')
	for i in plants:
		tooltip = ' title = \'Cpu usage%s\'' % create_tooltip(i)

		style = ' class="green"'
		
		now = datetime.datetime.now()
		
		list_keys = sorted(i.cpu_usage.keys())
		list_keys.reverse()
		
		cpu = {}
		counter = 1
		
		for k in list_keys:
			if now - k > datetime.timedelta(days=30): continue
		
			v = i.cpu_usage[k]

			for p, u in v:
				if len(v) == 1: p = 'cpu_solo'
							
				if not p in cpu: cpu[p] = [0, 0, 0, 0] #usage, count, max, date
				
				cpu[p][0] += u
				cpu[p][1] += 1
				if u >= cpu[p][2]: 
					cpu[p][2] = u
					cpu[p][3] = k
				#endif
			#endfor
			
			if counter == 20: break
			
			if len(v) > 1: counter += 1
		#endfor

		for p in cpu.keys():
			avg = cpu[p][0]/cpu[p][1]
			if avg > 10:
				style = ' class="pink"'
				break
			elif cpu[p][2] > 20 or avg > 5: style = ' class="yellow"'
			#endif
		#endfor
		
		if len(cpu.keys()) == 0: style = ' class="pink"'
		
		f.write('<td%s%s>watched processes: %i<br>' % (tooltip, style, len(cpu.keys())))
					
		for p in sorted(cpu.keys()):
			avg = cpu[p][0]/cpu[p][1]
			
			if 'cpu' in p or 'atx' in p:
				if avg > 10 or cpu[p][2] > 30:
					f.write('* %s: %0.1f (%0.1f max, %s)<br>' % (p, avg, cpu[p][2], cpu[p][3].strftime('%Y-%m-%d %H:%M:%S')))
				else:
					f.write('* %s: %0.1f<br>' % (p, avg))
				#endif
			elif avg > 5 or cpu[p][2] > 20: 
				f.write('* %s: %0.1f (%0.1f max, %s)<br>' % (p, avg, cpu[p][2], cpu[p][3].strftime('%Y-%m-%d %H:%M:%S')))
			#endif
		#endfor
		f.write('</td>\n')
	#endfor
	f.write('</tr>\n')
#enddef

def generate_libsh_log(f, plants):
	f.write('<tr>\n')
	f.write('<th>Libsh.log</th>\n')
	for i in plants:
		tooltip = ' title = \'Libsh.log%s\'' % create_tooltip(i)

		style = ' class="green"'

		if i.libsh:
			style = ' class="pink"'
		
			for k in i.libsh.keys():
				t = datetime.datetime.fromtimestamp(float(k))
				v = i.libsh[k]
			#endfor
			
			f.write('<td%s%s>error variable: %s (%s)</td>\n' % (tooltip, style, v, t.strftime('%Y-%m-%d')))
		else: f.write('<td%s%s></td>\n' % (tooltip, style, ))
		#endif
	#endfor
	f.write('</tr>\n')
#enddef

def generate_control_log(f, plants):
	f.write('<tr>\n')
	f.write('<th>Control.log</th>\n')
	for i in plants:
		tooltip = ' title = \'Control.log%s\'' % create_tooltip(i)

		style = ' class="green"'

		if i.control:
			style = ' class="pink"'

			f.write('<td%s%s>' % (tooltip, style))
			
			for k in i.control.keys():
				t = k
				e = i.control[k]
				
				f.write('%s: %s<br>' % (t.strftime('%Y-%m-%d %H:%M:%S'), e))
			#endfor
			
			f.write('</td>\n')
		else: f.write('<td%s%s></td>\n' % (tooltip, style, ))
		#endif
	#endfor
	f.write('</tr>\n')
#enddef
	
def generate_control_messages(f, plants):
	f.write('<tr>\n')
	f.write('<th>Control messages</th>\n')
	for i in plants:
		tooltip = ' title = \'Control messages%s\'' % create_tooltip(i)

		style = ' class="green"'
		
		division = 0
		if i.batch_count != 0:
			division = i.message_count/i.batch_count
		#endif

		if i.batch_count == 0 or division > 1:
			style = ' class="pink"'
		elif division > 0.3:
			style = ' class="yellow"'
			
		f.write('<td%s%s>batch count: %i<br>messages per batch: %0.2f<br>frequency: %s</td>' % (tooltip, style, i.batch_count, division, i.messages_counter))
	#endfor
	f.write('</tr>\n')
#enddef

def generate_adaptivity(f, plants):
	f.write('<tr>\n')
	f.write('<th>Adaptivity</th>\n')
	for i in plants:
		tooltip = ' title = \'Adaptivity%s\'' % create_tooltip(i)
		style = ''
		
		f.write('<td%s%s>' % (tooltip, style))
		
		for silo in sorted(i.adaptivity):
			text = silo
			if silo in i.materials_assignment:
				text = '%s (%s)' % (silo, i.materials_assignment[silo])
			#endif
			f.write('<a href="%s%s.csv">%s<br>' % (i.mj, silo, text))
		#endfor
		
		f.write('</td>')	
	#endfor
	f.write('</tr>\n')
#enddef

def generate_aggregate_close_times(f, plants):
	f.write('<tr>\n')
	f.write('<th>Aggregate close times</th>\n')
	for i in plants:
		tooltip = ' title = \'Aggregate close times%s\'' % create_tooltip(i)
		style = ' class="green"'
		
		if not i.close_times: style = ' class="red"'
		
		text = 'last ten weighing:<br>'
		
		#last ten weighing
		for agg in i.close_times:
			detail = []
			counter = 0
			sum = 0
			sqr_sum = 0
			
			for a, t1, t2 in i.close_times[agg][-10:]:
				a = a.total_seconds()
				counter += 1
				sum += a
				detail.append((a, t1.strftime('%Y-%m-%d %H:%M:%S'), t2.strftime('%Y-%m-%d %H:%M:%S')))
			#endfor
			
			if counter == 0: counter = 1
			avg = sum/counter
			
			for a, t1, t2 in i.close_times[agg][-10:]:
				a = a.total_seconds()
				sqr_sum += ((a - avg) ** 2) / counter
			#endfor
			
			dev = sqr_sum ** 0.5
			
			if dev > avg * 0.2: style = ' class="pink"'
			elif dev > avg * 0.1: style = ' class="yellow"'
			#endif	
			
			text = '%sAGG%s: <a title=\"%s">%0.3f</a> (odhchylka: %0.3f)<br>' % (text, agg, detail, avg, dev)
		#endfor
		
		text = '%sall weighing:<br>' % text
		
		#all weighing
		for agg in i.close_times:
			counter = 0
			sum = 0
			sqr_sum = 0
			
			for a, t1, t2 in i.close_times[agg]:
				a = a.total_seconds()
				counter += 1
				sum += a
			#endfor
			
			if counter == 0: counter = 1
			avg = sum/counter
			
			for a, t1, t2 in i.close_times[agg]:
				a = a.total_seconds()
				sqr_sum += ((a - avg) ** 2) / counter
			#endfor
			
			dev = sqr_sum ** 0.5
			
			text = '%sAGG%s: %0.3f (odhchylka: %0.3f)<br>' % (text, agg, avg, dev)
		#endfor
		
		f.write('<td%s%s>%s</td>' % (tooltip, style, text))	
	#endfor
	f.write('</tr>\n')
#enddef

def generate_unhandled_exceptions(f, plants):
	f.write('<tr>\n')
	f.write('<th>Unhandled exceptions</th>\n')
	for i in plants:
		tooltip = ' title = \'Unhandled exceptions%s\'' % create_tooltip(i)

		created = False
		style = ' class="green"'
		
		now = datetime.datetime.now()
		
		if i.exceptions:
			for d, fn, ex in i.exceptions:
				if now - d < datetime.timedelta(30) or d == datetime.datetime.fromtimestamp(0):
					style = ' class="pink"'
				
					if not created:
						f.write('<td%s%s>' % (tooltip, style))
						created = True
					#endif
					
					f.write('<div title=\'')
					for e in ex:
						f.write('%s&#013;' % e)
					#endfor
					f.write('\'>')
					
					f.write('%s: %s</div>' % (fn, d.strftime('%Y-%m-%d %H:%M:%S')))
				#endif
			#endfor
		#endif
		if not created: f.write('<td%s>' % style)
		
		f.write('</td>')
	#endfor
	f.write('</tr>\n')
#enddef

def generate_ini_created(f, plants):
	f.write('<tr>\n')
	f.write('<th>Ini zip created</th>\n')
	for i in plants:
		tooltip = ' title = \'Ini zip created%s\'' % create_tooltip(i)
		
		style = ' class="pink"'
		
		now = datetime.datetime.now()
		t = datetime.datetime.fromtimestamp(float(i.ini_created))
		
		if t.year == 1970: style = ' class="red"'

		if now - t < datetime.timedelta(7):
			style = ' class="green"'
		elif now - t < datetime.timedelta(30):			
			style = ' class="yellow"'
		#endif
		
		f.write('<td%s%s>%s</td>\n' % (tooltip, style, t.strftime('%Y-%m-%d %H:%M:%S')))
	#endfor
	f.write('</tr>\n')
#enddef

def	generate_ini_hashes(f, plants):
	h = IniParser()
	h.read('hashes.ini')
	for ini in h.sections():
		f.write('<tr>\n')
		f.write('<th>%s</th>\n' % ini)
		for i in plants:
			tooltip = ' title = \'%s%s\'' % (ini, create_tooltip(i))

			if ini in i.ini_hashes:
				hash = 'h%s' % i.ini_hashes[ini]		
		
				style = ' class="pink"'
			
				if h.has_option(ini, hash):
					val = h.get(ini, hash)
					app = val.split(':')[0]
					
					if (h.get(ini, hash) == '' or (app in i.versions and i.versions[app][0] in h.get(ini, hash))) \
					and (not h.has_option(ini, '%s_motherboard' % hash) or i.motherboard in h.get(ini, '%s_motherboard' % hash)):
						style = ' class="green"'

						if h.has_option(ini, '%s_message' % hash): hash = h.get(ini, '%s_message' % hash)
						else: hash = ''
					else:
						style = ' class="yellow"'
					#endif
				#endif
			else:
				hash = ''
				style = ' class="grey"'
			#endif		
		
			f.write('<td%s%s>%s</td>\n' % (tooltip, style, hash))
		#endfor
		f.write('</tr>\n')
	#endfor
#enddef

def generate_unauthorized_operations(f, plants):
	f.write('<tr>\n')
	f.write('<th>Unauthorized operations</th>\n')
	for i in plants:
		tooltip = ' title = \'Unauthorized operations%s\'' % create_tooltip(i)

		style = ''
		f.write('<td%s%s>' % (tooltip, style))
		
		f.write('unauthorized:<br>')		
		for x in i.unauthorized_operations:
			f.write('%s<br>' % (x))
		#endfor
		
		f.write('authorized:<br>')
		for x in i.authorized_operations:
			f.write('%s<br>' % (x))
		#endfor
		
		f.write('faulty batches:<br>')
		for x in i.faulty_batches:
			f.write('%s<br>' % (x))
		#endfor

		f.write('</td>\n')
	#endfor
#enddef

def generate_little_amounts(f, plants):
	f.write('<tr>\n')
	f.write('<th>Little amounts</th>\n')
	for i in plants:
		tooltip = ' title = \'Little amounts%s\'' % create_tooltip(i)

		style = ''
		
		
		
		#f.write('<td%s%s>' % (tooltip, style))
		line = ''
		
		for k in i.silo:
			offset, velocity, n, dev, param_velocity, param_offset = i.silo[k]
			
			if n <= 1: continue
			
			if abs(param_velocity - velocity) > 10 or abs(param_offset - offset) > 0.05: style = ' class="yellow"'
			
			line += 'silo: %s, offset: %s (%s), velocity: %s (%s), smerodatna odchylka: %0.2f, pocet mereni: %s<br>' % (k, param_offset, offset, param_velocity, velocity, dev, n)		
		#endfor
		
		if i.little_amounts_fails: style = ' class="yellow"'

		if i.little_amounts_error: style = ' class="pink"'
		
		f.write('<td%s%s>' % (tooltip, style))
		f.write('%s' % line)
		
		if i.little_amounts_fails: f.write('<br>weighing fails {silo: [navazeno, doba]} %s' % i.little_amounts_fails)
		
		f.write('</td>\n')
	#endfor
#enddef

def create_table(plants):
	a = '../public_html_incoming'
	if not os.path.isdir(a):
		a = './public_html_incoming'
	#endif

	if len(plants) != 1:
		f = open('%s/table.htm' % a, 'w')
	else:
		f = open('%s/%s.htm' % (a,plants[0].mj), 'w')
	#endif

	f.write('<HEAD><meta http-equiv="Content-Type" content="text/html;charset=utf-8"><TITLE>Table of applications</TITLE><LINK rel=\'StyleSheet\' href=\'table.css\' type=\'text/css\' media=\'all\'></HEAD>')
	f.write('<body>\n')
	
	f.write('<h1><a href=table.htm>Table of applications</a></h1>\n')
	
	now = datetime.datetime.now()
	now = now.strftime('%Y-%m-%d %H:%M:%S')
	
	f.write('<p>created: %s</p>\n' % now)

	f.write('<p>legend:<br>green = OK<br>yellow = notice/testing version<br>pink = warning/old version<br>red = error<br>grey = N/A</p>\n')

	f.write('<table>\n')

	generate_app_name(f, plants)
	generate_links(f, plants)
	generate_dates(f, plants)
	generate_tasks(f, plants)
	generate_motherboard(f, plants)
	generate_bios(f, plants)
	generate_testing_procedure(f, plants)
	generate_power_supply(f, plants)
	generate_disk(f, plants)
	generate_operating_system(f, plants)
	generate_installation_procedure(f, plants)
	generate_communication(f, plants)
	generate_lan_settings(f, plants)
	generate_ports(f, plants)
	generate_structure(f, plants)
	generate_coefficients(f, plants)
	generate_little_amounts(f, plants)
	generate_last_state(f, plants)
	generate_last_restart(f, plants)
	generate_current_month_log(f, plants)
	generate_sizes(f, plants)
	generate_versions_created(f, plants)
	generate_versions(f, plants)
	generate_router_log(f, plants)
	generate_io_communication_failures(f, plants)
	generate_smart(f, plants)
	generate_cpu_usage(f, plants)
	generate_libsh_log(f, plants)
	generate_control_log(f, plants)
	generate_control_messages(f, plants)
	generate_adaptivity(f, plants)
	generate_aggregate_close_times(f, plants)
	generate_unhandled_exceptions(f, plants)
	generate_ini_created(f, plants)
	generate_ini_hashes(f, plants)
	#generate_unauthorized_operations(f, plants)
	
	f.write('</tr>\n')
	
	f.write('</table>\n')

	f.write('</body>\n')
	
	f.close()
#enddef

def main():
	#TODO: analyza dalsich logu
	
	log.filename = 'table_creator.log'

	plants = []

	mj_list = []
	
	a = '../../incoming/'
	if not os.path.isdir(a):
		a = './incoming'
	#endif
	
	for d in os.listdir(a):
		if os.path.isdir('%s/%s' % (a,d)) and d.startswith('mj') and not(d.endswith('d')):
			try: mj_list.append(int(d[2:]))
			except: pass
		#endif
	#endfor
	mj_list.sort()
	mj_list.reverse()

	for i in mj_list:
		x = Plant('mj%02i' % i)
		x.process()
			
		plants.append(x)
	#endfor
	
	create_table(plants)
	
	for i in plants:
		i = [i]
		create_table(i)
	#endfor
#enddef

if __name__ == '__main__': main()
