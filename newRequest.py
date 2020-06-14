from bs4 import BeautifulSoup
import requests


def requestPage(site_url):
# Modified to consider Korean Censoring website
# 0 - Successful
# 1 - TimeOut Error - TO
# 2 - Routed to fixed KCSC Website - DNS
# 3 - Connection Error (RST) - CXN
# 4 - Unknown Error - UNK

	try:
		r = requests.get (site_url, timeout=10)

		# Routed to fixed KCSC (Korean Communications Standards Commission) Website
		if r.url[0:20] == "http://warning.or.kr":
			return 2
		return 0
	
	except requests.exceptions.ReadTimeout:
		return 1

	except requests.exceptions.ConnectionError:
		return 3
		# WinError 10054 - ConnectionResetError Included

	except:
		return 4
		


def loadAlexa_Category(alexa_html):
	alexa_soup = BeautifulSoup(alexa_html, 'lxml')

	element_list = []

	for element in alexa_soup.find_all('div', class_ = 'categories top'):
		for i in element.find_all('ul'):
			for j in i.find_all('li'):
				element_list.append((j.text, j.a["href"]))

	return element_list


def loadAlexa_CategoryItem(alexa_html):
	alexa_soup = BeautifulSoup(alexa_html, 'lxml')

	element_list = []

	for element in alexa_soup.find_all('div', class_ = 'td DescriptionCell'):
		website = element.p.a.text
		element_list.append(website)

	return element_list


def printResult_line (result, site, URL):
	switcher = {
		0:  # 0 - Successful
			"{:<30}{:<15}{:<20}{:<35}".format(site, "O", "", URL),
		1:  # 1 - TimeOut Error
			"{:<30}{:<15}{:<20}{:<35}".format(site, "X", "T/O", URL),
		2:  # 2 - Routed to fixed KCSC Website
			"{:<30}{:<15}{:<20}{:<35}".format(site, "X", "DNS", URL),
		3:  # 3 - Connection Error (RST)
			"{:<30}{:<15}{:<20}{:<35}".format(site, "X", "CXN", URL),
		4:  # 4 - Unknown Error
			"{:<30}{:<15}{:<20}{:<35}".format(site, "X", "UNK", URL)
	};

	print(switcher.get (result, "Invalid Input"))


def printResult(category, element_list):
	print ('{:=^100}'.format(''))
	print ('{:=^100}'.format('TEST RESULT FOR '+category.upper()))
	print ('{:=^100}'.format(''))

	print("{:<30}{:<15}{:<20}{:<35}".format("Site", "Accessible", "CensorType","URL"))

	for site in siteList:
		httpURL = 'http://www.'+site+'/'
		httpsURL = 'https://www.'+site+'/'

		printResult_line(requestPage(httpURL), site, httpURL)
		printResult_line(requestPage(httpsURL), site, httpsURL)


temp0 = requests.get ("https://www.alexa.com/topsites/category")
categoryList = loadAlexa_Category(temp0.text)

# Excluding 'world' category
categoryList = categoryList[:-1]

for i in categoryList:
	temp1 = requests.get ("https://www.alexa.com"+i[1])
	siteList = loadAlexa_CategoryItem(temp1.text)
	printResult(i[0], siteList)
	print()

# temp = requests.get ("https://www.alexa.com/topsites/category/Top/Adult")
# siteList = loadAlexa_CategoryItem(temp.text)
# printResult('adult', siteList)


