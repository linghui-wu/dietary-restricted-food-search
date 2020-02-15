from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import bs4
import time


def get_stores(kwd="Chicago"):
    browser = webdriver.Chrome()
    try:
        url = "https://www.wholefoodsmarket.com/stores"
        browser.get(url)
        search_input = browser.find_element_by_class_name(
            "wfm-search-bar--input")
        search_input.clear()
        search_input.send_keys(kwd)
        time.sleep(10)
        search_input.send_keys(Keys.RETURN)
        time.sleep(5)
        search_input.send_keys(Keys.RETURN)

        source = browser.page_source
    finally:
        browser.close()

    soup = bs4.BeautifulSoup(source, features="lxml")
    stores = soup.find_all("wfm-store-details", class_="hydrated")
    return stores


def get_info(store):
    nbhd = store.find("a", class_="w-link w-link--text").get_text()
    full_adds = store.find_all("div", class_="w-store-finder-mailing-address")
    add = full_adds[0].get_text()
    long_add = full_adds[1].get_text().split()
    city = long_add[0][:-1]
    state = long_add[1]
    zip_code = long_add[2]
    add_info = [add, city, state, zip_code]
    return nbhd, add_info


def get_add_dic(kwd):
    stores = get_stores(kwd)
    add_dic = dict()
    for store in stores:
        k, v = get_info(store)
        add_dic[k] = v

    return add_dic

if __name__ == "__main__":
    kwd = "illinois"
    print(len(get_add_dic(kwd)))
    print(get_add_dic(kwd))
