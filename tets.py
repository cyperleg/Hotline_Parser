import time

import undetected_chromedriver
from bs4 import BeautifulSoup
from Exporter import Exporter
import logging
import cloudscraper

scrapper = cloudscraper.create_scraper()


def reformat(x: str):
    index = x.find(".")

    return hotline_link + x[:index - 1] + "5" + x[index:]


def captcha_reload(link):
    driver = undetected_chromedriver.Chrome()
    driver.get(link)
    input()
    driver.quit()


def check_captcha(link):
    resp = scrapper.get(link)
    soup = BeautifulSoup(resp.text, "html.parser")
    if soup.find(attrs={"class": "captcha"}) is not None:
        captcha_reload(link)
        resp = scrapper.get(link)
        soup = BeautifulSoup(resp.text, "html.parser")

    return soup



hotline_link = "https://hotline.ua"

categories = ["tehnika-dlya-doma", "tehnika-dlya-krasoty-i-uhoda", "medtehnika-dlya-doma", "melkaya-tehnika-dlya-kuhni"]

# main cycle
for i in categories:

    logging.basicConfig(filename=f'{i}.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    exp = Exporter(i)

    soup = check_captcha("https://hotline.ua/ua/bt")

    subcategories = [(x.text, x['href']) for x in soup.find(attrs={"id": i}).parent.find_all(attrs={"class": "section-navigation__link"})]

    # subcategory cycle
    for j in subcategories:

        logging.info(f"Going into {j[0]}")

        if len(j[0].strip()) > 31:
            exp.create_sheet(j[0].strip()[:32])
        else:
            exp.create_sheet(j[0].strip())

        soup = check_captcha(hotline_link + j[1] + "?priceTo=7000&priceFrom=200")

        page_count = soup.find(attrs={"class": "pagination__pages"})

        if page_count is not None:
            if page_count.text.split("...")[-1].strip().isdigit():
                page_count = int(page_count.text.split("...")[-1].strip())
            elif page_count.text.split("\n")[-2].strip().isdigit():
                page_count = int(page_count.text.split("\n")[-2].strip())
            else:
                page_count = 1
        else:
            page_count = 1

        logging.info(f"Pages count - {page_count}")

        # page cycle
        for k in range(1, page_count + 1):

            logging.info(f"Page {k}:")

            soup = check_captcha(hotline_link + j[1] + "?priceTo=7000&priceFrom=200" + f"&p={k}")

            temp_urls = [x.a['href'] for x in soup.find_all(attrs={"class": "list-item__photo"})]

            counter = 0
            # goods cycle
            for o in temp_urls:
                if exp.check_item(hotline_link + o):
                    logging.info("already had good")
                    continue

                counter += 1
                if counter == 4:
                    time.sleep(60)
                    counter = 0
                try:
                    soup = check_captcha(hotline_link + o)

                    link = hotline_link + o

                    brand = soup.find(attrs={"class": "specifications__table"})
                    if brand is not None:
                        brand = brand.find("tbody").find("tr").find_all("td")[-1].text.strip()
                    else:
                        brand = "-" if brand == "" else brand

                    model = soup.find_all("li", attrs={"class": "breadcrumbs__item"})[-1].text

                    specs = soup.find("span", {"class": "specifications-list"}).text.\
                        replace("         ", '').replace("...", "").replace("\n", '').strip()

                    desc = soup.find(attrs={"class": "description__content"})
                    if desc is not None:
                        desc = desc.find("div").text.strip()
                    else:
                        desc = "-"

                    price = soup.find(attrs={"class": "many__price-sum"})
                    if price is not None:
                        price = price.text
                    else:
                        price = soup.find(attrs={"class": "price"}).text

                    imgs = [reformat(x.find("img")["src"]) for x in soup.find_all(attrs={"class": "zoom-gallery__nav-item--image"})]

                    logging.info(f"\t{brand} {model}")

                    exp.add_line([brand, model, price, desc, specs, imgs, link])

                except Exception as e:
                    captcha_reload(hotline_link)
                    logging.warning(f"skipping one good {e}", e, exc_info=True)
                    continue

            exp.save()











