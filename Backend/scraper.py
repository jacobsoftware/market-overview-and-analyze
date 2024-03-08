from playwright.async_api import async_playwright
import asyncio
import json
import httpx
import time
from lxml import html
from bs4 import BeautifulSoup
import datetime
import os, os.path
import re
from sqlalchemy.orm import sessionmaker
import pprint
from itertools import islice

import app

def load_json(file:str) -> list:
    with open(file, 'r') as json_file:
        key = json.load(json_file)
        return key
LOADED_KEYS = load_json('keys.json')
CSFLOAT_API_KEY = LOADED_KEYS['csfloat_api_key']
STEAM_MAIN_SITE = 'https://steamcommunity.com/market/search?appid=730'
CSGOSTASH_MAIN_SITE='https://csgostash.com/stickers/tournament/'
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; RM-1152) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15254'}
COOKIES_CSGOSTASH_USD = LOADED_KEYS['csgostash_cookies_usd']
HREFS_PATH = os.path.join(os.path.dirname(__file__), 'href_stickers.json')


def retry(function, retries=3):
    def wrapper(*args,**kwargs):
        attempts = 0
        while attempts < retries:
            try:
                return function(*args,**kwargs)
            
            except httpx.HTTPError as error:
                print(error)
                time.sleep(2 + attempts*2)
                attempts += 1
                if attempts == 3: raise Exception('Something is wrong with server')

    return wrapper

   
@retry
def api_request(url: str, params=None, cookies=None) -> httpx.Response:
    response = httpx.get(url, headers=HEADERS, params=params,cookies=cookies)   
    return response


# Steam site is unstable and quite often crash. I guess better option is csgocase. 
# There is also API steam but it has big downside of requests limits

# def get_data_from_steam_market(url: str,
#                                number_of_pages: int,
#                                search_phrase: str) -> list:
    
#     search_phrase = search_phrase.replace(' ', '+')
#     list_of_data = []

#     for i in range (1,number_of_pages+1):

#         current_url = url + '&q=' + search_phrase + '#p'+str(i) + '_deafault_desc'
#         response = api_request(current_url)
#         tree = html.fromstring(response.text)   
#         items = tree.xpath('//a[@class="market_listing_row_link"]')
        
#         for index,item in enumerate(items):

#             name =item.xpath('//div[@class="market_listing_item_name_block"]/span[@class="market_listing_item_name"]/text()')[index]
#             price = item.xpath('//div[@class="market_listing_right_cell market_listing_their_price"]/span/span[@class="normal_price"]/text()')[index]
#             market_volume = item.xpath('//div[@class="market_listing_right_cell market_listing_num_listings"]/span/span[@class="market_listing_num_listings_qty"]/text()')[index]
#             list_of_data.append([name, price, market_volume])

#         time.sleep(2)
    
#     return list_of_data


# No need to get hrefs
def check(function):
    def wrapper(url,search_phrase):
        try:
            check_json = load_json(HREFS_PATH)
            if search_phrase not in check_json:
                function(url,search_phrase)
            else: print('Already exist')
        except:
            print('Exception')
            function(url,search_phrase)
    return wrapper


@check                  
def get_href_from_csgostash(url: str,
                            search_phrase: str) -> None:

    change_phrase = search_phrase.replace(' ', '+')
    base_url = url + change_phrase
    response = api_request(base_url)
    # soup = BeautifulSoup(response.text,'lxml')
    # pagination = soup.find('ul', class_='pagination')
    # pages = pagination.find_all('li')
    # page_count = int(pages[-2].text)
    tree = html.fromstring(response.text)
    number_of_pages = tree.xpath('//div[@class="row"][3]/div[@class="col-lg-12 col-widen pagination-nomargin"]/ul[@class="pagination"]/li/a/text()')[-2]
    list_of_href = []
    
    for page in range(int(number_of_pages)):
        if page == 0:
            tree = html.fromstring(response.text)
            items = tree.xpath('//div[@class="col-lg-4 col-md-6 col-widen text-center"]')

        else:
            base_url = url + change_phrase
            next_page_url = base_url + '?page='+str(int(page+1))
            
            response = api_request(next_page_url)
            tree = html.fromstring(response.text)
            items = tree.xpath('//div[@class="col-lg-4 col-md-6 col-widen text-center"]')

        for index,item in enumerate(items):

            name = item.xpath('//h3/a/text()')[index]

            if search_phrase == '2020 RMR': full_name = 'Sticker | ' + name + ' | RMR 2020'
            else: full_name = 'Sticker | ' + name + ' | ' + search_phrase
            href_link = item.xpath('//div[@class="well result-box nomargin"]/h3/a/@href')[index]
            capsule_name = item.xpath('//div[@class="margin-bot-sm"]/p/a/text()')[index]
            temp_dict = {'name':full_name,'href_link':href_link,'capsule_name':capsule_name}
            print(temp_dict)
            list_of_href.append(temp_dict)

    dict_to_json = {}
    dict_to_json[search_phrase] = list_of_href

    #print(list_of_href)
    if os.path.isfile(HREFS_PATH):
        loaded_json = load_json(HREFS_PATH)
        loaded_json.update(dict_to_json)
        with open(HREFS_PATH, 'w') as save_hrefs:
            json.dump(loaded_json,save_hrefs,sort_keys=True,indent=4,separators=(',', ': '))
    else:
        with open(HREFS_PATH, 'w') as save_hrefs:
            json.dump(dict_to_json,save_hrefs,sort_keys=True,indent=4,separators=(',', ': '))


def get_data_about_event_stickers(event_name: str,
                                  table: object) -> None:

    hrefs = load_json(HREFS_PATH)
    hrefs = hrefs[event_name]
    cookie = {'currency':COOKIES_CSGOSTASH_USD.get('value')}
    scraped_data_about_stickers = []

    #for href in islice(hrefs, limit=10):
    for index,href in enumerate(hrefs):
        url = href['href_link']
        response = api_request(url,cookies=cookie)
        tree = html.fromstring(response.text)

        # date = Column(String)
        # name = Column(String)
        # price = Column(Float)
        # market_listings = Column(Integer)
        # sold_in_last_day = Column(Integer)
        # capsule_name = Column(String)
        
        current_date = datetime.datetime.today().strftime('%d-%m-%Y')
        name = href['name']
        capsule_name = href['capsule_name']

        price = tree.xpath('//div[@class="btn-group btn-group-justified"][1]/a/span[@class="pull-right"]/text()')
        price = price[0].replace('$','')

        listings = tree.xpath('//table[@class="table table-bordered text-left"]/tr[1]/td/span/text()')
        listings = re.findall('\d+',listings[0])
        if listings[0] == '': listings = 0
        else: listings = listings[0]

        sold_in_last_day = tree.xpath('//table[@class="table table-bordered text-left"]/tr[3]/td/span/text()')
        sold_in_last_day = re.findall('\d+', sold_in_last_day[0])
        if not sold_in_last_day: sold_in_last_day = 0
        else: sold_in_last_day = sold_in_last_day[0]

        temp_dict = {'date_of_scrape': current_date, 'name': name, 'price': price, 'market_listings': listings, 
                     'sold_in_last_day': sold_in_last_day, 'capsule_name': capsule_name}
        print('Number: ',index+1,temp_dict)
        scraped_data_about_stickers.append(temp_dict)

    #pprint.pprint(scraped_data_about_stickers)
    save_scraped_data(scraped_data_about_stickers,table)
        

def save_scraped_data(list_of_data_to_db: list,
                      table: object) -> None:
    session = app.SessionLocal()
    for item in list_of_data_to_db:
        entry = table(date_of_scrape=item['date_of_scrape'], name = item['name'], price = item['price'], market_listings = item['market_listings'],
                    sold_in_last_day = item['sold_in_last_day'], capsule_name = item['capsule_name']  )
        session.add(entry)
    session.commit()
    session.close()

def get_current_player_base() -> list:
    url = 'https://steamcharts.com/app/730'
    response = api_request(url)
    tree = html.fromstring(response.text)

    avg_player = tree.xpath('//div[@id="app-heading"]/div[1]/span/text()')
    peak_player_day = tree.xpath('//div[@id="app-heading"]/div[2]/span/text()')
    return [avg_player,peak_player_day]

def get_application_rate():
    url = 'https://csfloat.com/api/v1/listings'
    # id
    params = {'Authorization':CSFLOAT_API_KEY}
    response = api_request(url,params=params)
    print(response.json())

# Faster way to scrape data but without daily sell - preferable if csgostash set rate limits

# def get_data_from_csgostash(url: str,
#                             search_phrase: str) -> list:
    
#     change_phrase = search_phrase.replace(' ', '+')
#     base_url = url + change_phrase
#     cookie = {'currency':COOKIES_CSGOSTASH_USD.get('value')}
#     response = api_request(base_url,cookies=cookie)
#     soup = BeautifulSoup(response.text,'lxml')
    
#     pagination = soup.find('ul', class_='pagination')
#     pages = pagination.find_all('li')
#     page_count = int(pages[-2].text)

#     list_of_data = []
#     current_date = datetime.datetime.today().strftime('%m-%d-%Y')



#     for page in range(page_count):
#         if page == 0:
#             tree = html.fromstring(response.text)
#             items = tree.xpath('//div[@class="col-lg-4 col-md-6 col-widen text-center"]')

#         else:
#             base_url = url + change_phrase
#             next_page_url = base_url + '?page='+str(int(page+1))
            
#             response = api_request(next_page_url,cookies=cookie)
#             tree = html.fromstring(response.text)
#             items = tree.xpath('//div[@class="col-lg-4 col-md-6 col-widen text-center"]')

#         for index,item in enumerate(items):

#             name = item.xpath('//h3/a/text()')[index]

#             if search_phrase == '2020 RMR': full_name = 'Sticker | ' + name + ' | RMR 2020'
#             else: full_name = 'Sticker | ' + name + ' | ' + search_phrase

#             price = item.xpath('//div[@class="price"]/p/a/text()')[index]
#             price = price.replace('$','')
#             listings = item.xpath('//div[@class="btn-group-sm btn-group-justified"]/a[@class="btn btn-default market-button-item"]/text()')[index]
#             listings = listings.split(' ',1)[0]
#             date = current_date
#             list_of_data.append([full_name,price,listings])

#     print(search_phrase) 
#     print(list_of_data)
def main():

    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Paris 2023')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Rio 2022')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Antwerp 2022')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Stockholm 2021')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'2020 RMR')

    get_data_about_event_stickers('Paris 2023',app.models.Paris_2023)
    get_data_about_event_stickers('Rio 2022',app.models.Rio_2022)
    get_data_about_event_stickers('Antwerp 2022',app.models.Antwerp_2022)
    get_data_about_event_stickers('Stockholm 2021',app.models.Stockholm_2021)
    get_data_about_event_stickers('2020 RMR',app.models.Rmr_2020)

if __name__ == '__main__':
    #get_data_from_steam_market(STEAM_MAIN_SITE,15,'Paris holo 2023')

    #get_data_from_csgostash(CSGOSTASH_MAIN_SITE,'Paris 2023')
    # get_data_from_csgostash(CSGOSTASH_MAIN_SITE,'Rio 2022')
    # get_data_from_csgostash(CSGOSTASH_MAIN_SITE,'Antwerp 2022')
    # get_data_from_csgostash(CSGOSTASH_MAIN_SITE,'Stockholm 2021')
    # get_data_from_csgostash(CSGOSTASH_MAIN_SITE,'2020 RMR')
    #get_application_rate()
    #get_current_player_base()
    main()