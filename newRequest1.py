# Code referred from ...
# https://stackoverflow.com/questions/5942759/best-place-to-clear-cache-when-restarting-django-server
from django.conf import settings

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

settings.configure(CACHES=CACHES) # include any other settings you might need
# Referred code ends here

from bs4 import BeautifulSoup
import requests, time, csv
from django.core.cache import cache
import numpy as np
import matplotlib.pyplot as plt


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


def printResult_line (result, site, URL, tt):
    switcher = {
        0:  # 0 - Successful
            [site, "O", "", URL, tt],
        1:  # 1 - TimeOut Error
            [site, "X", "T/O", URL, tt],
        2:  # 2 - Routed to fixed KCSC Website
            [site, "X", "DNS", URL, tt],
        3:  # 3 - Connection Error (RST)
            [site, "X", "CXN", URL, tt],
        4:  # 4 - Unknown Error
            [site, "X", "UNK", URL, tt]
    };

    with open ('result.csv', 'a', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(switcher.get (result, "Invalid Input"))


def printResult(category, element_list, HTTP):
    # HTTP - True, HTTPS - False

    # [accessible, T/O, DNS, CXN, UNK]
    acc = [0, 0, 0, 0, 0]

    with open('result.csv', 'a', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow([])
        if HTTP:
            writer.writerow(["TEST RESULT FOR "+ category.upper()+" (HTTP),,,,"])
        else:
            writer.writerow(["TEST RESULT FOR "+ category.upper()+" (HTTPS),,,,"])
        writer.writerow(["Site", "Accessible", "CensorType", "URL", "Time Taken"])

    # Restrict number of sites per categories
    # element_list = element_list[:4]

    for site in element_list:
        if HTTP:
            httpURL = 'http://www.'+site+'/'
            ti = time.process_time()
            res = requestPage(httpURL)
            printResult_line(res, site, httpURL, time.process_time()-ti) 

        else:
            httpsURL = 'https://www.'+site+'/'
            ti = time.process_time()
            res = requestPage(httpsURL)
            printResult_line(res, site, httpsURL, time.process_time()-ti)

        acc[res] += 1

    return acc


# Code referred from...
# https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/horizontal_barchart_distribution.html#sphx-glr-gallery-lines-bars-and-markers-horizontal-barchart-distribution-py

def survey(results, category_names, categories):
    data = np.array(results)
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(categories, widths, left=starts, height=0.5, label=colname, color=color)
        xcenters = starts + widths / 2

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'

        for y, (x, c) in enumerate(zip(xcenters, widths)):
            ax.text(x, y, str(int(c)), ha='center', va='center', color=text_color) 

    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1), loc='lower left', fontsize='small')
    
    return fig, ax
# Referred code ends here


def testout (categoryList, HTTP, Label):
    categories = []
    results = []
    resultType = ['Accessible','TimeOut','DNS Tampering','ConnectionError','Unknown']

    for i in categoryList:
        temp1 = requests.get ("https://www.alexa.com"+i[1])
        categories.append(i[0])

        result = printResult(i[0], loadAlexa_CategoryItem(temp1.text), HTTP)
        results.append(result)

        cache.clear()    

    survey(results, resultType, categories)
    plt.savefig(Label)


with open('result.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([])
    writer.writerow(["Data collected at "+ time.ctime()+",,,,"])


temp0 = requests.get ("https://www.alexa.com/topsites/category")
categoryList = loadAlexa_Category(temp0.text)

# Restrict number of categories
# categoryList = categoryList[:2]

# Excluding 'world' category
categoryList = categoryList[:-1]

testout(categoryList, True, 'HTTP_category.png')
testout(categoryList, False, 'HTTPS_category.png')

# Testing Korea
# testout([('South Korea', '/topsites/countries/KR')], True, 'HTTP_Korea.png')
# testout([('South Korea', '/topsites/countries/KR')], False, 'HTTPS_Korea.png')
