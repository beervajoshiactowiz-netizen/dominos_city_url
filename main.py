from extract import parser,parser_data
from models import Urls,Outlet
from db_config import create_table,insert_into_db,fetch_url
from pydantic import ValidationError
import threading
from utils import load
import time

file="dominos.html"
url_table_name="city_url"
outlet_table_name="outlets"
MAX_WORKERS = 10


def main():
    create_table(url_table_name,outlet_table_name)
    url_data=parser()
    validated_url=[]
    for url in url_data:
        try:
            validated_url.append(Urls(**url))
        except ValidationError as e:
            print("Validation Error: ",e)
    if validated_url:
        insert_into_db(url_table_name,validated_url)

    urls = list(fetch_url(url_table_name))
    print(f"Total cities to process: {len(urls)}\n")


    total_inserted = 0
    total_skipped = 0
    results = {}
    lock = threading.Lock()

    def fetch(url):
        data = parser_data(url)
        with lock:
            results[url] = data

    for i in range(0, len(urls), MAX_WORKERS):
        batch = urls[i:i + MAX_WORKERS]
        threads = [threading.Thread(target=fetch, args=(url,)) for url in batch]

        for t in threads: t.start()
        for t in threads: t.join()

        # insert after each batch
        all_outlets = []
        for url in batch:
            for outlet in results.get(url, []):
                try:
                    all_outlets.append(Outlet(**outlet))
                except ValidationError as e:
                    total_skipped += 1
                    print(f"  Skipped: {e}")

        if all_outlets:
            insert_into_db(outlet_table_name, all_outlets)
            total_inserted += len(all_outlets)


if __name__=="__main__":
    st=time.time()
    main()
    et=time.time()
    print(et-st)