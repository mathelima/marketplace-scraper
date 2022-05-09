from playwright.sync_api import sync_playwright
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from requests.exceptions import InvalidURL

americanas = 'https://www.americanas.com.br'
products = ['copo-stanley']
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome / 100.0.4896.127 Safari/537.36'}


def main(products):
    cnpjs = []
    for product in products:
        url = americanas + '/busca/' + product
        products_links = search_products(url)
        for product_link in products_links:
            seller_url = search_seller(product_link)
            cnpj = search_cnpj(seller_url)
            if cnpj is not None:
                cnpjs.append(cnpj)
    print(cnpjs)


def search_products(url):
    try:
        req = Request(url, headers=headers)
        response = urlopen(req)
        soup = BeautifulSoup(response, 'html.parser')
        product_links = soup.find_all('div', {'class': 'inStockCard__Wrapper-sc-1ngt5zo-0 iRvjrG'})
        links = []
        for product_link in product_links:
            link = product_link.find('a')
            href = link.get('href')
            product_url = americanas + href
            links.append(product_url)
        return links

    except HTTPError as e:
        print(e.status, e.reason)

    except URLError as e:
        print(e.reason)


def search_seller(product_link):
    try:
        product_link = product_link.replace(" ", "%20")
        req = Request(product_link, headers=headers)
        response = urlopen(req)
        soup = BeautifulSoup(response, 'html.parser')
        get_div = soup.find('div', {'class': 'offers-box__Wrapper-sc-189v1x3-0 kegaFO'})
        if not get_div.find('a'):
            return
        get_link = get_div.find('a')
        href = get_link.get('href')
        seller_url = 'https://www.americanas.com.br' + href
        return seller_url

    except HTTPError as e:
        print(e.status, e.reason)

    except URLError as e:
        print(e.reason)

    except InvalidURL as e:
        print(e.reason)


def search_cnpj(seller_url):
    try:
        if seller_url is not None:
            print(seller_url)
            req = Request(seller_url, headers=headers)
            response = urlopen(req)
            soup = BeautifulSoup(response, 'html.parser')
            with sync_playwright() as p:
                try:
                    browser = p.chromium.launch()
                    page = browser.new_page(extra_http_headers=headers)
                    page.goto(seller_url)
                    if 'Loja Parceira' in soup.title.get_text():
                        page.locator('//*[@id="content-bottom"]/div[8]/div/div/div/div/div/div/div/a[3]').click()
                        text = page.locator('//*[@id="seller-modal-tabs-pane-exchange"]/pre').text_content()
                    else:
                        page.locator('//*[@id="main-top"]/div[3]/div/div/div/div/div/div/div[2]/button').click()
                        text = page.locator('xpath=/html/body/div[3]/div[2]/div/div/div[2]').text_content()
                    cnpj = text[-14:-1] + text[-1]
                    print('CPNJ:', cnpj)
                    browser.close()
                    return cnpj

                except TimeoutError as e:
                    print(e.reason)

    except HTTPError as e:
        print(e.status, e.reason)

    except URLError as e:
        print(e.reason)


if __name__ == '__main__':
    main(products)
