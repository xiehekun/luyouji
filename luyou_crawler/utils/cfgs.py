# encoding: utf-8
# Created on 2014-8-4
# @author: binge
import settings

'''
    some configs, like relation with zh_name and en_name, en_name base on qyer.com.
'''
qy_china_region_names = {
                "澳门" : "Macau",
                "淡水" : "Tamsui",
                "高雄市" : "Kaohsiung City",
                "恒春" : "Hengchun",
                "花莲县" : "Hualien County",
                "嘉义" : "Chiayi",
                "基隆市" : "Keelung City",
                "金瓜石" : "Jinguashi",
                "金门县" : "Kinmen County",
                "九份" : "Jioufen",
                "垦丁" : "Kenting",
                "兰屿" : "Orchid Island",
                "琉球屿" : "Liouciou",
                "鹿港" : "Lukang",
                "绿岛" : "Green Island",
                "马祖" : "Matsu",
                "苗栗县" : "Miaoli County",
                "南投县" : "Nantou County",
                "澎湖县" : "Penghu County",
                "屏东县" : "Pingtung County",
                "平溪"  : "Pingxi",
                "台北" : "Taipei",
                "台东县" : "Taitung County",
                "太鲁阁国家公园" : "Taroko National Park",
                "台南" : "Tainan",
                "台中市" : "Taichung City",
                "桃园县" : "Taoyuan County",
                "香港" : "Hong Kong",
                "新竹" : "Hsinchu",
                "宜兰县" : "Yilan County",
                "云林县" : "Yunlin County",
                "彰化县" : "Changhua County",
                "台湾" : "Taiwan",
                "台湾离岛" : "Taiwan Offshore Islands",
                "新北市" : "New Taipei City"
                }

mfw_qy_points_recorrspond = {
                             settings.mfw_region_crawl_cy : settings.qyer_region_crawl_food,
                             settings.mfw_region_crawl_jd : settings.qyer_region_crawl_sight,
                             settings.mfw_region_crawl_gw : settings.qyer_region_crawl_shopping
                             }

def chinese_region_en_name(zh_name):
    '''
    just get the Chinese region en_name which in qyer.com but not in other site.
    '''
    if zh_name in qy_china_region_names:
        return qy_china_region_names[zh_name]
    else:
        return ''

def mfw_point_db_name(mfw_point):
    return mfw_qy_points_recorrspond[mfw_point]
