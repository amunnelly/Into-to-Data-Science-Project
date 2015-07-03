# -*- coding: utf-8 -*-
"""
Created on Sat May 23 13:45:52 2015

@author: anthonymunnelly
"""

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import scipy.stats
import statsmodels.api as sm

url_nyc = "/Users/anthonymunnelly/Documents/Udacity/Intro to Data Science/NYC Subway Project/turnstile_data_master_with_weather.csv"

nyc = pd.read_csv(url_nyc)

def date_to_day(somedate):
    return somedate.strftime('%A')

    
def workday_holiday(somedate):
    if somedate.strftime('%A') == 'Saturday' or somedate.strftime('%A') == 'Sunday':
        return 0
    else:
        return 1

def tidy_up_dates(nyc):
    nyc['DATEn'] = pd.to_datetime(nyc.DATEn, "%Y-%m-%d")
    nyc['TIMEn'] = pd.to_datetime(nyc.TIMEn, "%H:%M:%S")
    nyc['Day_Type'] = nyc.DATEn.map(lambda x: workday_holiday(x))

    return nyc


def normalise(data):
    mean = data.mean()
    sd = data.std()
    return (data-mean)/sd


def mann_whitney_test(nyc):
    rain = nyc[nyc.rain == 1]
    shine = nyc[nyc.rain == 0]
    
    return scipy.stats.mannwhitneyu(rain.ENTRIESn_hourly, shine.ENTRIESn_hourly)


def plot_mean_temperatures(nyc):
    fig=plt.figure(1)
    plt.plot(nyc.meantempi, color = 'red')
    dates = pd.date_range('2011-05-01', '2011-05-30', freq = '2D')
    #Create date labels
    date_labels = [d.strftime('%a-%d') for d in dates]
    # Arrange the date labels so they appear correctly on the graph - harder than it looks
    plt.xticks(np.arange(0, 131951, 131951/15), date_labels, rotation=45)
    plt.title('Mean Temperature by Day')
    plt.xlabel('Day')
    plt.ylabel('Temperatures')
    plt.show()
    fig.savefig('mean_temperature_by_day.png')
    return


def calculate_OLS(nyc):
    numerical_data = nyc[["meanpressurei",
                          "meantempi",
                          "fog",
                          "precipi",
                          "rain"]]
                          
    features = normalise(numerical_data)
    
    day_type = pd.get_dummies(nyc.Day_Type)
    features = features.join(day_type)

    features.corr().to_csv('correlation_checker.csv')
    
    return features


def plotting_for_report(nyc):
    rain = nyc[nyc.rain == 1]
    shine = nyc[nyc.rain == 0]
    data = [rain.ENTRIESn_hourly, shine.ENTRIESn_hourly]
    fig, axes = plt.subplots(2,1, sharex = True, sharey = True)
    plt.title('Entries per Hour for Rainy and Dry Days')
    fig.subplots_adjust(hspace = 0.5)
    colors = ['blue', 'red']
    titles = ['Rain', 'Dry']
    for i in range(2):
        axes[i].hist(data[i].values, bins = 100, color = colors[i])
        axes[i].set_xlim([0,10000])
        axes[i].set_title(titles[i])
        axes[i].set_xlabel('Entries per Hour')
        axes[i].set_ylabel('Count of Entries')

    fig.savefig("rain_shine.png")
    plt.show()
    
    return

def plot_entries_v_date(nyc):
    fig = plt.figure(1)    
    plt.plot_date(nyc.DATEn, nyc.ENTRIESn_hourly.sum(), 'b-')
    fig.autofmt_xdate()
    plt.xlabel('Date')
    plt.ylabel('Ridership')
    plt.title('Ridership by Date')
    fig.savefig('entries_v_date.png')
    
    return
        
if __name__ == '__main__':
    nyc = tidy_up_dates(nyc)
    print mann_whitney_test(nyc)
    plot_mean_temperatures(nyc)
    features = calculate_OLS(nyc)
    print sm.OLS(nyc.ENTRIESn_hourly, features).fit().summary()