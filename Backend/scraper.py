import json
import httpx
import time
from lxml import html
import datetime
import os, os.path
import re
import pprint
from itertools import islice
import pandas as pd

import app
import models
from utils_file import *


    
LOADED_KEYS = load_json('keys.json')
CSFLOAT_API_KEY = LOADED_KEYS['csfloat_api_key']
STEAM_MAIN_SITE = 'https://steamcommunity.com/market/search?appid=730'
CSGOSTASH_MAIN_SITE='https://csgostash.com/stickers/tournament/'
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; RM-1152) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15254'}
COOKIES_CSGOSTASH_USD = LOADED_KEYS['csgostash_cookies_usd']
STICKERS_INFO = os.path.join(os.path.dirname(__file__), 'stickers_info.json')
CAPSULE_INFO = os.path.join(os.path.dirname(__file__), 'capsules_info.json')


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
                if attempts == 3: raise Exception('Something is wrong with server or link')

    return wrapper

   
@retry
def api_request(url: str, params=None, cookies=None) -> httpx.Response:
    response = httpx.get(url, headers=HEADERS, params=params,cookies=cookies)   
    return response


def check(function):
    def wrapper(url,search_phrase):
        try:
            check_json = load_json(STICKERS_INFO)
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
    print(base_url)
    response = api_request(base_url)
    tree = html.fromstring(response.text)
    number_of_pages = tree.xpath('//div[@class="row"]/div[@class="col-lg-12 col-widen pagination-nomargin"]/ul[@class="pagination"]/li/a/text()')[-2]
    print(number_of_pages)
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

            name = item.xpath('//div[@class="well result-box nomargin"]/h3/a/text()')[index]

            
            full_name = 'Sticker | ' + name + ' | ' + search_phrase
            href_link = item.xpath('//div[@class="well result-box nomargin"]/h3/a/@href')[index]
            capsule_name = item.xpath('//div[@class="margin-bot-sm"]/p/a/text()')[index]
            temp_dict = {'name':full_name,'href_link':href_link,'capsule_name':capsule_name}
            print(temp_dict)
            list_of_href.append(temp_dict)

    dict_to_json = {}
    dict_to_json[search_phrase] = list_of_href

    #print(list_of_href)
    save_or_update_json(STICKERS_INFO,dict_to_json)




def get_data_about_event_stickers(event_name: str,
                                  table: object) -> None:

    hrefs = load_json(STICKERS_INFO)
    hrefs = hrefs[event_name]
    cookie = {'currency':COOKIES_CSGOSTASH_USD.get('value')}
    scraped_data_about_stickers = []

    #for href in islice(hrefs, limit=10):
    for index,href in enumerate(hrefs):
        url = href['href_link']
        response = api_request(url,cookies=cookie)
        tree = html.fromstring(response.text)

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
    params = {'Authorization':CSFLOAT_API_KEY}
    response = api_request(url,params=params)
    print(response.json())

def get_buff_id_of_items():

    url = 'https://raw.githubusercontent.com/ModestSerhat/buff163-ids/main/buffids.json'
    response = api_request(url)
    response_dict = response.json()
    
    capsule_list = []
    stickers_list = []
    events = ['Paris 2023','Rio 2022','Antwerp 2022','Stockholm 2021','2020 RMR']
    rmr_capsule = ['2020 RMR Legends', '2020 RMR Challengers','2020 RMR Contenders']
    sticker_dict = load_json(STICKERS_INFO)
    
    for key in response_dict:
        
        if 'Capsule' in response_dict[key] or any(x in response_dict[key] for x in rmr_capsule):
            
            if any(x in response_dict[key] for x in events):
                capsule_list.append({'buff_id': key,'capsule_name':response_dict[key]})

        if re.search('^Sticker.*$',response_dict[key]):
            if any(x in response_dict[key] for x in events):
                split_name = response_dict[key].split(' | ')
                for index,_ in enumerate(sticker_dict[split_name[-1]]):

                    if sticker_dict[split_name[-1]][index]['name'] == response_dict[key]:
                        sticker_dict[split_name[-1]][index].update({'buff_id':key})
                        

                
                
                


            #stickers_list.append({'buff_id': key,'sticker_name':response_dict[key]})
    if os.path.isfile(CAPSULE_INFO) is False:
        capsule_dict = {}
        capsule_dict['capsule'] = capsule_list
        save_or_update_json(CAPSULE_INFO,capsule_dict)
    save_or_update_json(STICKERS_INFO,sticker_dict)

    





def main():

    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Paris 2023')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Rio 2022')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Antwerp 2022')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Stockholm 2021')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'2020 RMR')

    # get_data_about_event_stickers('Paris 2023',models.Paris_2023)
    # get_data_about_event_stickers('Rio 2022',models.Rio_2022)
    # get_data_about_event_stickers('Antwerp 2022',models.Antwerp_2022)
    # get_data_about_event_stickers('Stockholm 2021',models.Stockholm_2021)
    # get_data_about_event_stickers('2020 RMR',models.Rmr_2020)

if __name__ == '__main__':
    main()
    get_buff_id_of_items()

