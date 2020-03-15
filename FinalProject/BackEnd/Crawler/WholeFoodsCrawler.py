from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import ast
import bs4
import time
import re


def scroll_page(browser):
    """Automatically control to scroll the webpage to the bottom."""
    SCROLL_PAUSE_TIME = 1

    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = browser.execute_script(
            "return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return None


def get_links(source):
    """Retrive links of all products appear in one webpage source."""
    soup = bs4.BeautifulSoup(source, features="lxml")
    domain = "https://products.wholefoodsmarket.com"
    contents = soup.find_all(name="a", class_="ProductCard-Root--3g5WI")
    links = [domain + content.get("href") for content in contents]
    return links


def is_visible(browser, locator, timeout=30):
    """Check if an element is visible on the website"""
    try:
        ui.WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located((By.XPATH, locator)))
        return True
    except TimeoutException:
        return False


class WholeFoodsCrawler(object):

    def __init__(self, test=False):
        self.stores = None
        self.store_info = []
        self.prod_links = set()
        self.maylike_links = set()
        self.all_links = set()
        self.prod = None
        self.prod_info = []
        self.results = None
        self.adds = None
        self.test = test

    def get_stores(self, kwd="Chicago"):
        """Get stores by keyword."""

        browser = webdriver.Chrome(ChromeDriverManager().install())
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
        self.stores = soup.find_all("wfm-store-details", class_="hydrated")

        for store in self.stores:
            full_adds = store.find_all(
                "div", class_="w-store-finder-mailing-address")
            add = full_adds[0].get_text()
            city = full_adds[1].get_text().split()[0][:-1]
            state = full_adds[1].get_text().split()[1]
            zipcode = full_adds[1].get_text().split()[2]
            self.store_info.append([add, city, state, zipcode])

        with open("WFStores.txt", "w") as f:
            for info in self.store_info:
                f.write(str(info) + "\n")
        return self.store_info

    def get_categ_prod_links(self):
        """Get all product links by crawling the WF product category page."""
        browser = webdriver.Chrome(ChromeDriverManager().install())
        init_url = "https://products.wholefoodsmarket.com/search?sort=relevance"
        browser.get(init_url)

        # Main-category roducts without sub-categories
        NO_SUB_CATEG = ["cheese", "seafood"]

        categ_buttons = browser.find_elements_by_class_name(
            "LandingPage-SeeAll--2PvpU")

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
            browser.get(browser.current_url)

            categ = browser.current_url.split("=")[2]

            # Case 1: main category with sub-categories
            if categ not in NO_SUB_CATEG and categ != "floral":
                sub_buttons = browser.find_elements_by_class_name(
                    "Radio-Label--1a5oe")
                sub_action = ActionChains(browser)
                # Starting from the 2nd button because the 1st directs back
                for sub_button in sub_buttons[1:]:
                    sub_action.click(sub_button).perform()
                    scroll_page(browser)
                    links = get_links(browser.page_source)
                    self.prod_links.update(links)

                    if self.test == True:
                        break

                    sub_action = ActionChains(browser)

            # Case 2: main category == "floral", just skip
            elif categ == "floral":
                pass

            # Case 3: main category without sub-categories
            else:
                scroll_page(browser)
                links = get_links(browser.page_source)
                self.prod_links.update(links)

            back_action = ActionChains(browser)
            back_button = browser.find_element_by_class_name(
                "Radio-Label--1a5oe")
            back_action.click(back_button).perform()
            init_action = ActionChains(browser)

            if self.test == True:
                break

        browser.close()

        with open("WFCategLinks.txt", "w") as f:
            for link in self.prod_links:
                f.write(str(link) + "\n")
        return self.prod_links

    def get_maylike_prod_links(self):
        """Get product links from you-may-like section in each product page."""
        DOMAIN = "https://products.wholefoodsmarket.com"

        browser = webdriver.Chrome(ChromeDriverManager().install())

        for link in self.prod_links:
            browser.get(link)

            if is_visible(browser, "//div[@class='SimilarProducts-Row--3e_Rz']"):
                links = get_links(browser.page_source)
                self.maylike_links.update(links)
            else:
                pass

        browser.close()

        with open("WFMaylikeLinks.txt", "w") as f:
            for link in self.maylike_links:
                f.write(str(link) + "\n")

        return self.maylike_links

    def get_all_links(self):
        """Combine product links from category and you-may-like."""
        self.all_links = set(self.prod_links).union(set(self.maylike_links))

        with open("WFAllLinks.txt", "w") as f:
            for link in self.all_links:
                f.write(str(link) + "\n")
        return self.all_links

    def get_prod_info(self):
        """Get detailed information of each product."""
        browser = webdriver.Chrome(ChromeDriverManager().install())

        for link in self.all_links:
            browser.get(link)

            if is_visible(browser, "//div[@class='Product-Disclaimer--3ZGiZ']"):
                time.sleep(1)
                try:
                    ing_nu_buttons = browser.find_elements_by_class_name(
                        "Collapsible-Root--3cwwH")

                    ing_button = ing_nu_buttons[0]
                    ing_action = ActionChains(browser)
                    ing_action.click(ing_button).perform()

                    nu_button = ing_nu_buttons[1]
                    nu_action = ActionChains(browser)
                    nu_action.click(nu_button).perform()
                except Exception:
                    # No ingredients or nutrition
                    pass

                try:
                    detail_button = browser.find_element_by_class_name(
                        "Collapsible-Title--30gLK disable-click-focus")
                    detail_action = ActionChains(browser)
                    detail_action.click(detail_button).perform()
                except Exception:
                    # No product details
                    pass

            soup = bs4.BeautifulSoup(browser.page_source, features="lxml")

            prod_dic = dict()

            # Name
            try:
                prod_nm = soup.find(
                    "h1", class_="ProductHeader-Name--1ysBV").get_text()
                prod_dic["product name"] = prod_nm
            except Exception:
                prod_dic["product name"] = None

            # Ingredients from product details
            try:
                ingrds = soup.find(
                    "div", class_="Product-CollapsibleStatement--1VluS").get_text()
                prod_dic["ingredients"] = ingrds
            except Exception:
                prod_dic["ingredients"] = None

            # Ingredients
            try:
                ingrds = soup.find(
                    "div", class_="Product-SecondaryText--wF9l_").get_text()
                prod_dic["ingredients"] = ingrds
            except Exception:
                prod_dic["ingredients"] = None

            # Serving size
            try:
                serv_size_contents = soup.find(
                    "div", class_="Row__15gM6 NutritionTable-ServingInfo--3UL4q")
                for i in serv_size_contents:
                    serv_size = i.get_text()
                prod_dic["serving size"] = serv_size
            except Exception:
                prod_dic["serving size"] = None

            # How many servings per container
            try:
                servs_num = soup.find(
                    "div", class_="NutritionTable-ServingsPerContainer--1nUJT").get_text().split()[0]
                prod_dic["servings per container"] = servs_num
            except Exception:
                prod_dic["servings per container"] = None

            # Nutrition fact
            try:
                contents = soup.find_all("div", class_="Row__15gM6")
                for line in contents[1:]:
                    line = line.get_text()
                    try:
                        REG_EXR2 = r"([^0-9]*)(([0-9][.])?[0-9]+)([a-z]*)"
                        nutri = re.search(REG_EXR2, line).group(1)
                        quant = re.search(REG_EXR2, line).group(2)
                        if len(quant) != 0 and nutri != "Serving Size":
                            key = nutri
                            prod_dic[key] = quant
                    except Exception:
                        pass
            except Exception:
                pass

            # Dietary labels
            try:
                labels = soup.find_all("div", class_="Diets-DietName--1T3K1")
                prod_dic["labels"] = set()
                for label in labels:
                    prod_dic["labels"].add(label.get_text()
            except Exception:
                prod_dic["labels"] = None

            self.prod_info.append(prod_dic)
        browser.close()

        with open("WF_results.txt", "w") as f:
            for info in self.prod_info:
                f.write(str(info))

        return self.prod_info

    def clean(self):
        """Clean the craweled data."""

        # Products
        for dic in self.prod_info:
            for key in dic:
                if dic[key] == set():
                    dic[key] == None
        orig = pd.DataFrame(self.prod_info[0]).iloc[0]
        for d in self.prod_info[1:]:
            try:
                new_series = pd.DataFrame(d).iloc[0]
            except ValueError:
                new_series = pd.DataFrame(d, index=[0]).iloc[0]
            orig = pd.concat([orig, new_series], axis=1,
                             ignore_index=True, sort=False)
        COLS = ["product name", "ingredients", "calories", "trans fat", "saturated fat", "total fat", "sodium", "cholesterol",
                "total carbohydrates", "dietary fiber", "protein", "sugars", "labels", "serving size", "servings per container"]
        self.results = orig.T[COLS]
        self.results["store"] = "Whole Foods"
        self.results.to_csv("WFProducts.csv")

        # Stores
        self.adds = pd.DataFrame(self.stores)
        self.adds.columns = ["add", "city", "state", "zipcode"]
        self.adds.to_csv("WFStores.csv")
        return self.results, self.adds


def go(test=False, num=None):
    """Run the WholeFoods product spider."""
    wf = WholeFoodsCrawler(test)

    print("Getting Whole Foods stores...")
    wf.stores = wf.get_stores("Chicago")
    print('Whole Foods Store List Is Completed')
    print("Getting Whole Foods products...")
    wf.prod_links = wf.get_categ_prod_links()

    if test:
        wf.prod_links = list(wf.prod_links)[:num]

        wf.maylike_links = wf.get_maylike_prod_links()
        wf.all_links = list(wf.get_all_links())[:num]
        wf.prod_info = wf.get_prod_info()
        wf.results, wf.adds = wf.clean()
        for prod in wf.results.iterrows():
            print(prod)
    else:
        wf.maylike_links = wf.get_maylike_prod_links()
        wf.all_links = wf.get_all_links()
        wf.prod_info = wf.get_prod_info()
        wf.results, wf.adds = wf.clean()
