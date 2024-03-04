from playwright.async_api import async_playwright
import asyncio
import json
import httpx
import time
from lxml import html
from bs4 import BeautifulSoup
import datetime
import os, os.path

import app

def load_json(file:str) -> list:
    with open(file, 'r') as json_file:
        key = json.load(json_file)
        return key
loaded_keys = load_json('keys.json')

STEAM_MAIN_SITE = 'https://steamcommunity.com/market/search?appid=730'
CSGOSTASH_MAIN_SITE='https://csgostash.com/stickers/tournament/'
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; RM-1152) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15254'}
COOKIES_CSGOSTASH_USD = loaded_keys['csgostash_cookies_usd']
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
    soup = BeautifulSoup(response.text,'lxml')
    
    pagination = soup.find('ul', class_='pagination')
    pages = pagination.find_all('li')
    page_count = int(pages[-2].text)
    list_of_href = []
    
    for page in range(page_count):
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
            temp_dict = {'name':full_name,'href_link':href_link}
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
    

if __name__ == '__main__':
    #get_data_from_steam_market(STEAM_MAIN_SITE,15,'Paris holo 2023')

    #get_data_from_csgostash(CSGOSTASH_MAIN_SITE,'Paris 2023')
    # get_data_from_csgostash(CSGOSTASH_MAIN_SITE,'Rio 2022')
    # get_data_from_csgostash(CSGOSTASH_MAIN_SITE,'Antwerp 2022')
    # get_data_from_csgostash(CSGOSTASH_MAIN_SITE,'Stockholm 2021')
    # get_data_from_csgostash(CSGOSTASH_MAIN_SITE,'2020 RMR')

    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Paris 2023')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Rio 2022')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Antwerp 2022')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Stockholm 2021')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'2020 RMR')