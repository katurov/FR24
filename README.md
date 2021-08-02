##THE IDEA##

FR24 gives pretty nice service (on "business" level) if you build your own point for 'em. It is simple and easy, any can do it with the instruction from FR24. Hardware for this build is under $100, and it uses just about 20W/h, so this won't make you broke. 

	FR24 have its "gray points":
	1. They won't tell you to prepare your antenna (one with your SDR isn't good enough)
	2. They won't give you a history of planes traveled through "your controlled space" (but you can see "playback" on FR24 site)

As far as I looked for small planes, which aren't present in "playback" on FR24, I need to see and watch the web-console of my FR24 point to see hex-id,filter 'em by myself and don't blink. And so I did it to find 4C0DA1 (Piper PA-38-112 Tomahawk) but "sit here and don't blink" is bad varian for me as I have work and need to sleep a bit each day.

I'm thinking: what is something will "sit here and won't blink" 24/7 and write 'em all down to the list for me, so I'll able to check records in any time? This is the script.


##BASED ON:##

1. https://gist.github.com/msakai/3318776 -- this helps me to understand the sentence of the JSON pulled from FR24 
2. https://github.com/exxamalte/python-flightradar-client -- this opens me an idea to start

	I would like to thans 'em for the ideas. Thank you guys!

##INFO:##

1. HEX to human and be found here: https://www.planespotters.net/search?q=06A10C
2. Script use pooling to mySQL 'cause it can reconnect by itself (hope so)
3. Script works "here and now", so it cat lost some values and this is "ok" for my case
4. Terms:
4.1. SQW stands for "squawk" which you may know as "transponder": "channel" of plane's radio
4.2. FLIGHT stands for "call sign": https://www.flightradar24.com/blog/clearing-up-call-sign-confusion/

##HARDWARE UNDER THE BUILD:##

1. Raspberry Pi 2
2. Some suitable SDR (I really cannot remember which one)
3. An antenna done in some way like (I've made a "pepsy can")[https://discussions.flightaware.com/t/three-easy-diy-antennas-for-beginners/16348] 
4. Poweed USB-hub
5. Home server (mine: old laptop under debian)
6. Network with internet access, common for FR24 and Server (or they can access in some way to each other)

##PRECONDITIONS:##
1. You have done with the installation of own FlightRadar point and it is fully functional
2. You know IP address of your install. In my case it is 192.168.0.40
3. You have a dedicated server for script (python3 + mySQL)

##EXAMPLES AND HOWTOS:##

THIS is how I found the way to get JSON with currently presented crafts. It was interrested to understand that 'time=EPOCH' is used just to reject browser' caching algorithms. But it looks like you should use EPOCH with millis to make URL functional. Other headers are from my Safari and just are for "anycase".

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


THIS is the settings for mySQL database and user, please, change password for something. NB: localhost is for security. You also can use any database on your server, but change settings in connection in script. 

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

##ALGORITHM:##
1. Get JSON from FR24 point, if not - do nothing (on error wait a bit more)
2. For each record (which is single aircraft on radar) start work (see next)
3. If this is new record - just store it in list of current crafts
4. If this plane were seen, check is here more concrete values, if yes - put 'em to record in current crafts list
5. When list of planes from radar is over, check if here are planes in current list but not in last received JSON
6. If here is/are ones, pop in out from current list and move to seen list

* here is a daemon thread who constantly looks to "seen list" and pop rows from it out to store in database
