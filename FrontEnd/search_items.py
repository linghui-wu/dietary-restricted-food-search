import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'foodsearch.sqlite3')


def search(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns products
    that match the criteria.

    Returns a pair: an ordered list of attribute names and a list the
     containing query results.  Returns ([], []) when the dictionary
     is empty.
    '''
    assert isinstance(args_from_ui, dict)
    conn = sqlite3.connect("foodsearch.sqlite3")
    c = conn.cursor()


    if args_from_ui:
        select = make_select(args_from_ui)
        from_ = make_from(args_from_ui)
        query, param = make_condition(args_from_ui)
        c.execute(select + from_ + " AND ".join(query), param)
        return (get_header(c), c.fetchall())
    conn.close()
    # If no argument passed in, return empty lists
    return ([], [])

def make_select(args_from_ui):
    base = "SELECT "
    select = ["product.name", "store.name", "store.address"]
    if 'calories' in args_from_ui:
        select.append("product.calories")
    if 'trans_fat' in args_from_ui:
        select.append("product.trans_fat")
    if 'tot_fat' in args_from_ui:
        select.append("product.tot_fat")
    if 'sodium' in args_from_ui:
        select.append("product.sodium")
    if 'tot_carhy' in args_from_ui:
        select.append("product.tot_carhy")
    if 'protein' in args_from_ui:
        select.append("product.protein")
    if 'sugars' in args_from_ui:
        select.append("product.sugars")
    if 'zipcode' in args_from_ui:
        select.append("store.zipcode")
    if 'not_contain' in args_from_ui or 'contains' in args_from_ui:
        select.append("product.ingred") 
    return base + ", ".join(select)


def make_from(args_from_ui):
    return " FROM product JOIN store ON product.store = store.name WHERE "


def make_condition(args_from_ui):
    '''
    Get the sqlite query commands

    Inputs:
    args_from_ui: a dictionary, containing search criteria and returns courses
    that match the criteria.

    Outputs:
    query: a list of string, the conditions that will be added to base string
    param: a tuple of parameters, that will be passed in the sql commands
    '''
    query = []
    param = ()

    if 'calories' in args_from_ui:
        query.append("product.calories <= ?")
        param += (args_from_ui['calories'],)
    if 'trans_fat' in args_from_ui:
        query.append("product.trans_fat <= ?")
        param += (args_from_ui['trans_fat'],)
    if 'tot_fat' in args_from_ui:
        query.append("product.tot_fat <= ?")
        param += (args_from_ui['tot_fat'],)
    if 'sodium' in args_from_ui:
        query.append("product.sodium <= ?")
        param += (args_from_ui['sodium'],)
    if 'tot_carhy' in args_from_ui:
        query.append("product.tot_carhy <= ?")
        param += (args_from_ui['trans_fat'],)
    if 'protein' in args_from_ui:
        query.append("product.protein >= ?")
        param += (args_from_ui['protein'],)
    if 'sugars' in args_from_ui:
        query.append("product.sugars <= ?")
        param += (args_from_ui['sugars'],)

    if 'labels' in args_from_ui:
        for label in args_from_ui['labels']:
            query.append("product.labels LIKE ?")
            param += ('%' + label + '%',)

    if 'product_name' in args_from_ui:
        for word in args_from_ui['product_name'].split():
            query.append("product.name LIKE ?")
            param += ('%' + word + '%',)

    if 'store_name' in args_from_ui:
        query.append("product.store IN (%s)" %
                     ",".join('?' * len(args_from_ui['store_name'])))
        param += tuple(args_from_ui['store_name'])
    if 'zipcode' in args_from_ui:
        query.append("store.zipcode LIKE ?")
        param += (args_from_ui['zipcode'][:-1] + '%',)

    if 'contains' in args_from_ui:
        for word in args_from_ui['contains'].split():
            query.append("product.ingred LIKE ?")
            param += ('%' + word.strip(',') + '%',)
    if 'not_contain' in args_from_ui:
        for word in args_from_ui['not_contain'].split():
            query.append("product.ingred NOT LIKE ?")
            param += ('%' + word.strip(',') + '%',)
    return query, param


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    header = []

    for i in cursor.description:
        s = i[0]
        if "." in s:
            s = s[s.find(".") + 1:]
        header.append(s)

    return header
