# need to run: scrapy crawl healthgrades_spider -o testoutput.csv -t csv
# otherwise, not outputting to csv file specified in pipelines

from scrapy import Spider
from healthgrades.items import DoctorItem
from scrapy import Request
import re

class HealthGradesSpider(Spider):
	name = 'healthgrades_spider'
	allowed_urls = ['https://healthgrades.com']
	# change this URL for other specialties and locations of interest
	url_main = 'https://www.healthgrades.com/gastroenterology-directory/ny-new-york/new-york'
	start_urls = [url_main]
	roster = {}
			
	def parse(self, response):
		n_tot = response.xpath('//span[@data-qa-target="qa-search-count"]/text()').extract_first()
		#print(n_tot)

		page_max = 27
		all_urls = [self.url_main]
		for p in range(2,page_max+1):
			all_urls.append(self.url_main + '_' + str(p))
		#print(all_urls)

		# check if can scrape basic info from the first page
		for url in all_urls[0:2]:
			yield Request(url = url, callback=self.parse_result_page)

	def parse_result_page(self, response):
		cards = response.xpath('//div[@class="card-content"]')	
		#print(len(cards))
		for rec in cards:
			# for any of the info below, if tag does not exist, return empty string
			detailed_url = rec.xpath('.//h3[@class="uCard__name"]/a/@href').extract_first()
			hcp_id = detailed_url[11:]
			if hcp_id not in self.roster:
				self.roster[hcp_id] = 1
				name = rec.xpath('.//h3[@class="uCard__name"]/a/text()').extract_first()
				num_reviews = rec.xpath('.//span[@class="rating__reviews"]/text()').extract_first()
				rating = rec.xpath('.//span[contains(@class,"rating__stars")]/@aria-label').extract_first()
				age = rec.xpath('.//div[@class="uCard__age"]/text()').extract()
				addr_street = rec.xpath('.//div[@class="office-location__address"]/span[@class="address--street"]/text()').extract_first()
				addr_citystate = rec.xpath('.//div[@class="office-location__address"]/span[@class="address--city-state"]/text()').extract()
				practice = 	rec.xpath('.//div[@class="office-location__address"]/span[not(@class)]/text()').extract_first()
				num_insurance = rec.xpath('.//div[@class="uCard__insurance"]/div/text()').extract()
				featured = len(rec.xpath('.//div[@class="featured-call-out"]'))
				
				# indicator for if a featured doctor or not

				if len(addr_citystate) >= 5:
					city = addr_citystate[0]
					state = addr_citystate[2]
					zipcode = addr_citystate[4]
				else:
					city = ''
					state = ''
					zipcode = ''

				item = DoctorItem()
				item['featured'] = featured
				item['detailed_url'] = detailed_url
				item['hcp_id'] = hcp_id
				item['name'] = name

				if num_reviews == "Leave a review":
					item['num_reviews'] = 0
				else:
					item['num_reviews'] = int(num_reviews.strip().split(' ')[0])

				if len(age) == 0:
					item['age'] = None
				else:
					item['age'] = int(age[2])

				item['practice_name'] = practice
				item['practice_addr'] = ', '.join([addr_street, city, state, zipcode])
				item['addr_street'] = addr_street
				item['city'] = city
				item['state'] = state
				item['zipcode'] = zipcode

				if len(num_insurance) > 0:
					item['num_ins'] = int(num_insurance[2])

				#yield item
				# parse individual doctor's page for additional info
				yield Request(url = 'https://www.healthgrades.com' + detailed_url, meta={'item': item}, callback=self.parse_doctor_page)

	def parse_doctor_page(self, response):
		item = response.meta['item']
		yield item
