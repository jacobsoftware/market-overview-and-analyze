from playwright.async_api import async_playwright
import asyncio
import json
import httpx
import time
from lxml import html
from bs4 import BeautifulSoup
import app
STEAM_MAIN_SITE = 'https://steamcommunity.com/market/search?appid=730'
CSGOSTASH_MAIN_SITE='https://csgostash.com/stickers/tournament/'
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; RM-1152) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15254'}


def load_json(file:str) -> list:
    with open(file, 'r') as json_file:
        key = json.load(json_file)
        return key
    
def retry(function, retries=3):
    def wrapper(*args):
        attempts = 0
        while attempts < retries:
            try:
                return function(*args)
            
            except httpx.HTTPError as error:
                print(error)
                time.sleep(2 + attempts*2)
                attempts += 1
                if attempts == 3: raise Exception('Something is wrong with server')

    return wrapper

   
@retry
def api_request(url: str, params=None) -> httpx.Response:
    response = httpx.get(url, headers=HEADERS, params=params)   
    return response

# Steam site is unstable and quite often crash. I guess better option is csgocase.
def get_data_from_steam_market(url: str,
                               number_of_pages: int,
                               search_phrase: str) -> list:
    
    search_phrase = search_phrase.replace(' ', '+')
    list_of_data = []

    for i in range (1,number_of_pages+1):

        current_url = url + '&q=' + search_phrase + '#p'+str(i) + '_deafault_desc'
        response = api_request(current_url)
        tree = html.fromstring(response.text)   
        items = tree.xpath('//a[@class="market_listing_row_link"]')
        
        for index,item in enumerate(items):

            name =item.xpath('//div[@class="market_listing_item_name_block"]/span[@class="market_listing_item_name"]/text()')[index]
            price = item.xpath('//div[@class="market_listing_right_cell market_listing_their_price"]/span/span[@class="normal_price"]/text()')[index]
            market_volume = item.xpath('//div[@class="market_listing_right_cell market_listing_num_listings"]/span/span[@class="market_listing_num_listings_qty"]/text()')[index]
            list_of_data.append([name, price, market_volume])

        time.sleep(2)
    
    return list_of_data
# //div[@class="col-lg-4 col-md-6 col-widen text-center"]        
def get_href_from_csgostash(url: str,
                            search_phrase: str) -> None:
    search_phrase = search_phrase.replace(' ', '+')
    base_url = url + search_phrase
    response = api_request(base_url)
    soup = BeautifulSoup(response.text,'lxml')
    pagination = soup.find('ul', class_='pagination')
    pages = pagination.find_all('li')
    page_count = pages[-2].text


    list_of_href = []
    

if __name__ == '__main__':
    #get_data_from_steam_market(STEAM_MAIN_SITE,15,'Paris holo 2023')
    get_href_from_csgostash(CSGOSTASH_MAIN_SITE,'Paris 2023')