import requests
import os
from bs4 import BeautifulSoup

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

service = Service('\chromedriver_win32')

options = Options()
options.add_argument("--window-size=1920,1200") # specify window size, for screenshots, if any
options.add_argument("--headless") # prevents opening of browser on pc

driver = webdriver.Chrome(options=options, service=service) # initiate
driver.get("https://www.amazon.sg/")
driver.implicitly_wait(10) # set wait time for driver

# SEARCH FUNCTION
search = driver.find_element(by=By.NAME, value="field-keywords") # find search box. differs from site to site
item = input("Enter item you are interested in: ")

search.send_keys(item) # INPUT TO BE SENT
search.send_keys(Keys.ENTER)

get_url = driver.current_url

# BEAUTIFUL SOUP SWOOPS IN HERE, TO RETURN RESULTS
product_list = {
    'links': [],
    'names': [],
    'stars': [],
    'prices': []
}
product_dict = {}
values = []

top_num = 5 # SET number of products to return. Only returns page 1 of results

URL = get_url
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(id="search") # overall main container of results

# find specific container with list of results
product_elements = results.find_all("div", class_="sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20")

if(len(product_elements) < top_num): # only page 1 :(
    print("Only " + str(len(product_elements)) + " results are available to return")
    quit()
else:
    for number in range(0, top_num):
        link = product_elements[number].find("a", class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
        full_link = 'amazon.sg' + link['href'].strip()
        name = product_elements[number].find("span", class_="a-size-base-plus a-color-base a-text-normal")
        star = product_elements[number].find("span", class_="a-icon-alt")
        price = product_elements[number].find("span", class_="a-price-whole")
        if price:
            front_price = price.get_text().strip()
            price_decimal = product_elements[number].find("span", class_="a-price-fraction")
            back_price = price_decimal.get_text().strip()
            actual_price = '$' + str(front_price) + str(back_price)
        else:
            actual_price = 'N/A'

        product_list['links'].append(full_link)
        product_list['names'].append(name.get_text().strip() if name else 'N/A')
        product_list['stars'].append(star.get_text().strip() if star else 'N/A')
        product_list['prices'].append(actual_price)

    link_list = product_list['links']
    for i in range(0, len(link_list)):
        if product_list['links'][i] not in product_dict:
            product_dict[product_list['links'][i]] = (product_list['names'][i], product_list['stars'][i], product_list['prices'][i])

# CREATE PDF
directory = "C:\Amazon Selenium Outputs" # CHANGE to created folder directory, to store PDFs 
folder = os.listdir(directory)
doc_num = len(folder)
pdf_file = directory + "/amazonTEST" + str((doc_num)+1) + ".pdf" # change file name if needed
c = canvas.Canvas(pdf_file, pagesize=letter)
line_x = 50
line_y = 700
line_spacing = 20

for i in range(len(product_list['links'])):
    if line_y < 60: # go to new page if exceed
        c.showPage()
        line_y = 700
    product_link = product_list['links'][i]
    c.setFont('Helvetica-Bold', 10)
    c.drawString(line_x, line_y, "Product Link: ") # print bold
    c.setFont('Helvetica', 8)
    if (len(product_link) > 90):
        c.drawString(line_x + 70, line_y, product_link[0:90]) # print link
        line_y -= line_spacing
        c.drawString(line_x + 70, line_y, product_link[90:len(product_link)]) # print link
    else:
        c.drawString(line_x + 70, line_y, product_link) # print link
    line_y -= line_spacing
    # print details
    product_name = product_list['names'][i]
    product_stars = product_list['stars'][i]
    product_price = product_list['prices'][i]
    if (len(product_name) > 110):
        product_name = product_name[0:110] + "..."
    c.drawString(line_x, line_y, "Name: " + product_name)
    line_y -= line_spacing
    c.drawString(line_x, line_y, "Rating: " + product_stars)
    line_y -= line_spacing
    c.drawString(line_x, line_y, "Price: " + product_price) 
    line_y -= line_spacing
    line_y -= line_spacing

c.save()