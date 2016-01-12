"""
Brian Perrett with Moonlight Feather Inc.
sellbrite.py
Communication with sellbrite in a hackish way through selenium
"""
from __future__ import division
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time


class Sellbrite():
    login_url = "https://app.sellbrite.com/merchants/sign_in"
    inventory_url = "https://app.sellbrite.com/inventories"
    spreadsheet_url = "https://app.sellbrite.com/inventories_spreadsheet"
    base_url = "https://app.sellbrite.com"

    def __init__(self):
        # Disable images
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chromeOptions.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(chrome_options=chromeOptions)
        self.email = self._getEmail()
        self.pwd = self._getPassword()
        self.page = None
        self.urls = {}
        self._login()

    def _getEmail(self):
        with open("sb.data", "rb") as f:
            for line in f:
                line = line.split()
                if line[0] == "email":
                    email = line[1].strip()
        return email

    def _getPassword(self):
        with open("sb.data", "rb") as f:
            for line in f:
                line = line.split()
                if line[0] == "password":
                    password = line[1].strip()
        return password

    def _login(self):
        self.driver.get(self.login_url)
        element = self.driver.find_element_by_id("merchant_email")
        element.send_keys(self.email)
        element = self.driver.find_element_by_id("merchant_password")
        element.send_keys(self.pwd)
        element = self.driver.find_element_by_id("clickme")
        element.click()
        self.page = "dashboard"

    def _search(self, sku):
        """
        Searching through inventory_url
        """
        sku = str(sku)
        url = "{}?query={}".format(self.inventory_url, sku)
        self.driver.get(url)
        self.page = "search inventory " + sku

    def _searchSpreadsheet(self, sku):
        """
        Sends a query to spreadsheet_url.
        """
        sku = str(sku)
        url = "{}?query={}".format(self.spreadsheet_url, sku)
        self.driver.get(url)

    def _getTable(self):
        soup = BeautifulSoup(self.driver.page_source)
        table = soup.find_all("table")[0]
        return table

    def _getHeaders(self):
        table = self._getTable()
        thead = table.find("thead")
        # print(thead)
        headers = {}
        for i, th in enumerate(thead.find_all("th")):
            headers[str(th.text)] = i
        return headers

    def _getRow(self, sku):
        sku = str(sku)
        elements = self.driver.find_elements_by_tag_name("tr")
        for e in elements:
            try:
                e.find_element_by_link_text(sku)
                row = e
                break
            except Exception:
                pass
        return row

    def updateQuantityss(self, sku, quantity):
        """
        Not Working as of 9/3/15.  Cannot select spreadsheet elements
        """
        sku = str(sku)
        quantity = str(quantity)
        self._searchSpreadsheet(sku)
        headers = self._getHeaders()
        row = self._getRow(sku)
        elements = row.find_elements_by_tag_name("td")
        on_hand = elements[headers["On Hand"]]
        on_hand.click()
        on_hand.click()
        on_hand.clear()
        on_hand.send_keys(quantity)

    def _findSkuPage(self, sku):
        sku = str(sku)
        if sku not in self.urls:
            self._search(sku)
            elements = self.driver.find_elements_by_class_name("IM-name-content")
            for e in elements:
                for x in e.find_elements_by_link_text(sku):
                    if x != []:
                        href = x.get_attribute("href")
            self.urls[sku] = str(href)
            self.driver.get(href)
        else:
            self.driver.get(self.urls[sku])
        self.page = sku

    def _clickProductInfo(self):
        product_info = self.driver.find_element_by_link_text("Product Info")
        product_info.click()
        self.page = "product info"

    def updateQuantity(self, sku, quantity):
        sku = str(sku)
        quantity = str(quantity)
        info = self.getBasicInfo(sku)
        quantity = str(int(quantity) + int(info["reserved"]))
        self._findSkuPage(sku)
        time.sleep(.5)
        element = self.driver.find_element_by_name("quantity")
        element.clear()
        element.send_keys(quantity)
        element = self.driver.find_element_by_class_name("PE-inv-location-table__header")
        element = element.find_element_by_tag_name("a")
        element.click()
        self.page = sku

    def addQuantity(self, sku, add_quantity):
        sku = str(sku)
        info = self.getBasicInfo(sku)
        quantity = info["quantity"]
        new_quantity = str(int(quantity) + int(add_quantity) + int(info["reserved"]))
        elements = self.driver.find_elements_by_class_name("IM-name-content")
        for e in elements:
            for x in e.find_elements_by_link_text(sku):
                if x != []:
                    href = x.get_attribute("href")
        self.driver.get(href)
        time.sleep(.5)
        element = self.driver.find_element_by_name("quantity")
        element.clear()
        element.send_keys(new_quantity)
        element = self.driver.find_element_by_class_name("PE-inv-location-table__header")
        element = element.find_element_by_tag_name("a")
        print("Found save button.")
        element.click()
        self.page = sku

    def deductQuantity(self, sku, deduct_quantity):
        sku = str(sku)
        info = self.getBasicInfo(sku)
        quantity = info["quantity"]
        new_quantity = str(int(quantity) - int(deduct_quantity) + int(info["reserved"]))
        elements = self.driver.find_elements_by_class_name("IM-name-content")
        for e in elements:
            for x in e.find_elements_by_link_text(sku):
                if x != []:
                    href = x.get_attribute("href")
        self.driver.get(href)
        time.sleep(.5)
        element = self.driver.find_element_by_name("quantity")
        element.clear()
        element.send_keys(new_quantity)
        element = self.driver.find_element_by_class_name("PE-inv-location-table__header")
        element = element.find_element_by_tag_name("a")
        element.click()
        self.page = sku

    def updateBinLocation(self, sku, bin_loc):
        sku = str(sku)
        bin_loc = str(bin_loc)
        self._findSkuPage(sku)
        time.sleep(.5)
        element = self.driver.find_element_by_name("bin_location")
        element.clear()
        element.send_keys(bin_loc)
        element = self.driver.find_element_by_class_name("PE-inv-location-table__header")
        element = element.find_element_by_tag_name("a")
        element.click()
        self.page = sku

    def getBasicInfo(self, sku):
        sku = str(sku)
        self._search(sku)
        soup = BeautifulSoup(self.driver.page_source)
        tables = soup.find_all("table")
        for table in tables:
            for tr in table.find_all("tr"):
                # print(tr)
                for td in tr.find_all("td"):
                    if td is not None:
                        try:
                            cl = td.get("class")
                            if cl is not None and "IM-sku-data" in cl:
                                if td.text.strip() == sku:
                                    row = tr
                        except Exception:
                            pass
        found = False
        for td in row.find_all("td"):
            if not found:
                if td.get("class") is not None and "IM-sku-data" in td.get("class"):
                    div = td.find("div")
                    a = div.find("a")
                    href = a.get("href")
                    self.urls[sku] = self.base_url + href
                    found = True
                    print("Current url dictionary \n{}".format(self.urls))
            if td.get("class") is not None and "IM-name-data" in td.get("class"):
                title = td.text.strip()
            elif td.get("class") is not None and "IM-bin-location" in td.get("class"):
                bin_loc = td.text.strip()
            elif td.get("data-resizable-column-id") is not None and "available" in td.get("data-resizable-column-id"):
                quantity = td.text.strip()
            elif td.get("data-resizable-column-id") is not None and "allocated" in td.get("data-resizable-column-id"):
                reserved = td.text.strip()
        self.page = "search inventory " + sku
        return {"title": title, "bin": bin_loc, "quantity": quantity, "reserved": reserved}

    def getDetailedInfo(self, sku):
        sku = str(sku)
        self._search(sku)
        soup = BeautifulSoup(self.driver.page_source)
        tables = soup.find_all("table")
        for table in tables:
            for tr in table.find_all("tr"):
                # print(tr)
                for td in tr.find_all("td"):
                    if td is not None:
                        try:
                            cl = td.get("class")
                            if cl is not None and "IM-sku-data" in cl:
                                if td.text.strip() == sku:
                                    row = tr
                        except Exception:
                            pass
        for td in row.find_all("td"):
            if td.get("class") is not None and "IM-name-data" in td.get("class"):
                title = td.text.strip()
            elif td.get("class") is not None and "IM-bin-location" in td.get("class"):
                bin_loc = td.text.strip()
            elif td.get("data-resizable-column-id") is not None and "quantity" in td.get("data-resizable-column-id"):
                quantity = td.text.strip()
        link = self.driver.find_element_by_link_text(sku)
        link.click()
        self._clickProductInfo()
        e = self.driver.find_element_by_name("product[standard_id]")
        upc = e.get_attribute("value")
        self.page = "product info " + sku
        return {"title": title, "bin": bin_loc, "quantity": quantity, "upc": upc}


def testSearch():
    sb = Sellbrite()
    sb._search(341)


def testSearchSpreadsheet():
    sb = Sellbrite()
    sb._searchSpreadsheet(341)


def testFindSkuPage():
    sb = Sellbrite()
    sb._findSkuPage(341)


def testUpdateQuantity():
    sb = Sellbrite()
    sb.updateQuantity(341, 20)


def testUpdateBinLocation():
    sb = Sellbrite()
    sb.updateBinLocation(341, "B096")


def testGetBasicInfo():
    sb = Sellbrite()
    print(sb.getBasicInfo(341))


def testGetHeaders():
    sb = Sellbrite()
    sb._searchSpreadsheet(341)
    print(sb._getHeaders())


def testGetRow():
    sb = Sellbrite()
    sb._searchSpreadsheet(341)
    row = sb._getRow(341)
    print(row.get_attribute("innerHTML"))


def testUpdateQuantityss():
    sb = Sellbrite()
    sb.updateQuantityss(341, 20)

if __name__ == '__main__':
    # testSearch()
    # testSearchSpreadsheet()
    # testFindSkuPage()
    # testUpdateQuantity()
    # testUpdateBinLocation()
    testGetBasicInfo()
    # testGetHeaders()
    # testGetRow()
    # testUpdateQuantityss()
