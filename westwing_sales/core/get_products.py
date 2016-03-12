# -*- coding: utf-8 -*-
import datetime
import json
import traceback

import os
import requests
from bs4 import BeautifulSoup
from django.conf import settings

__author__ = 'mateuszdargacz@gmail.com'
__date__ = '3/12/16 / 11:56 AM'
__git__ = 'https://github.com/mateuszdargacz'

CAMPAING_DETAILS_URL_CLASS = 'campaign-item__wrapping-link'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/601.4.4 (KHTML, like Gecko) Version/9.0.3 Safari/601.4.4',
    'Referer': 'http://www.westwing.pl/campaign/',
    'Cache-Control': 'max-age=0',
    'Cookie': 'ww_uid=pimpmks%40o2.pl; optimizelyEndUserId=oeu1451915493817r0.49070222512818873; ww_jid=56e3fcc9aa3496.80226209; PHPSESSID=08o0a1e2esjqeo9neckb2m95b4; deviceName=desktop; deviceNameTS=1457781961; ww_login=1; 08b2c388d80a05b574a596507bac73d1=4dffd1159ec1113216fdc9c3adda7bac89a4035ea%3A4%3A%7Bi%3A0%3Bs%3A7%3A%221400525%22%3Bi%3A1%3Bs%3A13%3A%22pimpmks%40o2.pl%22%3Bi%3A2%3Bi%3A31536000%3Bi%3A3%3Ba%3A2%3A%7Bs%3A14%3A%22isPartialLogin%22%3Bb%3A1%3Bs%3A19%3A%22lastLoginFromDevice%22%3Bi%3A1457781961%3B%7D%7D; YII_CSRF_TOKEN=c2a4445f1e86fda5320819d1c6c5ba625649d8cd;'
}
URI = 'http://www.westwing.pl'


class MagicEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Product, ProductSet)):
            a = obj.to_JSON()
            return a
        else:
            return super(MagicEncoder, self).default(obj)


class Product(object):
    name = ''
    url = ''
    image = ''
    price = 0
    sale = 0

    @property
    def sale_percentage(self):
        return round(((self.price - self.sale) / self.price) * 100, 2)

    def __str__(self):
        return '%s: sale: %s%% price:%s ->%s' % (self.name, self.sale_percentage, self.price, self.url)

    def __repr__(self):
        return '%s: sale: %s%% price:%s ->%s' % (self.name, self.sale_percentage, self.price, self.url)

    def to_JSON(self):
        sale_percentage = self.sale_percentage
        return dict(
            name=self.name,
            url=self.url,
            image=self.image,
            price=self.price,
            sale=self.sale,
            sale_percentage=sale_percentage
        )


class ProductSet(object):
    products = set()

    def add(self, *args):
        self.products.add(*args)

    def __init__(self):
        self.products = set()

    @property
    def ordered(self):
        return sorted(self.products, key=lambda x: x.sale_percentage, reverse=True)[:settings.MAX_FROM_CAMPAIGN]

    @property
    def average_percent(self):
        ordered = self.ordered
        if len(ordered):
            return round(sum([prod.sale_percentage for prod in ordered]) / float(len(ordered)), 2)

    def to_JSON(self):
        average_percent = self.average_percent
        print(list(x.get('sale_percentage') for x in [prod.to_JSON() for prod in self.ordered]))
        print('^' * 30)
        return dict(
            ordered=self.ordered,
            average_percent=average_percent
        )

    def __repr__(self):
        return str(len(self.products))


def get_campaign_products(campaign_url):
    url = URI + campaign_url
    res = requests.get(url, headers=HEADERS)
    selector = BeautifulSoup(res.content, 'html.parser')
    products = selector.find_all('article', class_='product-item')
    product_set = ProductSet()
    for prod in products:
        product = Product()
        product.name = prod.find('h2', class_='product-item__title').text
        product.url = URI + prod.find('a', class_='product-item__wrapping-link').get('href')
        product.image = prod.find('img', class_='product-item__image').get('src')
        product.price = round(
            float(prod.find('span', class_='product-item__price--original').text.strip().replace(',-', '')), 2)
        product.sale = round(float(
            prod.find('span', class_='product-item__price--our').text.strip().replace(',-', '').replace('od    ',
                '')), 2)
        product_set.add(product)
    product_set.products = set(product_set.ordered)
    return product_set


def get_all_products():
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'products.json')
    campaign_products = dict()
    days_ago = 0
    try:
        stats = os.stat(cache_path)
        mtime = datetime.datetime.fromtimestamp(stats.st_mtime)
        now = datetime.datetime.now()
        days_ago = (now - mtime).days
    except:
        pass
    if os.path.exists(cache_path) and days_ago < 1:
        campaign_products = json.load(open(cache_path, 'r'))
    else:
        res = requests.get(URI + '/campaign/', headers=HEADERS)
        selector = BeautifulSoup(res.content, 'html.parser')
        campaigns = selector.find_all('a', class_=CAMPAING_DETAILS_URL_CLASS)
        for campaign in campaigns:
            campaign_name = campaign.find('div', class_='campaign-item__title-text').text
            product_set = get_campaign_products(campaign.get('href'))
            campaign_products.update({
                campaign_name: product_set
            })
        with open(cache_path, 'w+') as prod_file:
            json.dump(campaign_products, prod_file, cls=MagicEncoder)
    return campaign_products
