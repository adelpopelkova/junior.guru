import re
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from scrapy import Request
from scrapy import Spider as BaseSpider
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Identity, MapCompose, TakeFirst

from juniorguru.scrapers.items import Job, first, parse_relative_time, split


class Spider(BaseSpider):
    name = 'linkedin'
    custom_settings = {
        'USER_AGENT': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:75.0) '
                       'Gecko/20100101 Firefox/75.0'),
        'ROBOTSTXT_OBEY': False,
    }
    search_params = {
        'keywords': 'Software Engineer',
        'location': 'Czech Republic',
        'f_E': '1,2',  # entry level, internship
        'f_TP': '1,2,3,4',  # past month
        'redirect': 'false',  # ?
        'position': '1',  # the job ad position to display as open
        'pageNum': '0',  # pagination - page number
        'start': '0',  # pagination - offset
    }
    start_urls = [
        ('https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/'
         f'search?{urlencode(search_params)}')
    ]
    results_per_request = 25

    def parse(self, response):
        links = response.css('a[href*="linkedin.com/jobs/view/"]::attr(href)').getall()
        links = [strip_params(link, ['position', 'pageNum']) for link in links]
        yield from response.follow_all(links, callback=self.parse_job)

        if len(links) >= self.results_per_request:
            url = increment_param(response.url, 'start', self.results_per_request)
            yield Request(url, callback=self.parse)

    def parse_job(self, response):
        loader = Loader(item=Job(), response=response)
        loader.add_css('title', 'h1::text')
        loader.add_value('link', response.url)
        loader.add_css('company_name', 'h1 ~ h3 a::text')
        loader.add_css('company_name', 'h1 ~ h3 span::text')
        loader.add_css('company_link', 'h1 ~ h3 a::attr(href)')
        loader.add_css('location', 'h1 ~ h3 > span:nth-of-type(2)::text')
        loader.add_xpath('employment_types', "//h3[contains(., 'Employment type')]/following-sibling::span/text()")
        loader.add_xpath('experience_levels', "//h3[contains(., 'Seniority level')]/following-sibling::span/text()")
        loader.add_css('posted_at', 'h1 ~ h3:nth-of-type(2) span::text')
        loader.add_css('description_html', '.description__text')
        yield loader.load_item()


def strip_params(url, param_names):
    parts = urlparse(url)
    params = {name: value for name, value
              in parse_qs(parts.query).items()
              if name not in param_names}
    query = urlencode(params, doseq=True)
    return urlunparse(parts._replace(query=query))


def increment_param(url, param_name, inc=1):
    parts = urlparse(url)
    params = parse_qs(parts.query)
    params.setdefault(param_name, ['0'])
    params[param_name] = str(int(params[param_name][0]) + inc)
    query = urlencode(params, doseq=True)
    return urlunparse(parts._replace(query=query))


class Loader(ItemLoader):
    default_output_processor = TakeFirst()
    employment_types_in = MapCompose(str.lower, split)
    employment_types_out = Identity()
    posted_at_in = Compose(first, parse_relative_time)
    experience_levels_in = MapCompose(str.lower, split)
    experience_levels_out = Identity()
