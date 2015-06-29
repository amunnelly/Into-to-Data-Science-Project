# -*- coding: utf-8 -*-

import pandas as pd
import datetime
import matplotlib.pyplot as plt
import scipy.stats
import statsmodels.api as sm

url_nyc = "turnstile_data_master_with_weather.csv"
nyc = pd.read_csv(url_nyc)

    
def workday_holiday(somedate):
    '''
    (datetime) -> int
    Examine the somedate datetime variable to see if it's a Saturday or
    Sunday. Return 0 if it is, 1 if it's not.
    '''
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
    '''
    (pd.Series) -> pd.Series
    Take a pd.Series data and returns that series normalised to having
    a mean of 0 and a standard deviation of 1.
    '''
    mean = data.mean()
    sd = data.std()
    return (data-mean)/sd


def ttest(nyc):
    '''
    (pd.DataFrame) -> tuple
    Take a Dataframe and returns the t-value and p-value of the ENTRIESn_hourly
    for that Dataframe, comparing a series of entries on rainy days and 
    dry days.
    '''
    rain = nyc[nyc.rain == 1]
    shine = nyc[nyc.rain == 0]
    print "Mean Rain: {}".format(rain.ENTRIESn_hourly.mean())
    print "Mean Shine: {}".format(shine.ENTRIESn_hourly.mean())
    
    return scipy.stats.ttest_ind(rain.ENTRIESn_hourly, shine.ENTRIESn_hourly, equal_var = False)


def calculate_OLS_features(nyc):
    numerical_data = nyc[["meanpressurei",
                          "EXITSn_hourly",
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
    '''
    (pd.DataFrame) -> None
    Plots histograms for ENTRIESn_hourly on rainy and dry days.
    '''
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
    plt.plot_date(nyc.DATEn, nyc.ENTRIESn_hourly, alpha = 0.5)
#    dates = pd.date_range('2011-05-01', '2011-05-30', freq = 'D')
    fig.autofmt_xdate()
    plt.xlabel('Date')
    plt.ylabel('Ridership')
    plt.title('Ridership by Date')
    fig.savefig('entries_v_date.png')
    
    return
    
    
if __name__ == '__main__':
    nyc = tidy_up_dates(nyc)
    print ttest(nyc)
    features = calculate_OLS_features(nyc)
    print sm.OLS(nyc.ENTRIESn_hourly, features).fit().summary()