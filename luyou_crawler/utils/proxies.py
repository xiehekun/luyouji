'''
Created on 2014-8-7

@author: 596572
'''
from utils import load_data
from scrapy.selector import Selector


def proxies_fetch():

    url = 'http://free-proxy-list.net/'
    _anonymity_levels = ['elite proxy']
    _check_time_units = {
                         'seconds' : 1,
                         'minutes' : 60
                         }
    _check_time_limit = 60 * 10
    data = load_data(url=url)
    hxs = Selector(text=data)
    proxy_nodes = hxs.xpath('//table[@id="proxylisttable"]//tr')
    proxies = []
    if proxy_nodes:
        for proxy_node in proxy_nodes:
            anonymity_level = proxy_node.xpath('./td[position() = 5]/text()').extract()
            if not anonymity_level:
                continue
            check_time_str = proxy_node.xpath('./td[position() = 8]/text()').extract()
            if not check_time_str:
                continue
            check_time_s = check_time_str[0].split(' ')
            c = int(check_time_s[0])
            u = check_time_s[1]
            if u not in _check_time_units:
                continue
            if (c * _check_time_units[u]) > _check_time_limit:
                continue
            anonymity_level = anonymity_level[0].strip()
            if not anonymity_level in _anonymity_levels:
                continue
            ip = proxy_node.xpath('./td[position() = 1]/text()').extract()[0].strip()
            port = proxy_node.xpath('./td[position() = 2]/text()').extract()[0].strip()
            proxy = 'http://' + ip + ':' + port
            proxies.append(proxy)
    return proxies

