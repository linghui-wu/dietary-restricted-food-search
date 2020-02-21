from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import bs4
import time
import re


def get_stores(kwd="Chicago"):
    """
    Get raw store information by keywords.
    Input:
        kwd (string): search store by zipcode, city or state
    Output:
        stores (BS4 object): raw infomation of all the stores
    """
    browser = webdriver.Chrome()
    try:
        init_url = "https://www.wholefoodsmarket.com/stores"
        browser.get(init_url)
        search_input = browser.find_element_by_class_name(
            "wfm-search-bar--input")
        search_input.clear()
        search_input.send_keys(kwd)
        time.sleep(1)
        search_input.send_keys(Keys.RETURN)
        time.sleep(1)
        search_input.send_keys(Keys.RETURN)

        source = browser.page_source
    finally:
        browser.close()

    soup = bs4.BeautifulSoup(source, features="lxml")
    stores = soup.find_all("wfm-store-details", class_="hydrated")
    return stores


def get_store_info(store):
    """
    Get detaled information of each store.
    Input:
        store (BS4 object): row information of a particular store
    Output:
        [nbhd, add, city, state, zip_code] (list):
                - nbhd: which neighborhood the store belongs to
                - add: detailed address of the store
                - city: which city the store locates
                - state: which state the store locates
    """
    nbhd = store.find("a", class_="w-link w-link--text").get_text().lower()
    full_adds = store.find_all("div", class_="w-store-finder-mailing-address")
    add = full_adds[0].get_text().lower()
    long_add = full_adds[1].get_text().split()
    city = long_add[0][:-1].lower()
    state = long_add[1].lower()
    zip_code = long_add[2]
    return [nbhd, add, city, state, zip_code]


def get_add_dic(kwd):
    """
    Convert the store information into a dictionary.
    Input:
        kwd (string): search store by zipcode, city or state
    Output:
        add_dic (dict): dictionaries storing store information
                - key: store index
                - value: store information
    """
    stores = get_stores(kwd)
    add_dic = {idx: get_store_info(store) for idx, store in enumerate(stores)}
    return add_dic


def scroll_page(browser):
    """
    Automatically control to scroll the webpage to the bottom.
    Input:
        browser: web driver
    Output:
        None
    """
    SCROLL_PAUSE_TIME = 1

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script(
            "return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return None


def get_prod_links(source):
    """
    Retrive product links from a web source.
    Input:
        webpage source
    Output:
        links (list): product links
    """
    soup = bs4.BeautifulSoup(source, features="lxml")
    domain = "https://products.wholefoodsmarket.com"
    contents = soup.find_all(name="a", class_="ProductCard-Root--3g5WI")
    links = [domain + content.get("href") for content in contents]
    return links


def get_categ_prod_links():
    """
    Get all product links by crawling the Whole Foods product category webpage.
    Input:
            None
    Output:
            prod_links (set): a set of the links of products from category page
    """
    prod_links = set()
    browser = webdriver.Chrome()
    init_url = "https://products.wholefoodsmarket.com/search?sort=relevance"
    browser.get(init_url)

    # Main-category roducts without sub-categories
    NO_SUB_CATEG = ["cheese", "seafood"]

    categ_buttons = browser.find_elements_by_class_name(
        "LandingPage-SeeAll--2PvpU")

    # Total number of main categories
    # Main categories and their sub categories
    # Produce
    #       Fresh Fruit
    #       Fresh Herbs
    #       Fresh Vegetables
    # Dairy & Eggs
    #       Butter & Margarine
    #       Dairy Alternatives
    #       Eggs
    #       Milk & Cream
    #       Yogurt
    # Floral
    # Cheese
    # Frozen Foods
    #       Frozen Breakfast
    #       Forzen Entrées & Appetizers
    #       Frozen Fruits & Vegetables
    #       Frozen Pizza
    #       Ice Cream & Frozen Desserts
    # Beverages
    #       Coffee
    #       Juice
    #       Kombucha & Tea
    #       Soft Drinks
    #       Sports, Energy & Nutritional Drinks
    #       Tea
    #       Water, Seltzer & Sparkling Water
    # Snacks, Chips, Salsas & Dips
    #       Candy & Chocolate
    #       Chips
    #       Cookies
    #       Crackers
    #       Jerky
    #       Nutrition & Granola Bars
    #       Nuts, Puffs, & Rice Cakes
    #       Salsas, Dips, & Spreads
    # Pantry Essentials
    #       Baking
    #       Canned Goods
    #       Condiments & Dressings
    #       Jam, Jellies & Nut Butters
    #       Pasta & Noodles
    #       Rice & Grains
    #       Sauces
    #       Soups & Broths
    #       Spices & Seasonings
    # Breads, Rolls, & Bakery
    #       Breads
    #       Breakfast Bakery
    #       Dessers
    #       Rolls & Buns
    #       Tortillas & Flat Breads
    # Breakfast
    #       Cereal
    #       Hot Cereal & Pancake Mixes
    # Beef, Poultry & Pork
    #       Deli Meat
    #       Hot Dogs, Bacon & Sausage
    #       Meat Alternatives
    #       Meat Counter
    #       Packaged Meat
    #       Packaged Poultry
    #       Poultry Counter
    # Seafood
    # Prepared Foods
    #       Prepared Meals
    #       Prepared Soups & Salads
    # Wine, Beer, & Spirits
    #       Beer
    #       Spirits
    #       Wine

    # Num of main categories of products = 14
    CATEG_NUM = len(categ_buttons)

    init_action = ActionChains(browser)
    for i in range(CATEG_NUM):
        init_url = "https://products.wholefoodsmarket.com/search?sort=relevance"
        browser.get(init_url)
        time.sleep(2)
        categ_buttons = browser.find_elements_by_class_name(
            "LandingPage-SeeAll--2PvpU")

        # Direct to the webpage of the main category of the food
        categ_button = categ_buttons[i]
        init_action.click(categ_button).perform()
        categ_url = browser.current_url
        browser.get(categ_url)

        categ = categ_url.split("=")[2]  # The name of the category
        print(categ)

        # Case 1: main category with sub-categories
        if categ not in NO_SUB_CATEG and categ != "floral":
            sub_buttons = browser.find_elements_by_class_name(
                "Radio-Label--1a5oe")
            sub_action = ActionChains(browser)
            # Starting from the second button because the first directs back
            for sub_button in sub_buttons[1:]:
                sub_action.click(sub_button).perform()
                scroll_page(browser)
                source = browser.page_source
                links = get_prod_links(source)
                prod_links.update(links)
                sub_action = ActionChains(browser)
                print("Number of products: ", len(links))
        # Case 2: main category == "floral", just skip
        elif categ == "floral":
            pass
        # Case 3: main category without sub-categories
        else:
            scroll_page(browser)
            source = browser.page_source
            links = get_prod_links(source)
            prod_links.update(links)
            print("Number of products: ", len(links))

        back_action = ActionChains(browser)
        back_button = browser.find_element_by_class_name("Radio-Label--1a5oe")
        back_action.click(back_button).perform()
        init_action = ActionChains(browser)
    browser.close()

    with open("pord_links.txt", "w") as f:
        for link in prod_links:
            f.write(str(link) + "\n")
    return prod_links


def is_visible(broswer, locator, timeout=30):
    """
    Check if an element is visible on the website to control the scraping.
    Inputs:
        browser (webdriver): the web browser opened using selenium
        locator (string): the particular element to check
        timeout (int): maximum waiting time defaults to 30 seconds
    Output:
        True/False (bool): whether the element appears within the given time
    """
    try:
        ui.WebDriverWait(broswer, timeout).until(
            EC.visibility_of_element_located((By.XPATH, locator)))
        return True
    except TimeoutException:
        return False


def get_may_like_prod(prod_links):
    """
    To construct a more complete list of Whole Foods product by retriving the links of you-may-like product(s) in each item's introduction webpage, because the upper limit number of products in one sub-category page is 200.
    Input:
        prod_links (iterable): the set of product links scraped from category pages
    Output:
        may_like_prod_links (set): the set of the links of you-may-like products
    """
    may_like_prod_links = set()
    DOMAIN = "https://products.wholefoodsmarket.com"
    broswer = webdriver.Chrome()
    cnt = 0
    for link in prod_links:
        broswer.get(link)

        if is_visible(broswer, "//div[@class='SimilarProducts-Row--3e_Rz']"):
            source = broswer.page_source
            soup = bs4.BeautifulSoup(source, features="lxml")
            contents = soup.find_all("a", class_="ProductCard-Root--3g5WI")
            links = [DOMAIN + c.get("href") for c in contents]
            print(cnt, " | Number of you-may-like products", len(links))
            cnt += 1
            may_like_prod_links.update(links)
        else:
            print("TIME OUT!!!!")
    broswer.close()

    with open("you-may-like_links.txt", "w") as f:
        for link in may_like_prod_links:
            f.write(str(link) + "\n")

    return may_like_prod_links


def get_all_links(prod_links, may_like_prod_links):
    """
    Combine the product links from category webpages and you-may-like product links.
    Input:
        None
    Output:
        all_prod_links (set): the links of all Whole Foods product except flowers
    """
    # prod_links = get_categ_prod_links()
    # may_like_prod_links = get_may_like_prod(prod_links)
    all_prod_links = prod_links.union(may_like_prod_links)

    # Save crawlered links into the file because selenium is so
    # time-consuming!!!
    with open("final_links.txt", "w") as f:
        for link in all_prod_links:
            f.write(str(link) + "\n")
    return all_prod_links


if __name__ == "__main__":
    # get_add_dic("boston")

    # get_categ_prod_links()
    
    prod_links = set()
    with open("pord_links.txt") as f:
        for line in f:
            prod_links.add(line)
    # may_like_prod_links = get_may_like_prod(prod_links)
    # print(len(may_like_prod_links))

    may_like_prod_links = set()
    with open("you-may-like_links.txt") as f:
        for line in f:
            may_like_prod_links.add(line)


    print(len(get_all_links(prod_links, may_like_prod_links)))
