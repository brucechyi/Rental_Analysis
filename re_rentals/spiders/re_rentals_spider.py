from scrapy import Spider, Request
from re_rentals.items import ReRentalsItem
import re

class Re_RentalsSpider(Spider):
	name 		 = 'Re_RentalsSpider'
	allowed_urls = ['https://www.rentals.com/']
	start_urls 	 = ['https://www.rentals.com/New-York/New-York/?page=1']

	def parse(self, response):
		result_urls = ['https://www.rentals.com/New-York/New-York/?page={}&per_page=30'.format(x) for x in range (1, 3)]
		#result_urls = ['https://www.rentals.com/New-York/New-York/?page={}&per_page=1000'.format(x) for x in range (1, 9)]
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
				zipcode = page_rows[i].xpath('.//div[1]/h5/text()').extract_first().split(' ')[3]
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


