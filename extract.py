from lxml import html
import re
import gzip
import os
import requests
from utils import xpath_file

base_url="https://www.dominos.co.in"
file="xpaths.json"
XPATHS=xpath_file(file)
headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://www.dominos.co.in/store-location/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        # 'cookie': '_gcl_au=1.1.1121010527.1773899531; _gid=GA1.2.362445554.1773899533; _ga=GA1.1.1502612679.1773408617; _fbp=fb.1.1773899532647.25529123894767585; moe_uuid=005a9800-88e6-414a-9244-ee3bf6b15efa; _ga_51NSXH673Q=GS2.1.s1773899532$o1$g0$t1773899534$j58$l0$h0; _ga_CRJBK2R8LM=GS2.1.s1773899532$o1$g0$t1773899534$j58$l0$h0; _ga_KQE6QVSPD1=GS2.1.s1773899540$o2$g1$t1773899821$j34$l0$h0',
    }

def parser():
    response = requests.get("https://www.dominos.co.in/store-location/", headers=headers)
    tree = html.fromstring(response.text)
    urls=[]
    cities=tree.xpath(XPATHS["cities_path"])
    for city in cities:
        city_name=city.xpath('string(./text())').split('(')[0].strip()
        city_link=city.xpath('string(./@href)')
        url=f"{base_url}{city_link}"
        urls.append({
            "city_name":city_name,
            "url":url
        })

    return urls

def parser_data(url):
    city_name = url.rstrip('/').split('/')[-1]

    os.makedirs("html_pages", exist_ok=True)
    file_path = f"html_pages/{city_name}.html.gz"

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    if not os.path.exists(file_path):
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            f.write(response.text)
        print(f"  Saved backup: {file_path}")
    else:
        print(f"  Backup exists, skipping save: {file_path}")


    tree = html.fromstring(response.text)
    return extract_data(tree, city_name)


def extract_data(tree,city_name):
    result = []

    outlets_path=tree.xpath(XPATHS["outlets_path"])

    for outlets in outlets_path:
        address= outlets.xpath(XPATHS["address_path"]).strip()
        city_match=city_name
        pincode=re.search(r'\b(\d{6})\b', address)
        if pincode:
            pincode=pincode.group(1)

        outlet_dict={
            "OutletName":outlets.xpath(XPATHS['outletName_path']).strip(),
            "area":outlets.xpath(XPATHS["area_path"]).strip(),
            "address":address,
            "city":city_match,
            "pincode":pincode,
            "DeliveryTime":outlets.xpath(XPATHS["deliveryTime_path"]).strip(),
            "Cost":outlets.xpath(XPATHS["cost_path"]),
            "timing":outlets.xpath(XPATHS["timing_path"]).strip(),
            "Status":outlets.xpath(XPATHS["status_path"]).strip(),
            "goodFor":outlets.xpath(XPATHS["goodFor_path"]).strip(),
            "phone":outlets.xpath(XPATHS["phone_path"]),
            "StoreUrl":"https://www.dominos.co.in" + str(outlets.xpath(XPATHS["storeUrl_path"]).strip()),
            "menuUrl":outlets.xpath(XPATHS["menuUrl_path"])
        }
        result.append(outlet_dict)

    return result