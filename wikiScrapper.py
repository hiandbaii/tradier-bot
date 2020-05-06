import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
import pickle

class PageScrapper(object):
    def __init__(self):
        self.fileout = "sp500.csv"
        self.col_names = ["symbol", "security", "gicSector", "gicIndustry", "CIK"]
        self.df = pd.DataFrame(columns=self.col_names)

    def fetch_info(self, url):
        res = requests.get(url, verify=False)
        soup = BeautifulSoup(res.text, 'lxml')
        if soup:
            try:
                table = soup.find_all('table')[0]
            except:
                return -1

        rows = table.find_all('tr')
        for row in rows:
            entry = row.find_all('td')
            if len(entry):
                symbol = entry[0].text.rstrip()
                security = entry[1].text.rstrip()
                gicSector = entry[3].text.rstrip()
                gicIndustry = entry[4].text.rstrip()
                CIK = entry[7].text.rstrip()
                tdf = pd.DataFrame({
                                    self.col_names[0]: [symbol],
                                    self.col_names[1]: [security],
                                    self.col_names[2]: [gicSector],
                                    self.col_names[3]: [gicIndustry],
                                    self.col_names[4]: [CIK]
                                 })
                self.df = self.df.append(tdf)
        self.df.to_pickle('sp500.pickle')
        return 0


if __name__ == "__main__":
    # Avoid dealing w/ SSL issues for networks using self-signed certs
    # I'm not a security expert.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    scraper = PageScrapper()
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    scraper.fetch_info(url)
