'''
Created on 2014-8-7

@author: 596572
'''
from utils import load_data
from scrapy.selector import Selector


def proxies_fetch():

    url = 'http://free-proxy-list.net/'
    _anonymity_levels = ['elite proxy']
    data = load_data(url=url)
    hxs = Selector(text=data)
    proxy_nodes = hxs.xpath('//table[@id="proxylisttable"]//tr')
    proxies = []
    if proxy_nodes:
        for proxy_node in proxy_nodes:
            anonymity_level = proxy_node.xpath('./td[position() = 5]/text()').extract()
            if not anonymity_level:
                continue
            anonymity_level = anonymity_level[0].strip()
            if not anonymity_level in _anonymity_levels:
                continue
            ip = proxy_node.xpath('./td[position() = 1]/text()').extract()[0].strip()
            port = proxy_node.xpath('./td[position() = 2]/text()').extract()[0].strip()
            proxy = 'http://' + ip + ':' + port
            proxies.append(proxy)
    return proxies

