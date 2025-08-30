import pandas as pd
import numpy as np
import requests
from io import StringIO

next_url = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election"
url_24 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2024_United_Kingdom_general_election"
url_19 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2019_United_Kingdom_general_election"
url_17 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2017_United_Kingdom_general_election"
url_15 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2015_United_Kingdom_general_election"
url_10 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2010_United_Kingdom_general_election"
url_05 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2005_United_Kingdom_general_election"
big_std = 0.023
small_std = 0.016


next_col_dict = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"LD",
    "Nat":"SNP",
    "Grn":"Grn",
    "Ref":"Ref",
    "Oth":"Others",
}
col_dict24 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dems",
    "Nat":"SNP",
    "Grn":"Green",
    "Ref":"Reform",
    "Oth":"Others",
}
col_dict19 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dem",
    "Nat":"SNP",
    "Grn":"Green",
    "Ref":"Brexit",
    "Oth":"Other",
}
col_dict17 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dem",
    "Nat":"SNP",
    "Grn":"Green",
    "Ref":"UKIP",
    "Oth":"Others",
}
col_dict15 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dem",
    # "Nat":"SNP",
    "Grn":"Green",
    "Ref":"UKIP",
    "Oth":"Others",
}
col_dict10 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dem",
    # "Nat":"SNP",
    # "Grn":"Green",
    # "Ref":"UKIP",
    "Oth":"Others",
}
col_dict05 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dem",
    # "Nat":"SNP",
    # "Grn":"Green",
    # "Ref":"UKIP",
    "Oth":"Others",
}


def try_to_int(v):
    try:
        x = int(v)
    except:
        x = 0
    return x

def try_to_float(v):
    try:
        x = float(v)
    except:
        x = 999
    return x

def calculate_others(list_of_pcs):
    others = 1-sum(list_of_pcs)
    return others

def get_latest_polls(df, n=10, allow_repeated_pollsters=False):
    df = df.copy()
    if allow_repeated_pollsters is False:
        pollster_cols = []
        for col in df.columns:
            if "Poll" in col:
                pollster_cols.append(col)
        df = df.drop_duplicates(subset=pollster_cols[0], keep="first")
    df=df.drop(df[(df["Total"]<0.97) | (df["Total"]>1.03)].index)
    return df.iloc[:n]

def wiki_polls_preprocessing(df, col_names = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dems",
    "Nat":"SNP",
    "Grn":"Green",
    "Ref":"Reform",
    "Oth":"Others",
}):
    df["Sample size"] = df["Sample size"].map(lambda x: try_to_int(x))
    df.columns = df.columns.droplevel(1)
    df = df.drop(df[df["Sample size"]==0].index).copy()
    pc_cols = ["Con", "Lab", "Lib Dems", "SNP", "Green", "Reform", "Others"]
    pc_cols = list(col_names.values())
    for col in pc_cols:
        if type(df[col].iloc[0]) is str:
            df[col] = df[col].map(lambda x:try_to_float(str(x).replace("%",""))/100)
    df[col_names["Oth"]] = df.apply(lambda x: calculate_others([x[col_names["Con"]],x[col_names["Lab"]],x[col_names["Lib"]],x[col_names["Nat"]],x[col_names["Grn"]],x[col_names["Ref"]]]) if x[col_names["Oth"]]==9.99 else x[col_names["Oth"]],axis=1)
    for col in df.columns:
        if type(df[col].iloc[0]) is str:
            df[col] = df[col].map(lambda x:str(x).replace("%",""))
    for col in pc_cols:
        df.drop(df[df[col]==9.99].index,axis=0,inplace=True)
    df["Total"] = df[pc_cols].sum(axis=1)
    return df.copy()

def get_wiki_polls_table(url):
    """
    Enhanced function to get polling tables from Wikipedia with proper headers
    Sprint 2 Day 2: Enhanced web scraping with error handling
    """
    try:
        # Set headers to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Make request with proper headers
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Parse HTML with pandas
        tables = pd.read_html(StringIO(response.text))
        poll_tables = []
        
        for t in tables:
            if "Con" in t.columns:
                poll_tables.append(t)
        
        if not poll_tables:
            raise ValueError("No polling tables found with Conservative column")
        
        df = poll_tables[0].copy()
        return df
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch Wikipedia page: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to parse polling table: {str(e)}")


def get_latest_polls_from_html(url, col_dict=next_col_dict, n=10, allow_repeated_pollsters=False):
    """
    Enhanced function with better error handling
    Sprint 2 Day 2: Improved error handling and validation
    """
    try:
        df = get_wiki_polls_table(url)
        df = wiki_polls_preprocessing(df, col_names=col_dict)
        df = get_latest_polls(df, n=n, allow_repeated_pollsters=allow_repeated_pollsters)
        return df
    except Exception as e:
        raise Exception(f"Failed to get latest polls from HTML: {str(e)}")

def get_latest_polls_dict(n=3):
    latest_polls_df = get_latest_polls_from_html(next_url)
    latest_polls_df = latest_polls_df[next_col_dict.values()].copy()
    latest_polls_dict = {}
    for n in range(n):
        r = latest_polls_df.iloc[n]
        for col in latest_polls_df.columns:
            latest_polls_dict[col+str(n)] = r[col]
    return latest_polls_dict

def get_weighted_poll_avg(url, col_dict):
    sdf = get_latest_polls_from_html(url,col_dict=col_dict, n=3)
    sdf_m = sdf[col_dict.values()].mean()

    ldf = get_latest_polls_from_html(url,col_dict=col_dict, n=10)
    ldf_m = ldf[col_dict.values()].mean()
    return pd.concat([sdf_m,ldf_m],axis=1).transpose().mean()

