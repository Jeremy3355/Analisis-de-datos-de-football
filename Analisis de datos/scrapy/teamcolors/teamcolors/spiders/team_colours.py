import scrapy
import re

class ColorsSpider(scrapy.Spider):
    name = 'team_colours'
    allowed_domains = ['teamcolorcodes.com']
    start_urls = ['https://teamcolorcodes.com/soccer/laliga-color-codes/']
    custom_settings = {
        'FEED_URI': 'team_colours_spain.csv',
        'FEED_FORMAT': 'csv',
        'ROBOTSTXT_OBEY': True,
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def parse(self, response):
        self.log(f"Visitando la página: {response.url}")
        # Extraer los enlaces de cada equipo
        team_links = response.xpath('//div[contains(@class, "entry-content")]//a/@href').getall()
        self.log(f"Enlaces encontrados: {team_links}")

        for link in team_links:
            if link.startswith('https://teamcolorcodes.com'):
                yield response.follow(link, self.parse_team)
            else:
                full_link = response.urljoin(link)
                yield response.follow(full_link, self.parse_team)

    def parse_team(self, response):
        self.log(f"Visitando la página del equipo: {response.url}")
        team_name = response.xpath('//header[contains(@class, "entry-header")]//h1/text()').get()
        colours = response.xpath('//figure[contains(@class, "wp-block-table")]//table//tbody//tr//td/text()').getall()

        if team_name:
            team_name = team_name.replace(' Color Codes', '')

        filtered_colours = list(set(elemento for elemento in colours if elemento.strip().startswith('#')))
        
        if len(filtered_colours) == 0:
            self.log(f"Visitando la página del equipo: {response.url}")
            colours = response.xpath('//div[contains(@class, "su-table")]//table//tbody//tr//td/text()').getall()
            filtered_colours = list(set(elemento for elemento in colours if elemento.strip().startswith('#')))
        
        if len(filtered_colours) == 0:
            self.log(f"Visitando la página del equipo: {response.url}")
            colours = response.xpath('//div[contains(@class, "entry-content")]//div[contains(@class, "colorblock")]//text()').getall()
            colours = [color.lower() for color in colours]
            hex_pattern = re.compile(r'hex color:\s*(#\w+);')
            filtered_colours = list(set(hex_pattern.search(elemento).group(1) for elemento in colours if hex_pattern.search(elemento)))
            
        yield {'team_name':team_name,
               'country_name':'Spain',
               'colours':filtered_colours}

# $x('//header[contains(@class, "entry-header")]//h1/text()').map(elm => elm.wholeText)
# $x('//figure[contains(@class, "wp-block-table")]//table//tbody//tr//td[contains(@class, "has-text-align-left")]/text()').map(elm => elm.wholeText)
# [contains(@class, "has-text-align-left")]