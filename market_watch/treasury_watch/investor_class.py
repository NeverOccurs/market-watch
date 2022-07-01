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

import pandas as pd


def load_data():
    bills_url = 'https://home.treasury.gov/system/files/276/May_9_2022_IC_Bills.xls'
    coupons_url = 'https://home.treasury.gov/system/files/276/May_9_2022_IC_Coupons.xls'
    bills_data = pd.read_excel(bills_url, skiprows=3)
    coupons_data = pd.read_excel(coupons_url, skiprows=3)

    return bills_data, coupons_data


def clean_names(data):
    # rename variables
    renamer = lambda x: x.strip().replace('\n', '').replace(' ', '')

    rename_dict = {
        'Issuedate': 'issue_date',
        'Auctionhighrate%': 'high_rate',
        'Cusip': 'cusip',
        'Maturitydate': 'maturity_date',
        'Totalissue': 'total_issue',
        '(SOMA)FederalReservebanks': 'Fed',
        'Depositoryinstitutions': 'Banks',
        'Individuals': 'Individuals',
        'Dealersandbrokers': 'Broker Dealers',
        'PensionandRetirementfundsandIns.Co.': 'Pension',
        'Investmentfunds': 'Investment Fund',
        'Foreignandinternational': 'Foreign',
        'Other(seecategorydescription)': 'Other',
        '(%)CouponrateOrSpread': 'coupon_rate',  # for coupons only
        'Securitytype': 'coupons_desc',  # coupons only
        'Securityterm': 'bills_desc',  # bills only
    }

    data = data.rename(columns=renamer).rename(columns=rename_dict)

    return data


def reformat_dates(data, date_cols):
    for c in date_cols:
        data[c] = pd.to_datetime(data[c])

    return data


def change_data_type(data):
    dtype_mapping = {
        'high_rate': float,
        'total_issue': float,
        'Fed': float,
        'Banks': float,
        'Individuals': float,
        'Broker Dealers': float,
        'Pension': float,
        'Investment Fund': float,
        'Foreign': float,
        'Other': float,
        'coupon_rate': float
    }

    return data.astype({k: v for k, v in dtype_mapping.items() if k in data.columns})


def parse_bills_tnc(data):
    return data.assign(
        tenor=lambda x: x['bills_desc'].apply(lambda y: y.split(' ')[0]),
        group=lambda x: x['bills_desc'].apply(lambda y: y.split(' ')[1])
    )


def parse_coupons_tnc(data):
    return data.assign(
        tenor=lambda x: x['coupons_desc'].apply(lambda y: y.split(' ')[0]),
        group=lambda x: x['coupons_desc'].apply(lambda y: y.split(' ')[1])
    )


if __name__ == '__main__':
    participants = ['Fed', 'Banks', 'Individuals', 'Broker Dealers',
                    'Pension', 'Investment Fund', 'Foreign', 'Other']

    # load data
    bills_data, coupons_data = load_data()

    # preliminary post-processing: renaming, change data types, drop null values
    bills_data = (bills_data
                  .pipe(clean_names)
                  .pipe(pd.DataFrame.dropna, subset=['bills_desc'])
                  .pipe(change_data_type)
                  .pipe(reformat_dates, date_cols=['issue_date', 'maturity_date'])
                  .pipe(parse_bills_tnc)
                  )

    # preliminary post-processing: renaming, change data types, drop null values
    coupons_data = (coupons_data
                    .pipe(clean_names)
                    .pipe(pd.DataFrame.dropna, subset=['coupons_desc'])
                    .pipe(change_data_type)
                    .pipe(reformat_dates, date_cols=['issue_date', 'maturity_date'])
                    .pipe(parse_coupons_tnc)
                    )