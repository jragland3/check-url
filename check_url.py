import asyncio
import json
import difflib
import os
from nodriver import start, cdp, loop
from bs4 import BeautifulSoup as bs
from datetime import datetime
from selen


async def main():
    url = 'https://www.viator.com/'
    driver = await start()
    tab = driver.main_tab
    tab.add_handler(cdp.network.ResponseReceived, status_check)
    tab = await driver.get(url)
    content = await tab.get_content()
    data = {}
    date = str(datetime.now().date()).replace('-', '_')

    data['date_of_run'] = date
    data['url'] = url
    data['title'] = (await tab.select_all('[data-automation="page-HOME"]'))[0].text
    data['test_element_count'] = await count_elements(tab)

    # Create directory for the daily report
    try:
        os.mkdir(f'artifacts/{date}')
    except:
        pass

    # Write html contents to file
    with open(f'artifacts/{date}/content.html', 'w') as f:
        soup = bs(content, features='lxml')
        f.write(soup.prettify())
    
    # Write 'data' object to json file
    with open(f'artifacts/{date}/data.json', 'w') as f:
        json_string = json.dumps(data, indent=4)
        f.write(json_string)

    # Compare files and return the lines that match (differences are removed)
    # TODO WIP: does not yet work as intended
    with open(f'artifacts/2024_12_28/content.html', 'r') as f1, open(f'artifacts/2024_12_27/content.html', 'r') as f2:
        similar_html = await compare_files(f1, f2)

        with open(f'artifacts/2024_12_28/similar.txt', 'w') as d:
            d.write(similar_html)

    # TODO add data for percentage of difference between the latest '...content.html' and the previous one


async def percent_change(file1, file2):
    line_match_gen = difflib.n_diff(file1.readlines(), file2.readlines())
    similar = ''
    num_changed_lines = 0
    for line in line_match_gen:
        similar += line
    for line in similar.split(f'\n'):
        if line != '':
            if line[0] == '+' and line[0] == '-' and line[0] == '@':
                num_changed_lines += 1
    return num_changed_lines 

async def compare_files(file1, file2):
    line_match_gen = difflib.ndiff(file1.readlines(), file2.readlines())
    similar = ''
    for line in line_match_gen:
        #if line != '' and line[0] != '+' and line[0] != '-' and line[0] != '@':
        similar += line
    return similar

async def status_check(event: cdp.network.ResponseReceived):
    if (event.response.url == 'https://www.viator.com/'):
        status_code = event.response.status
        try:
            assert status_code == 200
            print('status ok')
        except():
            print(f'Received a {status_code} status code. Exiting program...')
            quit()

async def count_elements(page):
    element_count = len(await page.select_all('[data-automation]'))
    return element_count


async def get_page_hash(driver, url):
    page = await driver.get(url)
    content = await page.get_content()
    hash = str(hashlib.md5(content.encode()).hexdigest())
    return hash


# asyncio.run(main())
# asyncio results in errors when running
# This is replaced with the following 'if' block

if __name__ == '__main__':
    # Runs the program without errors
    loop().run_until_complete(main())
