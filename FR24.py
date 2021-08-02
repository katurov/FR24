'''
THE IDEA
	FR24 gives pretty nice service (on "business" level) if you build your own point for 'em. It is simple and easy, any
	can do it with the instruction from FR24. Hardware for this build is under $100, and it uses just about 20W/h, so
	this won't make you broke. 

	FR24 have its "gray points":
	1. They won't tell you to prepare your antenna (one with your SDR isn't good enough)
	2. They won't give you a history of planes traveled through "your controlled space" (but you can see "playback" on FR24 site)

	As far as I looked for small planes, which aren't present in "playback" on FR24, I need to see and watch the web-console 
	of my FR24 point to see hex-id,filter 'em by myself and don't blink. And so I did it to find 4C0DA1 (Piper PA-38-112 Tomahawk)
	but "sit here and don't blink" is bad varian for me as I have work and need to sleep a bit each day.

	I'm thinking: what is something will "sit here and won't blink" 24/7 and write 'em all down to the list for me, so I'll able
	to check records in any time? This is the script.


BASED ON:
	1. https://gist.github.com/msakai/3318776 -- this helps me to understand the sentence of the JSON pulled from FR24 
	2. https://github.com/exxamalte/python-flightradar-client -- this opens me an idea to start

	I would like to thans 'em for the ideas. Thank you guys!

INFO:
	1. HEX to human and be found here: https://www.planespotters.net/search?q=06A10C
	2. Script use pooling to mySQL 'cause it can reconnect by itself (hope so)
	3. Script works "here and now", so it cat lost some values and this is "ok" for my case
	4. Terms:
		4.1. SQW stands for "squawk" which you may know as "transponder": "channel" of plane's radio
		4.2. FLIGHT stands for "call sign": https://www.flightradar24.com/blog/clearing-up-call-sign-confusion/

HARDWARE UNDER THE BUILD:
	1. Raspberry Pi 2
	2. Some suitable SDR (I really cannot remember which one)
	3. An antenna done in some way like: https://discussions.flightaware.com/t/three-easy-diy-antennas-for-beginners/16348
		personally I've made a "pepsy can"
	4. Home server (mine: old laptop under debian)
	5. Network with internet access, common for FR24 and Server (or they can access in some way to each other)

PRECONDITIONS:
	1. You have done with the installation of own FlightRadar point and it is fully functional
	2. You know IP address of your install. In my case it is 192.168.0.40
	3. You have a dedicated server for script (python3 + mySQL)

EXAMPLES AND HOWTOS:

	THIS is how I found the way to get JSON with currently presented crafts. It was interrested to understand that 'time=EPOCH' is
	used just to reject browser' caching algorithms. But it looks like you should use EPOCH with millis to make URL functional. 
	Other headers are from my Safari and just are for "anycase".

	Please, change IP address of FR24 point not only in URL, but in headers

		curl 'http://192.168.0.40:8754/flights.json?time=1627592900630' 
			-X 'GET' 
			-H 'Accept: application/json, text/javascript, */*; q=01' 
			-H 'Accept-Language: en-gb' 
			-H 'Host: 192.168.0.40:8754' 
			-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15' 
			-H 'Referer: http://192.168.0.40:8754/tracked.html' 
			-H 'Accept-Encoding: gzip, deflate' 
			-H 'Connection: keep-alive' 
			-H 'X-Requested-With: XMLHttpRequest'


	THIS is the settings for mySQL database and user, please, change password for something. NB: localhost is for security.
	You also can use any database on your server, but change settings in connection in script. 

		Server version: 8.0.25 MySQL Community Server - GPL

		mysql> CREATE USER 'fr24'@'localhost' IDENTIFIED BY 'password';
		Query OK, 0 rows affected (0,06 sec)

		mysql> CREATE DATABASE fr24;
		Query OK, 1 row affected (0,02 sec)

		mysql> GRANT ALL PRIVILEGES ON fr24 . * TO 'fr24'@'localhost';
		Query OK, 0 rows affected (0,02 sec)

		mysql> FLUSH PRIVILEGES;
		Query OK, 0 rows affected (0,01 sec)

	THIS is a single table of the database to store all the values:

		CREATE TABLE flights (
			hex_id VARCHAR(8) DEFAULT '',
			flight VARCHAR(8) DEFAULT '',
			squawk VARCHAR(8) DEFAULT '',
			checkout_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			lat DECIMAL(7,4),
			lon DECIMAL(7,4),
			alt DECIMAL(9,2),
			speed DECIMAL(9,2),
			vspeed DECIMAL(9,2),
			course INT
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci;


	THIS is a real flow from FR24 software, note how values added through time for every flight

		['451E8C', 0.0, 0.0, 306, 37975, 430, '2265', 0, '', '', 1627792767, '', '', '', 0, 64, '']
		['4BCE03', 0.0, 0.0, 320, 0, 441, '0000', 0, '', '', 1627792862, '', '', '', 0, 0, '']
		['4BCE03', 45.1525, 19.8544, 320, 38000, 438, '3256', 0, '', '', 1627792902, '', '', '', 0, 0, 'SXS6Z']
		['3C66B0', 0.0, 0.0, 0, 36000, 0, '0000', 0, '', '', 1627792935, '', '', '', 0, 0, '']
		['4BCE03', 45.1525, 19.8544, 320, 38000, 438, '3256', 0, '', '', 1627792902, '', '', '', 0, 0, 'SXS6Z']
		['3C66B0', 0.0, 0.0, 309, 36000, 430, '2270', 0, '', '', 1627792970, '', '', '', 0, 64, '']
		['4BCE03', 45.1525, 19.8544, 320, 38000, 438, '3256', 0, '', '', 1627792902, '', '', '', 0, 0, 'SXS6Z']
		['3C66B0', 0.0, 0.0, 309, 36000, 432, '2270', 0, '', '', 1627792988, '', '', '', 0, -64, '']

		NB: nobody tells you all data will be added during the contact, nobody tells you values will be correct

ALGORITHM:
	1. Get JSON from FR24 point, if not - do nothing (on error wait a bit more)
	2. For each record (which is single aircraft on radar) start work (see next)
	3. If this is new record - just store it in list of current crafts
	4. If this plane were seen, check is here more concrete values, if yes - put 'em to record in current crafts list
	5. When list of planes from radar is over, check if here are planes in current list but not in last received JSON
	6. If here is/are ones, pop in out from current list and move to seen list

	a. here is a daemon thread who constantly looks to "seen list" and pop rows from it out to store in database


'''

import 		requests 
from 		time 				import sleep, time
from 		datetime 			import datetime
from		threading			import Thread
from		mysql.connector		import pooling, Error as mysqlError

# HTTP headers for query, to make my script looks like a real browser
#
#
headers = {
	'Accept' : 'application/json, text/javascript, */*; q=01',
	'Accept-Language' : 'en-gb',
	'Host' : '192.168.0.40:8754', 
	'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15' ,
	'Referer' : 'http://192.168.0.40:8754/tracked.html' ,
	'Accept-Encoding' : 'gzip, deflate' ,
	'Connection' : 'keep-alive' ,
	'X-Requested-With' : 'XMLHttpRequest'
}

# MAPPING of values in plane's row in JSON
#	Some of 'em left unattendand, as I don't have any info about (and seen no values do make a guess)
#
keys = {
	'HEX ID' 	: 0,		# Plane's HEX id
	'LAT' 		: 1,		# Latitude
	'LON'		: 2,		# Longtitude
	'COURSE'	: 3, 		# aircraft_track (degrees, 0 is north, going clockwise)
	'ALT'		: 4, 		# foots over the sea
	'SPEED'		: 5, 		# knots per hour
	'SQW'		: 6, 		# squawk
	'DATE'		: 10,		# date time as epoch
	'VSPEED'	: 15, 		# vertical speed as foot per minute
	'FLIGHT'	: 16		# ok, this is call sign number
}

# VARIABLES and CONSTANTS
#
#
e 				= None 		# Ethalon to drop repeated messages
flights_current = {}		# planes present on radar 
flights_seen	= {}		# planes went out from radar and ready for database
foot_to_meters	= 0.3048	# foots to meters
knots_to_kmh	= 1.8520	# knots to km/h

# CREDENTIALS to connect to mySQL database
#
#
maindb	= { 'user'	: 'fr24', 'password' : 'password', 'host' : 'localhost', 'database' : 'fr24' }



# ZEROTRUST to numbers from strings
#
#
def safeint ( numb ) :
	try :
		return int(numb)
	except :
		return 0

# ZEROTRUST to numbers from strings
#
#
def safefloat ( numb ) :
	try :
		return float(numb)
	except :
		return 0.00



# REWORK JSON received from FR24 point.
#	1. Store "current list" of planes' hexs
#	2. For each plane in JSON do:
#		3. IF it is new - store it in current and take next
#		4. IF it repeated row, check are new values better than prevs and if yes - update stored values
#		5. REMOVE updated HEX from "current list" of planes' hexs
#	6. Check HEXs left in "current list" and move correspondent rows from "current" to "seen" list
#
def reWork ( fligts ) :
	global keys, flights_current, flights_seen
	
	flights_list = list(flights_current.keys())

	for (k, pair) in fligts.items() :

		try :
			f_date 	= datetime.fromtimestamp( pair[keys['DATE']] ).strftime('%Y-%m-%d %H:%M:%S')
		except :
			f_date	= datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		f_hex		= pair[ keys['HEX ID'] ]
		f_flight	= pair[ keys['FLIGHT'] ]
		f_sqw		= pair[ keys['SQW'] ]
		f_lat 		= safefloat(pair[ keys['LAT'] ])
		f_lon 		= safefloat(pair[ keys['LON'] ])
		f_course	= safeint( pair[ keys['COURSE'] ])
		f_alt		= int(safeint( pair[ keys['ALT'] ]) * foot_to_meters)
		f_speed		= int(safeint( pair[ keys['SPEED'] ]) * knots_to_kmh)
		f_vspeed	= int(safeint( pair[ keys['VSPEED'] ]) * foot_to_meters)

		if f_hex not in flights_list :
			flights_current.update(
				{ f_hex : {
					'DATE' 		: f_date,
					'FLIGHT'	: f_flight,
					'SQW'		: f_sqw,
					'LAT'		: f_lat,
					'LON'		: f_lon,
					'ALT'		: f_alt,
					'COURSE'	: f_course,
					'SPEED'		: f_speed,
					'VSPEED'	: f_vspeed
					} }
				)

			continue

		this_flight = flights_current.get( f_hex, {} )

		if this_flight == {} :
			this_flight = {
				'DATE' 		: f_date,
				'FLIGHT'	: f_flight,
				'SQW'		: f_sqw,
				'LAT'		: f_lat,
				'LON'		: f_lon,
				'ALT'		: f_alt,
				'COURSE'	: f_course,
				'SPEED'		: f_speed,
				'VSPEED'	: f_vspeed
				}
		else :
			this_flight.update( {'DATE' : f_date} )
			if f_flight != '' 	: this_flight.update( {'FLIGHT' : f_flight} )
			if f_sqw != '' 		: this_flight.update( {'SQW' 	: f_sqw} )
			if f_lat > 0.00 	: this_flight.update( {'LAT' 	: f_lat} )
			if f_lon > 0.00 	: this_flight.update( {'LON' 	: f_lon} )
			if f_alt > 0.00 	: this_flight.update( {'ALT' 	: f_alt} )
			if f_course > 0 	: this_flight.update( {'COURSE' : f_course})
			if f_speed  > 0 	: this_flight.update( {'SPEED'  : f_speed})
			if f_vspeed > 0 	: this_flight.update( {'VSPEED' : f_vspeed})

		flights_current.update( {f_hex : this_flight} )

		flights_list.pop( flights_list.index(f_hex) )


	for t_hex in flights_list :
		this_flight = flights_current.pop( t_hex )
		flights_seen.update( {t_hex : this_flight} )
		print( t_hex, this_flight )



# DAEMON thread to store values to database:
#	1. If here are no values to store - sleep for a while
#	2. Transform rows of "seen list" to store in database, remove 'em from list
#	3. Get connection from pool
#	4. Put rows into database
#	5. Commit
#	6. Free the connection to database
#	7. Sleep for a while
#
def storeList () :
	global cnxpool, flights_seen

	while True :
		flights_list = list(flights_seen.keys())

		if len( flights_list ) < 1  :
			sleep(20)
			continue

		insert_list = []
		for f_hex in flights_list :
			f_row = flights_seen.pop( f_hex, {} )
			if f_row == {} :
				continue

			insert_list.append( (
				f_hex,
				f_row['FLIGHT'],
				f_row['SQW'],
				f_row['DATE'],
				f_row['LAT'],
				f_row['LON'],
				f_row['ALT'],
				f_row['SPEED'],
				f_row['VSPEED'],
				f_row['COURSE'],
				) )

		if len( insert_list ) < 1 :
			sleep(20)
			continue

		try :
			cnx		= cnxpool.get_connection()
			cursor	= cnx.cursor(buffered=True)

			query = "INSERT INTO flights (hex_id, flight, squawk, checkout_at, lat, lon, alt, speed, vspeed, course) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			cursor.executemany( query, insert_list )

			cursor.close()
			cnx.commit()
			cnx.close()
		except mysqlError as err:
			cursor.close()
			cnx.close()
			print(err)
		except KeyboardInterrupt :
			raise



# MAIN thread
#	1. Create the connection pool to database
#	2. Start thread which stores values to database 
#	3. Start loop to ask FR24 point does it have news for you
#
if __name__ == '__main__':


	cnxpool = pooling.MySQLConnectionPool(pool_name = "fr", pool_size = 2, **maindb)

	x = Thread(target=storeList)
	x.start()

	while True :
		try :
			r = requests.get("http://192.168.0.40:8754/flights.json?time={}".format( time() * 1000), headers=headers)
			c = r.json()
			
			if e != c :
				reWork (c)
				e = c

			sleep(5)
		except requests.exceptions.ConnectionError :
			sleep( 20 )



#
#
# WHAT by Paul A Katurov <katurov@gmail.com>