import pandas as pd


def prod_clean(tj, wf, josco):
    """Clean and concate the product dataset."""
    tj_prod = pd.read_csv(tj, index_col=0)
    wf_prod = pd.read_csv(wf, index_col=0)
    josco_prod = pd.read_csv(josco, index_col=0)
    josco_prod.drop(columns=["id"], inplace=True)

    tj_prod.columns = ["name", "store", "ingred", "calories", "trans_fat", "tot_fat", "satu_fat", "sodium",
                       "cholesterol", "tot_carhy", "diet_fiber", "protein", "sugars", "tot_serv", "serv_size", "labels"]
    wf_prod.columns = ["name", "ingred", "calories", "trans_fat", "satu_fat", "tot_fat", "sodium",
                       "cholesterol", "tot_carhy", "diet_fiber", "protein", "sugars", "labels", "serv_size", "tot_serv", "store"]
    josco_prod.columns = ["name", "ingred", "serv_size", "tot_serv", "calories", "tot_fat", "satu_fat",
                          "trans_fat", "tot_carhy", "sugars", "protein", "sodium", "diet_fiber", "cholesterol", "store", "labels"]

    product = pd.concat([tj_prod, wf_prod, josco_prod], sort=False)
    # Reorignize dataframe columns according to the SQL structure
    product = product[["name", "ingred", "calories", "trans_fat", "satu_fat", "tot_fat", "sodium",
                       "cholesterol", "tot_carhy", "diet_fiber", "protein", "sugars", "labels", "serv_size", "tot_serv", "store"]]
    # print(product.columns)
    product["store"] = product["store"]
    product = product[product["name"].notna()]
    product.reset_index(drop=True, inplace=True)
    product.to_csv("product.csv")

    return product


def store_clean(tj, wf, josco):
    """Clean and concate the store dataset."""
    tj_store = pd.read_csv(tj, index_col=0)

    wf_store = pd.read_csv(wf, index_col=0)
    wf_store["name"] = "Whole Foods"
    wf_store.columns = ["address", "city", "state", "zipcode", "name"]

    josco_store = pd.read_csv("JOSCO_store.csv")
    josco_store.drop(columns=["id"], inplace=True)
    # josco_store.columns = ["zipcode", "city", "state", "address", "name"]

    store = pd.concat([tj_store, wf_store, josco_store], sort=False)
    store = store[["name", "address", "city", "state", "zipcode"]]
    # print(store.columns)
    store.reset_index(drop=True, inplace=True)
    store.to_csv("store.csv")
    return store


def go():
    """Run the data cleaning"""
    tj_prod = "TJ_prod.csv"
    wf_prod = "WF_prod.csv"
    josco_prod = "JOSCO_prod.csv"
    prod_clean(tj_prod, wf_prod, josco_prod)

    tj_store = "TJ_store.csv"
    wf_store = "WF_store.csv"
    josco_store = "JOSCO_store.csv"
    store_clean(tj_store, wf_store, josco_store)

go()
