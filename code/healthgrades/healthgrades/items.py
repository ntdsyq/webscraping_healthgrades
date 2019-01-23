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
	age = scrapy.Field()
	practice_name = scrapy.Field()
	practice_addr = scrapy.Field()
	addr_street = scrapy.Field()
	city = scrapy.Field()
	state = scrapy.Field()
	zipcode = scrapy.Field()
	num_ins = scrapy.Field()
