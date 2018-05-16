from scrapy import Spider, Request
from re_rentals.items import ReRentalsItem
import re

class Re_RentalsSpider(Spider):
	name 		 = 'Re_RentalsSpider'
	allowed_urls = ['https://www.rentals.com/']
	#start_urls 	 = ['https://www.rentals.com/New-York/New-York/?page=1']
	start_urls 	 = ['https://www.rentals.com/Locations']

	def parse(self, response):
		states_rows  = response.xpath('//ul[@class="search_locations_states"]/li')
		state_urls 	 = []
		for i in range(0, len(states_rows)):
			state = states_rows[i].xpath('./a/@href').extract_first()
			state_urls = state_urls + ['https://www.rentals.com'+state]

		for url in state_urls:
			yield Request(url=url, callback=self.parse_state_page)

	def parse_state_page(self, response):
		cities_rows = response.xpath('.//ul[@class="home_rent_apt"]/li')
		cities_urls = []
		for i in range(0, len(cities_rows)):
			city = cities_rows[i].xpath('./a/@href').extract_first()
			cities_urls = cities_urls + ['https://www.rentals.com'+city]

		for url in cities_urls:
			yield Request(url=url, callback=self.parse_cities_page)

	def parse_cities_page(self, response):
		try:
			pages = int(response.xpath('.//div[@class="pagination-heading-text"]/text()').extract_first().split(" ")[3])
		except IndexError:
			pages = 0

		if pages > 0:
			result_urls = [response.url+'?page={}&per_page=30'.format(x) for x in range (1, pages+1)]
		else:
			result_urls = [response.url+'?page=1&per_page=30']

		for url in result_urls:
			yield Request(url=url, callback=self.parse_result_page)

	def parse_result_page(self, response):
		# This fucntion parses the search result page to come up with individual listing URL
		individual_urls = []
		page_rows 		= response.xpath('//div[@id="search_results"]/div[@class="result"]')
		#iterate through each listing on the page
		for i in range(0,len(page_rows)):
			#if the listing is part of a single family residence, parse
			if page_rows[i].xpath('./@itemtype').extract_first().split('/')[3] == 'SingleFamilyResidence':
				price 	= page_rows[i].xpath('.//div[1]/div/strong/text()').extract_first()
				bedroom = page_rows[i].xpath('.//div[1]/p/text()').extract_first().split('/')[0]
				bathroom= page_rows[i].xpath('.//div[1]/p/text()').extract_first().split('/')[1]
				try:
					zipcode = page_rows[1].xpath('.//div[1]/h5/text()').extract_first().split(',')[1].split(' ')[2]
				except IndexError:
					zipcode = 0

				address = page_rows[i].xpath('./div[1]/a/@title').extract_first()
				
				item=ReRentalsItem()
				item['price']	= price
				item['bedroom'] = bedroom
				item['bathroom']= bathroom
				item['zipcode'] = zipcode
				item['address'] = address

				yield item
			
			else: #if the listing is part of a multiple listing of an apartment complex 
		 		href 			= page_rows[i].xpath('./div/a/@href').extract_first()
		 		individual_urls = individual_urls + ['https://www.rentals.com' + href]

		for url in individual_urls:
			yield Request(url=url, callback=self.parse_detail_page)


	def parse_detail_page(self, response):
		# This function parses the non-singlefamily listings
		apt_table = response.xpath('//table[@class="floorPlanTable"]/tr')
		zipcode   = response.xpath('.//span[@itemprop="postalCode"]/text()').extract_first()
		address   = response.xpath('.//span[@itemprop="streetAddress"]/text()').extract_first()

		for i in range(1, len(apt_table)):
			price 	= apt_table[i].xpath('./td[6]/text()').extract_first()
			bedroom = apt_table[i].xpath('./td[2]/text()').extract_first()
			bathroom= apt_table[i].xpath('./td[3]/text()').extract_first()



			item=ReRentalsItem()
			item['price']	= price
			item['bedroom'] = bedroom
			item['bathroom']= bathroom
			item['zipcode'] = zipcode
			item['address'] = address

			yield item


