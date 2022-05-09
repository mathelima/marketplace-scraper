from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from requests.exceptions import InvalidURL
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

americanas = 'https://www.americanas.com.br'
produtos = ['copo-stanley']
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome / 100.0.4896.127 Safari/537.36'}


def main(produtos):
    cnpjs = []
    for produto in produtos:
        url = americanas + '/busca/' + produto
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
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(seller_url)

            if 'Loja Parceira' in soup.title.get_text():
                more_information = driver.find_element(By.XPATH,
                                                       '//*[@id="content-bottom"]/div[8]/div/div/div/div/div/div/div/a[3]').click()
                texto = driver.find_element(By.XPATH, '//*[@id="seller-modal-tabs-pane-exchange"]/pre').text
            else:
                more_information = driver.find_element(By.XPATH,
                                                       '//*[@id="main-top"]/div[3]/div/div/div/div/div/div/div[2]/button').click()
                texto = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div/div[2]').text

            driver.close
            cnpj = texto[-14:-1] + texto[-1]
            return cnpj

    except HTTPError as e:
        print(e.status, e.reason)

    except URLError as e:
        print(e.reason)


if __name__ == '__main__':
    main(produtos)
