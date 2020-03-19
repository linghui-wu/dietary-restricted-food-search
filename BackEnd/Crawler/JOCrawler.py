import re
import time
import json
import requests
import csv
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs


class JOCrawler(object):

    def __init__(self, num=None, test=False):
        '''
        If want to test the crawler, please input test=True and the number
        of items you want to get
        '''
        self.item_ids = []
        self.label_dict = {}
        self.label_list = ['organic', 'gluten_free',
                           'fat_free', 'vegan', 'kosher', 'sugar_free']
        self.dep_links = []
        self.num = num
        self.test = test

    def get_body(self, browser):
        '''
        Get the body of the browser
        ''' 
        Pagelength = browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        source = browser.page_source
        data = bs(source, 'lxml')
        body = data.find('body')
        return body

    def get_item_ids(self, browser, num_scroll):
        '''
        Get the index of items in the departments
        '''
        scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
        Pagelength = browser.execute_script(scroll_down)
        item_ids = []
        for i in range(num_scroll):
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        source = browser.page_source
        data = bs(source, 'lxml')
        body = data.find('body')
        for cnt, item in enumerate(body.find_all('div', attrs=\
            {'class': 'item-info'})):
            if item['id'] not in item_ids and 'undefined' not in item['id']:
                item_ids.append(item['id'][14:])
                if self.num:
                    if (cnt + 1) >= self.num:
                        break
        item_ids = set(item_ids)
        return list(item_ids)

    def build_item_csv(self, browser, domain, file_name):
        '''
        Build csv file for the items' information
        '''
        with open(file_name, mode='w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(('id', 'name', 'ingred', 'calories', 'trans_fat',
                             'satu_fat', 'tot_fat', 'sodium', 'cholestreol', \
                             'tot_carhy','diet_fiber', 'protein', 'sugar', \
                             'labels', 'serv_size','tot_serv', 'store'))
            for i in self.item_ids:
                browser.get(domain + 'items/item_' + i)
                time.sleep(5)
                body = self.get_body(browser)
                if body.find_all('h3'):
                    if not body.find_all('h3')[-1].text == 'Nutrition Facts':
                        continue
                    for header in body.find_all('h3'):
                        if header.text == 'Ingredients':
                            ing_info = header.nextSibling()[0].text
                        else:
                            ing_info = ''
                    name = body.find_all('h2')[0].text
                    serve_size = body.find_all(
                        'h3')[-1].findParent().div.text[13:]
                    serve_num = body.find_all(
                        'h3')[-1].findParent().text.split()[-1]
                    if serve_num.isdigit():
                        serve_num = float(serve_num)
                    else:
                        serve_num = ''
                    nut_dict, nut_info = self.build_nut_dict(body.find_all(
                        'h3')[-1].findParent().findParent().find_all('li'))
                    label = [k for k, v in self.label_dict.items() if i in v]
                    writer.writerow((i, name, ing_info,
                                     nut_dict.get('Calories', 0),
                                     nut_dict.get('Trans Fat', 0),
                                     nut_dict.get('Saturated Fat', 0),
                                     nut_dict.get('Total Fat', 0),
                                     nut_dict.get('Sodium', 0),
                                     nut_dict.get('Cholesterol', 0),
                                     nut_dict.get('Total Carbohydrate', 0),
                                     nut_dict.get('Dietary Fiber', 0),
                                     nut_dict.get('Protein', 0),
                                     nut_dict.get('Sugars', 0),
                                     label, serve_size, serve_num, \
                                     'Jewel Osco'))

    def build_nut_dict(self, nutrition_facts):
        '''
        Build the nutrition dictionary for each item
        '''
        nut_dict = {}
        nut_info = []
        for label in nutrition_facts:
            label = label.get_text()
            try:
                reg = re.search("([^0-9]*)(([0-9][.])?[0-9]+)([a-z]*)", label)
                nut_dict[reg.group(1).strip()] = float(reg.group(2))
                nut_info.append(reg.group(1).strip() + " " +
                                reg.group(2) + reg.group(4))
            except Exception:
                pass
        return nut_dict, ",".join(nut_info)

    def get_labels(self, cat_link, browser):
        '''
        Get the dictionary of labels for the items in each department
        '''
        for label in self.label_list:
            browser.get(cat_link + "?nutrition%5B%5D={}".format(label))
            time.sleep(5)
            self.label_dict[label] = self.label_dict.get(
                label, []) + self.get_item_ids(browser, 10)

    def get_store_info(self, browser):
        '''
        Get the store information of Jewel Osco in Chicago
        '''
        loc_body = self.get_body(browser)
        add = loc_body.findAll('address', attrs={"class": "c-address"})
        address = []
        for i in add:
            address.append(i.text)
        with open('JOSCO_store.csv', mode='w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(
                ('zipcode', 'city', 'state', 'address', 'name', 'id'))
            idx = 0
            for i in address:
                l = i
                i = l.replace('chicago', '')
                s = re.search(
                    "([0-9]*[^0-9]*)([,])([^0-9]*)([6][0-9][0-9][0-9][0-9])",
                    i)
                writer.writerow((s.group(4), 'chicago', s.group(
                    3), s.group(1), 'jewel osco', idx))
                idx += 1

    def get_dep_links(self, domain, body):
        '''
        Get the department links of Jewel Osco
        '''
        for link in body.findAll('a', attrs={"class": "rmq-7fc413e6"}):
            if 'aisles' not in link.get('href'):
                self.dep_links.append(domain + link.get('href'))
        self.dep_links = self.dep_links[3:9] + self.dep_links[10:18]

    def go_product(self):
        '''
        Build the csv file of product information
        '''
        url = 'https://www.instacart.com/store/jewel-osco/browse_departments'
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.get(url)
        time.sleep(30)
        browser.get(url)
        time.sleep(5)
        domain = 'https://www.instacart.com/store/'
        body = self.get_body(browser)
        self.get_dep_links(domain, body)
        if self.test:
            self.dep_links = self.dep_links[2:3]
            i = 'jo_test'
        else:
            i = 1
        for dept in self.dep_links:
            browser.get(dept)
            time.sleep(5)
            body = self.get_body(browser)
            bo = body.find_all('a')
            cate_links = set(domain + i.get('href')
                             for i in bo if 'aisles' in i.get('href'))
            cate_links = list(cate_links)
            num_scroll = 20
            if self.test:
                cate_links = cate_links[0:1]
                num_scroll = 2
            for j in cate_links:
                self.get_labels(j, browser)
                browser.get(j)
                time.sleep(5)
                self.item_ids += self.get_item_ids(browser, num_scroll)
            print('{} items'.format(len(self.item_ids)))
            self.build_item_csv(browser, domain, '{}.csv'.format(i))
            print('{}.csv is completed.'.format(i))
            if self.test:
                pass
            else:
                i += 1
        browser.close()
        if self.test:
            pass
        else:
            df_list = [pd.read_csv('{}.csv'.format(t)) for t in range(1, 15)]
            df = pd.concat(df_list)
            df.drop_duplicates('id', inplace=True)
            df.drop(axis=1, columns=['Unnamed: 0'])
            df.to_csv('JOSCO_prod.csv')

    def go_store(self):
        '''
        Build the csv file of store information
        '''
        url = 'https://local.jewelosco.com/il/chicago.html'
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.get(url)
        self.get_store_info(browser)
        browser.close()


def go(test, num):
    '''
    Run the Jewel Osco product spider
    '''
    jo = JOCrawler(num, test)
    print("Getting Jewel Osco stores...")
    jo.go_store()
    print('Jewel Osco Store List Is Completed')
    print("Getting Jewel Osco products...")
    jo.go_product()
    if test:
        prod_df = pd.read_csv('jo_test.csv')
        for i in prod_df.iterrows():
            print(i)
