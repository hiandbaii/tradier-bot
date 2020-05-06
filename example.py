from http import client
import time
import pandas as pd
import pickle
from datetime import date
import requests

class tradierBot(object):
    def __init__(self):
        self.apitoken = self.__import_apitoken()
        self.headers = {"Accept": "application/json",
                        "Authorization": "Bearer " + self.apitoken}
        self.lheader = [] #HTTP response header from last /markets API call
        self.connection = client.HTTPSConnection('sandbox.tradier.com', 443, timeout=30)

        #Do an initial HTTP request to check API state
        self.__test_api()

    def __import_apitoken(self):
        f = open("myapitoken")
        return f.read()

    #Test Connection
    def __test_api(self):
        self.connection.request('GET', '/v1/markets/quotes?symbols=ibm', None, self.headers)
        try:
            response = self.connection.getresponse()
            content = response.read() #Have to read otherwise Exception on next HTTP GET
            self.lheader = response.headers
        except client.HTTPException:
            print("HTTP GET failed ¯\\_(ツ)_/¯")

    def simple_get(self,symbol='spy'):
        self.connection.request('GET', '/v1/markets/quotes?symbols='+symbol, None, self.headers)
        try:
            response = self.connection.getresponse()
            self.lheader = response.headers
            content = response.read()  # JSON response
            return content
        except client.HTTPException:
            print("HTTP GET failed ¯\\_(ツ)_/¯")

    #Historical Quote API takes ONE ticker at a time
    def get_historical(self,symbol='spy',interval='daily',start='2020-03-01',end='2020-03-31'):
        url = 'https://sandbox.tradier.com/v1/markets/history'
        response = requests.get(url,
                                params={'symbol':symbol,
                                        'interval':interval,
                                        'start':start,
                                        'end':end},
                                headers=self.headers)
        json_response = response.json()
        print(symbol, end='')
        print(json_response)

    # Throttle as needed for rate-limited API. Will actually check implementation if needed. Could also handle w/ timeouts?
    def __throttle(self):
        navail = self.lheader['X-Ratelimit-Available']
        if navail == 0:
            # Assume our clock is within 5 seconds of tradier's clock
            time2sleep = max(1, self.lheader['X-Ratelimit-Expiry'] - time.time() + 5)
            time.sleep(time2sleep)

    def __del__(self):
        self.connection.close()

if __name__ == "__main__":
    tb = tradierBot()
    df = pd.read_pickle('sp500.pickle')
    for row in df.iterrows():
        tb.get_historical(row[1].symbol)
        pass
        # content = tb.simple_get(row[1]['symbol'])

