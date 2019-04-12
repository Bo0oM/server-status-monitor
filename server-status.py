import sys,re,urllib2,sqlite3,urlparse,time

def insert(domain, vhost, client_ip, path):
	c.execute('''select vhost from log where vhost = ? and path = ?''', (vhost,path,))
	cnt=c.fetchall()
	if len(cnt)==0:
		critical = ['SESS','server', 'admin','log','sql','monitor','sess','token']
		if any(word in path for word in critical):
			critical=1
		else:
			critical=0
		c.execute('''INSERT INTO log(domain, critical, vhost, client_ip, path) values(?,?,?,?,?)''', (domain,critical,vhost,client_ip,path))
		conn.commit()
		#print '[!] Got data: Domain - '+domain+' - vhost - '+vhost+' - client - '+client_ip+' - path - '+path
	else:
		#print '[-] Duplicate Skipped!'
		return None;

def processing(target):
	req = urllib2.Request(target+'/server-status/', headers={ 'User-Agent': 'Mozilla/5.0', 'Accept-Charset': 'utf-8'})
	try:
		response = urllib2.urlopen(req)
		if response.code == 200:
			sstatus = response.read();
			info2 = re.compile('</td><td>(.*)</td><td nowrap>(.*)</td><td nowrap>GET (.*)</td></tr>')
			res2 = re.findall(info2, sstatus)
			#print len(res2)
			for line in res2:
				client = line[0]
				vhost = line[1]
				path = line[2]
				
				insert(target, vhost, client, path)
			c.execute('''select count(*) from log''')
			count=c.fetchall()
			print '[+] Proccessing end, current results:'+str(count[0])

		else:
			print '[-] Wrong Response code. Exit.'
	except urllib2.HTTPError, error:
		print '[-] failed. exit.'
		exit


if len(sys.argv)>1:
	print '- Monitoring - :'+sys.argv[1]
	conn = sqlite3.connect(urlparse.urlparse(sys.argv[1]).netloc+'.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS log(domain, critical integer, vhost, client_ip, path)''')
	print '[~] Database: '+urlparse.urlparse(sys.argv[1]).netloc+' Initialized'
	while True:
		processing(sys.argv[1])
		time.sleep(1)
else:
	print 'nope'
