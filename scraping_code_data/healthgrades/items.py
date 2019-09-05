# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoctorItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	featured = scrapy.Field()
	detailed_url = scrapy.Field()
	hcp_id = scrapy.Field()
	name = scrapy.Field()
	num_reviews = scrapy.Field()
	rating = scrapy.Field()
	age = scrapy.Field()
	practice_name = scrapy.Field()
	practice_addr = scrapy.Field()
	addr_street = scrapy.Field()
	city = scrapy.Field()
	state = scrapy.Field()
	zipcode = scrapy.Field()
	num_ins = scrapy.Field()
	gender = scrapy.Field()

	
	# ratings for doctors on: Trustworthiness, Explains condition(s) well, Answers questions, Time well spent
	doc_rating = scrapy.Field()
	
	# rating for office & staff on: 
	staff_rating = scrapy.Field()
	hosp_fellow = scrapy.Field()
	hosp_res = scrapy.Field()
	hosp_md = scrapy.Field()
	
	def __repr__(self):
		"""only print out attr1 after exiting the Pipeline"""
		return repr({'hcp_id': self['hcp_id']})
