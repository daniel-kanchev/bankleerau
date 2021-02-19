import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankleerau.items import Article


class LeerauSpider(scrapy.Spider):
    name = 'leerau'
    start_urls = ['https://www.bankleerau.ch/ueber-uns/aktuell-news/']

    def parse(self, response):
        links = response.xpath('//a[@class="more"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('(//div[@id="crumbpath"]//a)[last()]/text()').get()
        if title:
            title = title.strip()
        else:
            return

        date = response.xpath('//span[@class="news-list-date"]//text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%d.%m.%Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="news-text-wrap"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
