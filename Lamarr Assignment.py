# Importing required Libraries
import requests as rq
from bs4 import BeautifulSoup
import markdownify
import json
import re
import schedule
import time


def get_title_content():
    """ Functionality :
            - To read the title and content if already existed else creates a dictionary with title and content as keys
            - Takes links from the https://razorpay.com/learn/ website and returns the title and content"""

    try:
        with open("Results.json", "r") as input_file:
            result = json.load(input_file)
    except:
        print("No such file found")
        result = {'title': [], 'content': []}

    given_url = 'https://razorpay.com/learn/'
    response = rq.get(given_url)
    soup = BeautifulSoup(response.text, features="lxml")
    headings = soup.find_all('h2', {'class': ['post-title-alt']})

    titles = []
    links = []
    content = []

    for each_header_tag in headings:
        title = each_header_tag.text.strip()
        if title not in result['title']:
            links.append(each_header_tag.find('a')['href'].strip())
            titles.append(title)

    for link in links:
        response_link = rq.get(link)
        soup = BeautifulSoup(response_link.text, features="lxml")
        content_in_post_meta = soup.find('div', {"class": ["post-meta"]})
        meta_data_under_title = markdownify.markdownify(str(content_in_post_meta.find('div', {"class": ["below"]})))

        content_in_post_content = soup.find('div', {"class": ["post-content"]})
        text_to_discard_1 = content_in_post_content.find('div', {"class": ["code-block"]})
        text_to_discard_2 = content_in_post_content.find_all('p')
        text_to_discard_3 = content_in_post_content.find_all('a')

        entire_description = markdownify.markdownify(str(content_in_post_content)).replace(
            markdownify.markdownify(str(text_to_discard_1)), '')

        for tag in text_to_discard_2:
            if re.findall("Read more|Also Read|Read also|Also read|Read More", tag.text.strip()):
                entire_description = entire_description.replace(markdownify.markdownify(str(tag)), '')

        for tag in text_to_discard_3:
            try:
                if "border-radius" in tag['style']:
                    entire_description = entire_description.replace(markdownify.markdownify(str(tag.parent)), '')
            except:
                pass

        content.append((meta_data_under_title + "\n" + entire_description).strip())

    result['title'] += titles
    result['content'] += content

    with open("Results.json", "w") as outfile:
        json.dump(result, outfile)

    return None


# The scheduler is scheduled to run the function "get_title_content" after every 10 minutes.
schedule.every().to(10).minutes.do(get_title_content)

while True:
    schedule.run_pending()
    time.sleep(1)
