import urllib.parse
import bs4
import csv
import re
import pandas as pd
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import jellyfish
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


NUTRITION_INFO = ['calories', 'trans fat', 'total fat',
                  'saturated fat', 'sodium', 'cholesterol',
                  'carbohydrate', 'dietary fiber',
                  'protein', 'total sugars']

LABELS = ['vegan', 'gluten free', 'kosher', 'dairy free', 'organic']
DAIRY_KEY = ['milk', 'cream', 'cheese', 'curd', 'custard', 'rennet']


def split(txt, seps):
    '''
    Split a string (txt) by the elements from a 
    list of separation strings (seps)

    Inputs:
        txt (a string)
        seps (a list of strings)
    Output:
        A list of strings
    '''
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]


def get_sp(browser, url):
    '''
    Get the generated soup object from the html of a url
    '''
    browser.get(url)
    html = browser.page_source
    sp = BeautifulSoup(html, 'lxml')
    return sp


def get_label_list(label):
    '''
    Extract all the products from webpages that store 
    specialized food items with particular labels.

    Input: 
        label(a string)

    Output:
        a list of strings (the names of products)
    '''
    browser = webdriver.Chrome(ChromeDriverManager().install())
    url = 'https://www.traderjoes.com/dietary-lists/' + label
    sp = get_sp(browser, url)
    all_div = sp.find_all(
        'div', style=\
        "columns: 2 325px; -moz-columns: 2 325px; -webkit-columns: 2 325px;")
    item_list = []
    for div in all_div:
        info = div.get_text().split('\n')
        for item in info:
            stan_item = ' '.join(item.split())
            if stan_item != '':
                item_list.append(stan_item)
    browser.close()
    return item_list

def get_label_dic(LABELS):
    label_dic = {}
    for l in LABELS[:3]:
        label = '-'.join(l.split())
        label_dic[l] = get_label_list(label)
    return label_dic


def check_name(name, label):
    '''
    Extract potential labels of a product by checking the name
    of the product

    Inputs:
        name (a string)
        label (a string)
    Output:
        boolean
    '''
    if 'free' in label:
        label1 = '-'.join(label.split())
        if (label in name) or (label1 in name):
            return True
    else:
        if label in name:
            return True


def get_labels(name, ing_info, label_dic):
    '''
    Label the products by checking the names,
    checking the list extracted from the specialized products
    and checking the ingredient information.

    Inputs:
        name (a string)
        ing_info (a string)
    '''
    label_set = set([])
    for l in LABELS:
        if check_name(name, l):
            label_set.add(l)

    for l in LABELS[:3]:
        if l not in label_set:
            for item in label_dic[l]:
                v = jellyfish.jaro_winkler(name, item)
                if v > 0.97:
                    label_set.add(l)
                    break
    for k in DAIRY_KEY:
        dairy_free = True
        if k in ing_info:
            dairy_free = False
            break

    if dairy_free:
        label_set.add('dairy free')

    if len(label_set) == 0:
        return None

    return label_set


def process(sp, index, label_dic):
    '''
    Extract desired information from the soup object.

    Inputs:
        sp(a soup object)
        index(boolean): whether the crawling 
                        is performed by changing indices
    Output:
        a dictionary that stores the desired information
    '''

    d = {}

    if index:
        name = ' '.join(sp.find('div',class_="article featured").get_text().\
            split()).lower()
        d['name'] = split(name,[' add'])[0].strip()
    else:
        name =  sp.title.get_text().split('|')[0].strip()
        d['name'] = name
    
    d['store'] = 'Trader Joes'
    all = sp.get_text()
        
    if 'INGREDIENTS:' in all:
        ing_nut_info = ''.join(all.split('INGREDIENTS:')[1:])
    else:
        return d
      
    if 'varies by region' in ing_nut_info.lower():
        return d
    if 'NUTRITION FACTS:' in all:
        ing_info = ing_nut_info.split('NUTRITION FACTS:')[0].lower().strip().\
        title()
        d['ing_info'] = ing_info
    else:
        return d
    nut_info = ''.join(ing_nut_info.split('NUTRITION FACTS:')[1:]).\
    split('tells you')[0].lower().title()
    for nut in NUTRITION_INFO:
        key = '_'.join(nut.split())
        if nut in nut_info:
            num_list = re.findall('\d+',nut_info.split(nut)[1].split(',')[0])
            if len(num_list) != 0:
                d[key] =  float(num_list[0])
            else:
                d[key] = 0
        else:
            d[key] = 0
    
    if not ('vari' or 'vaired') in nut_info.split('|')[0] :
        d['serve_ct'] = float(re.findall('\d+',nut_info)[0])
        
    if 'serv. size:' in nut_info:
        d['serve_size'] = nut_info.split('serv. size:')[1].split(',')[0].strip()
    else:
        if 'serving size' in nut_info:
            d['serve_size'] = nut_info.split('serving size')[1].split('|')[0].\
            strip() 
    
    d['labels'] = get_labels(name, ing_info, label_dic)
        
    return d



class TraderJoesCrawler(object):

    def __init__(self):
        self.stores = None
        self.byindex = None
        self.bydigin = None
        self.bylabel = None
        self.final = None

    def get_stores(self, url):
        '''
        Extract the location information of trader joe
        stores in a certain area, specified by the url
        '''
        source = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(source, 'lxml')

        rv = []
        dic = {'name':[], 'address':[], 'city':[], 'state':[], 'zipcode':[]}
        temp = soup.findAll('script', type="application/ld+json")
        for s in temp[1:]:
            s = json.loads(s.get_text())
            i = s['address']
            dic['name'].append('trader joes')
            dic['address'].append(i['streetAddress'])
            dic['city'].append(i['addressLocality'])
            dic['state'].append(i['addressRegion'])
            dic['zipcode'].append(i['postalCode'])

        df = pd.DataFrame(dic)
        with open('TJ_store.csv', 'w') as f:
            df.to_csv(path_or_buf=f, index=True)

        return df

    def get_byindex(self, num, label_dic):
        '''
        Access the first data set in Trader Joes by 
        the indices of the products and get the product
        information. Process the information and collect
        desired ones in a dataframe.
        Input: 
            num: number of pages crawled
        Output: 
            a dataframe
        '''
        browser = webdriver.Chrome(ChromeDriverManager().install())

        i = 4730
        ct = 0

        indx_dic = []
        while i <= 6000 and ct < num:
            url = 'https://www.traderjoes.com/fearless-flyer/article/' + str(i)
            browser.get(url)
            html = browser.page_source
            sp = BeautifulSoup(html, 'lxml')
            if 'Article' in sp.title.get_text():
                product = process(sp, True, label_dic)
                product['index'] = i
                indx_dic.append(product)
                ct += 1
            i += 1
        browser.close()

        df_indx = pd.DataFrame(indx_dic)

        return df_indx

    def get_bydigin(self, num, label_dic):
        '''
        Access the second data set in Trader Joes by 
        the digin posts and get the product
        information. Process the information and collect
        desired ones in a dataframe. 

        Input: 
            num: number of pages crawled (each page may
                generate several products)
        Output: 
            a dataframe
        '''
        browser = webdriver.Chrome(ChromeDriverManager().install())
        pg = 1
        name_set = set([])
        ct = 0

        while pg <= 42 and ct < num:
            url = 'https://www.traderjoes.com/digin/page/' + str(pg)
            browser.get(url)
            html = browser.page_source
            sp = BeautifulSoup(html, 'lxml')
            for link in sp.find_all('a'):
                if '/post/' in link.get('href'):
                    name = link.get('href').split('/post/')[1]
                    name_set.add(name)
            pg += 1
            ct += 1

        digin_dic = []

        for n in name_set:
            url = 'https://www.traderjoes.com/digin/post/' + n
            browser.get(url)
            html = browser.page_source
            sp = BeautifulSoup(html, 'lxml')
            digin_dic.append(process(sp, False, label_dic))

        browser.close()
        df_digin = pd.DataFrame(digin_dic)

        return df_digin

    def get_bylabel(self, label_dic):
        '''
        Access the third data set in Trader Joes by 
        the specified products and get the product
        information. Process the information and collect
        desired ones in a dataframe. 

        Output: 
            a dataframe
        '''

        label_prds_dic = {}
        for key in label_dic:
            product_list = label_dic[key]
            for item in product_list:
                if item in label_prds_dic:
                    label_prds_dic[item].add(key)
                else:
                    label_prds_dic[item] = set([key])
                for l in LABELS:
                    if l in item:
                        label_prds_dic[item].add(l)

        df_label = pd.DataFrame.from_dict([label_prds_dic]).T
        df_label.reset_index(inplace=True)
        df_label['store'] = 'Trader Joes'
        df_label = df_label.rename(columns={"index": "name", 0: "labels"})

        return df_label

    def get_final(self, l):
        '''
        Merge the dataframe collected from different sources
        into a big one
        Input: 
            a list of dataframes
        Output: 
            a dataframe
        '''
        df_tj = pd.concat(l, sort=False)
        df_tj = df_tj.drop(columns='index')
        df_tj = df_tj.drop_duplicates(subset=['name'])
        return df_tj

def go(test, run_stores, item_idx, pg_digin, run_label):
    '''
    The test function for crawling over Trader Joes.

    Inputs: 
        test (boolean): whether to perform a partial test
                        or the entire procedure of crawling
        run_stores(boolean): whether to collect the location
                        information of relevant stores
        item_idx (int): The number of crawlings performed by
                        accessing products of different indces
        pg_digin(int): The number of crawlings performed by
                        accessing products from digin pages
        run_label(boolean): whether to collect products from 
                        the source that store specialized items
    Output:
        A TraderJoesCrawler Object
    '''
    tj = TraderJoesCrawler()
    label_dic = get_label_dic(LABELS)
    if test:
        if run_stores:
            tj.stores = tj.get_stores(
                'https://locations.traderjoes.com/il/chicago/')
            print('Trader Joes store list is complete.')

        tj.byindex = tj.get_byindex(item_idx, label_dic)
        tj.bydigin = tj.get_bydigin(pg_digin, label_dic)

        if run_label:
            tj.bylabel = tj.get_bylabel(label_dic)
            tj.final = tj.get_final([tj.byindex, tj.bydigin, tj.bylabel])
        else:
            tj.final = tj.get_final([tj.byindex, tj.bydigin])

        with open('TJ_test.csv', 'w') as f:
            tj.final.to_csv(path_or_buf=f, index=True)

        for prod in tj.final.iterrows():
            print(prod)
        print('Trader Joes product info is complete.')

    else:
        tj.stores = tj.get_stores(
            'https://locations.traderjoes.com/il/chicago/')
        print('Trader Joes store list is complete.')
        tj.byindex = tj.get_byindex(1000, label_dic)
        tj.bydigin = tj.get_bydigin(100, label_dic)
        tj.bylabel = tj.get_bylabel(label_dic)
        tj.final = tj.get_final([tj.byindex, tj.bydigin, tj.bylabel])

        with open('TJ_prod.csv', 'w') as f:
            tj.final.to_csv(path_or_buf=f, index=True)

        print('Trader Joes product info is complete.')

    return tj


# Example:
# Run the test instead of the entire dataset (True)
# Get the store information (True)
# Get 30 product items (not necessarily food) by crawling over the index
# Get all food items stored in 5 pages of digin posts
# Do not get food items generated from the label pages (False)

# tj = go(True, True, 30, 5, False)


# You may check the output dataframe by calling:
# tj.final
