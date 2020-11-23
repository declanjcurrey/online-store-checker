import requests
import webbrowser
from threading import *
import sys

MAX_RETRIES = 50

PS5_URLS = [
    {
        "name": "PS5 Console - John Lewis",
        "url": "https://www.johnlewis.com/sony-playstation-5-console-with-dualsense-controller/white/p5115192",
        "element_ids": [
            "button--add-to-basket"
        ]
    },
    {
        "name": "PS5 Console - Amazon",
        "url": "https://www.amazon.co.uk/PlayStation-9395003-5-Console/dp/B08H95Y452/ref=sr_1_4?crid=3GGLK62X4H5M2&dchild=1&keywords=playstation+5&qid=1605741208&sprefix=pla%2Caps%2C177&sr=8-4",
        "element_ids": [
            "add-to-cart-button"
        ]
    },
    {
        "name": "Godfall PS5 - Amazon",
        "url": "https://www.amazon.co.uk/Gearbox-Publishing-5060760881603-Godfall-PS5/dp/B08JRD17BL/ref=bmx_4/259-2721406-8839332?_encoding=UTF8&pd_rd_i=B08JRD17BL&pd_rd_r=52a36a79-4d57-46de-b935-8cfc786c9b20&pd_rd_w=hgd7I&pd_rd_wg=Co8kK&pf_rd_p=1c67f0c1-d460-4c49-88d7-d8384dea5f37&pf_rd_r=5DJTP6TMXG3229WHHH3E&psc=1&refRID=5DJTP6TMXG3229WHHH3E",
        "element_ids": [
            "add-to-cart-button"
        ]
    }
]

headers = {
    'User-Agent': 'Someones MacBook Pro'
}

session = requests.session()
session.headers.update(headers)

thread_list = []
lock = Semaphore(value=1)


def strip_url(url):
    url = url.replace("https://", "")
    if "www." in url:
        url = url.replace("www.", "")
    url = url.split("/", 1)[0]
    return url


def setup_chrome():
    if sys.platform == 'darwin':
        return webbrowser.get("open -a /Applications/Google\ Chrome.app %s")
    if sys.platform == 'windows':
        return webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s")


def make_page_request(url):
    res = session.get(url)
    return res.status_code, res.text


def handle_200_response(browser, store, page):
    status_code = 200
    retries = 0
    if any(x in page for x in store['element_ids']):
        print("{0} - {1} is up!! And product can be purchased!!! Good Luck!!".format(strip_url(store['url']), store['name']), flush=True)
        browser.open(store['url'])
    else:
        while status_code == 200 and not any(x in page for x in store['element_ids']):
            print("Site: {0} - {1} is up but no add-to-basket element exists... trying again...".format(strip_url(store['url']), store['name']))
            status_code, page = make_page_request(store['url'])

            if retries == MAX_RETRIES:
                print("Maximum retries attempted for {}. Closing thread... ".format(strip_url(store['url'])))
                break

            if status_code == 503:
                handle_503_response(browser, status_code, store)

            if any(x in page for x in store['element_ids']):
                print("Add to basket element exists, opening up chrome! Good luck!")
                browser.open(store['url'])
                break


def handle_503_response(browser, status_code, store):
    retries = 0
    while status_code == 503:
        status_code, page = make_page_request(store['url'])

        if status_code == 503:
            print("{0} is down, GET request returned {1}. retrying...".format(strip_url(store['url']), status_code),
                  flush=True)
            retries += 1
            if retries == MAX_RETRIES:
                print("Maximum retries attempted for {}. Closing thread... ".format(strip_url(store['url'])))
                break

        if status_code == 200:
            handle_200_response(browser, store, page)
            break


def handle_404_response(store):
    print("It seems the page you are trying to request cannot be found. 404 on {}".format(store['url']), flush=True)


def hit_website(browser, store):
    status_code, page = make_page_request(store['url'])

    if status_code == 200:
        handle_200_response(browser, store, page)

    if status_code == 404:
        handle_404_response(store)

    if status_code == 503:
        handle_503_response(browser, status_code, store)

    print(store['name'] + " thread completed processing.", flush=True)


if __name__ == "__main__":
    # setup threads
    for store in PS5_URLS:
        t = Thread(target=hit_website, args=(setup_chrome(), store), name=store['name'])
        thread_list.append(t)

    for thread in thread_list:
        print("starting... {}".format(thread.name))
        thread.start()

    for thread in thread_list:
        thread.join()

    print("Script complete.")
