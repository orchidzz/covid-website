import requests
from bs4 import BeautifulSoup
import re
from datetime import date
import database

response = requests.get('https://www.worldometers.info/coronavirus/?utm_campaign=homeAdvegas1?%22')

if response.status_code == 200:
	today = str(date.today()) #format yyyy-mm-dd
	
	soup = BeautifulSoup(response.text, 'html.parser')
	cls = soup.find_all(class_='maincounter-number')
	res = [today] #[date, cases, deaths, recovered]
	#parse the scraped html text to get values in span sections
	for div in cls:
		span = div.span.text
		span = re.sub(',', '', span)
		res.append(int(span))
		
	#catch error
	if len(res)!= 4:
		print("unexpected error when scraping")
	else:
		#insert into database table
		db = database.CovidDatabase()
		db.addToTable(res[0], res[1], res[3], res[2])
		#date, cases, recovered, deaths
else:
	print("failed to request")
