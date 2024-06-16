import cloudscraper
import bs4

scrapper = cloudscraper.create_scraper()

site = scrapper.get("https://hotline.ua/ua/bt/").text

soup = bs4.BeautifulSoup(site, "html.parser")

print(soup.prettify())