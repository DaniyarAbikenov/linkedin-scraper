import json
import os
import time
from lib2to3.fixes.fix_input import context
from pathlib import Path
from urllib.parse import urljoin, urlencode

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class Searcher:
    def __init__(self):
        self.step = 1
        self.page_end = None

    def extract_company(self, code: WebElement):
        link = code.find_elements(By.CSS_SELECTOR, 'a')[1]
        name = link.text.strip()
        linkedin_link = link.get_attribute('href')
        return {
            "name": name,
            "linkedin_link": linkedin_link,
        }

    def extract_companies(self, code: WebElement):
        search_list = code.find_elements(By.CSS_SELECTOR, ".search-marvel-srp li")
        companies = []
        for item in search_list:
            try:
                companies.append(self.extract_company(item))
            except Exception as e:
                pass
                # print(e)
        return companies


    def _get_page_count(self, link):
        content = self.raw_search(link).find_elements(By.CSS_SELECTOR, '.artdeco-pagination__pages li')[-1]
        return int(content.text.strip())


    def search(self, link, page_start=1, page_end=None, with_save = False):
        if page_end:
            self.page_end = page_end
        if self.page_end is None:
            self.page_end = self._get_page_count(link)
            print(f"найдено {self.page_end} pages")
        companies = []
        for i in range(page_start, self.page_end + 1):
            result = self.raw_search(f"{link}&page={i}")
            companies.extend(self.extract_companies(result))
            if with_save:
                with open(f"search{self.step}.json", 'w', encoding='utf-8') as f:
                    json.dump(companies, f, ensure_ascii=False, indent=4)
        self.step += 1
        return companies

    def raw_search(self, link):
        options = webdriver.ChromeOptions()
        options.debugger_address = "localhost:9222"
        driver = webdriver.Chrome(options=options)
        driver.get(link)
        time.sleep(3)
        return driver.find_element(By.CSS_SELECTOR, "body")


def raw_main(context):
    # raw_link = "https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22103644278%22%5D&companySize=%5B%22C%22%5D&industryCompanyVertical=%5B%2299%22%5D&keywords=industrial%20design&origin=FACETED_SEARCH&sid=%2Cg5"
    searcher = Searcher()
    output_dir = Path("searches")
    backup_dir = Path("search_backups")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)
    try:
        context['results'] = searcher.search(context['link'], page_start=1)
        # result.extend(searcher.search("https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22104195383%22%5D&industryCompanyVertical=%5B%2299%22%2C%22140%22%5D&keywords=web%20design&origin=FACETED_SEARCH&sid=NdB", limit=50))
        with open(output_dir / (context['name'] + ".json"), 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e)
    finally:
        with open(backup_dir / f"{context['name']}.json", 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=4)


def main():
    context = {
        "link": input("Link:"),
        "name": input("Output file:") or "result.json",

    }
    raw_main(context)

def multi_main():
    with open("multi.json", 'r', encoding='utf-8') as f:
        contexts = json.load(f)
    for context in contexts:
        print(context)
        raw_main(context)



if __name__ == '__main__':
    main()
