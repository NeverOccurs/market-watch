#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Mercer@Zhihu
# Created Date: July 2022
# version ='0.1'
# ---------------------------------------------------------------------------
""" Parse auction announcements and results of U.S. Treasury securities"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import datetime
from bs4 import BeautifulSoup as bs
import requests as req
import pandas as pd
from tqdm.notebook import tqdm


def parse_data(url):
    page = req.get(url)
    soup = bs(page.content, "xml")
    auction_data = soup.contents[0]

    # parse information of auction results
    results = auction_data.find('AuctionResults')
    results_data_dict = {tag.name: tag.text for tag in results.find_all()}

    # parse information of auction announcement/meta
    announcement = auction_data.find('AuctionAnnouncement')
    ann_data_dict = {tag.name: tag.text for tag in announcement.find_all()}

    cusip = ann_data_dict['CUSIP']

    results_df = pd.DataFrame(data=results_data_dict, index=[cusip])
    announcement_df = pd.DataFrame(data=ann_data_dict, index=[cusip])

    return results_df, announcement_df


def get_result_url(date, num):
    return f'https://www.treasurydirect.gov/xml/R_{date}_{num}.xml'


def get_data(cache_dates):
    df_result_list = []
    df_ann_list = []
    for dt in tqdm(cache_dates, desc='Caching Treasury auctions data ...'):
        ran_out = False
        n = 1
        while not ran_out:
            try:
                df_result, df_ann = parse_data(get_result_url(dt, n))
                df_result_list.append(df_result)
                df_ann_list.append(df_ann)
                n += 1
            except:
                ran_out = True

    result_cache_df = pd.concat(df_result_list)
    ann_cache_df = pd.concat(df_ann_list)

    return result_cache_df, ann_cache_df


if __name__ == "__main__":
    start_date = '2008-1-1'
    end_date = datetime.date.today().strftime('%Y%m%d')
    dates = [dt.strftime('%Y%m%d') for dt in pd.date_range(start_date, end_date, freq='B')]

    result_data, announcement_data = get_data(dates)