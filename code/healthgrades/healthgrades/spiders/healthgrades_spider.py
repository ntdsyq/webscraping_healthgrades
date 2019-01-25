# need to run: scrapy crawl healthgrades_spider -o testoutput.csv -t csv
# otherwise, not outputting to csv file specified in pipelines

from scrapy import Spider
from healthgrades.items import DoctorItem
from scrapy import Request
import re
import numpy as np

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
		for url in all_urls:
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
					item['rating'] = np.nan
				else:
					if num_reviews is not None:
						if len(num_reviews) > 0:
							item['num_reviews'] = int(num_reviews.strip().split(' ')[0])
							item['rating'] = float(rating.split(' ')[1])
						else:
							item['num_reviews'] = 0
							item['rating'] = np.nan	
					else:
						item['num_reviews'] = 0
						item['rating'] = np.nan

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

				# yield item
				# parse individual doctor's page for additional info
				yield Request(url = 'https://www.healthgrades.com' + detailed_url, meta={'item': item}, callback=self.parse_doctor_page)

	def parse_doctor_page(self, response):
		item = response.meta['item']

		# rating details for doctor and office & staff
		if item['num_reviews'] != 0:
			doc_perf = response.xpath('//div[contains(@class,"c-doctor-performance")]//li')

			# only record if all 4 elements available
			if len(doc_perf) == 4:
				doc_rating = [0,0,0,0]
				for i in range(4):
					doc_star = doc_perf[i].xpath('./div[@class="star-rating"]/div[@class="filled"]/span/@class').extract()
					doc_rating[i] = len(doc_star) - 0.5 * ( doc_star[-1] == 'hg3-i hg3-i-star-half')
				item['doc_rating'] = '|'.join([str(x) for x in doc_rating])
					
			staff_perf = response.xpath('//div[contains(@class,"c-staff-performance")]//li')
			
			# only record if all 3 elements available - can improve
			if len(staff_perf) == 3:
				staff_rating = [0,0,0]
				for i in range(3):
					staff_star = staff_perf[i].xpath('./div[@class="star-rating"]/div[@class="filled"]/span/@class').extract()
					staff_rating[i] = len(staff_star) - 0.5 * ( staff_star[-1] == 'hg3-i hg3-i-star-half')
				item['staff_rating'] = '|'.join([str(x) for x in staff_rating]) 

		# get gender
		if item['featured'] == 0:
			item['gender'] = response.xpath('//span[@data-qa-target = "ProviderDisplayGender"]/text()').extract_first()
		else:
			item['gender'] = response.xpath('//span[@data-qa-target = "ProviderDisplayGender"]/text()').extract()[1]

		# education history
		edu = response.xpath('//section[@class="education-subsection"]//div[@class="education-card"]')
		keymap = {'Fellowship Hospital':'hosp_fellow', 'Residency Hospital':'hosp_res', 'Medical School': 'hosp_md'}
		if len(edu) > 0:
			edu_hist = {}
			for e in edu:
				k = e.xpath('.//div[@class="education-completed"]/text()').extract_first()
				v = e.xpath('.//div[@class="education-name"]/text()').extract_first()
				if k in ['Fellowship Hospital', 'Residency Hospital', 'Medical School']:
					edu_hist[keymap[k]] = v
			if len(edu_hist) > 0:
				for k in edu_hist:
					item[k] = edu_hist[k]

		yield item
