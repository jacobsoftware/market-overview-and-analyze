# Those methods are alternative way to scrape same data without volume sell.


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
