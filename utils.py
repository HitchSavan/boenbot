#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests, os, random, platform

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver


def search_image(image_url_to_find, boenBody):
    boenBody.send_message(boenBody.peer_id, 'Ща, погодь')
    find_message = ''
    
    print(f'Running on {platform.system()}')
    if platform.system() == 'Windows':
        driver = webdriver.Firefox(executable_path=f'{os.getcwd()}/geckodriver.exe') #для винды
    else:
        driver = webdriver.Firefox(executable_path=f'{os.getcwd()}/geckodriver', firefox_options=boenBody.opts) #для убунту

    driver.implicitly_wait(10)

    driver.get('https://yandex.ru/images/')

    try:
        search_button_element = driver.find_element('xpath', '/html/body/header/div/div[2]/div[1]/form/div[1]/span/span/button')
        search_button_element.click()
        search_button_element.click()
        print('Finded searchfield...')
        try:
            search_element = driver.find_element('class name', 'Textinput-Control')
            search_element.send_keys(image_url_to_find)
            search_element.send_keys(Keys.RETURN)
        except:
            search_element = driver.find_element('class name', 'Textinput-Control')
            search_button_element.click()
            search_element.send_keys(image_url_to_find)
            search_element.send_keys(Keys.RETURN)
        print('Searching...')

        alt_res_element = driver.find_element('xpath', '//div[@class="CbirSimilar-Thumb"]/a[1]')
        alt_res_url = alt_res_element.get_attribute('href')
        

        try:
            print('Trying to find Twitter...')
            res_element = driver.find_element('partial link text', 'Твиттер')
            print(res_element.text)
            print(res_element.get_attribute('href'))

            find_message += f'Попытка в твиттер: {res_element.text}: {res_element.get_attribute("href")}\nИли это (первая ссылка): {alt_res_url}'
            boenBody.send_message(boenBody.peer_id, find_message, boenBody.event.obj['id'])
        except NoSuchElementException:
            print('Failed to find Twitter')
            find_message += f'В твиттере нема...'
            try:
                similar_images = driver.find_elements('class name', 'CbirSimilar-Thumb')
                random.choice(similar_images[:5]).click()
                print('Opened similar images')

                res_element = driver.find_element('class name', 'MMImage-Origin')
                res_img_url = res_element.get_attribute('src')
                print('Finded similar image')

                art = requests.get(res_img_url, stream=True, headers={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)", "Referer": "http://example.com"}, timeout=5)
                if not os.path.exists(f'{boenBody.cache_path}/buf'):
                    os.mkdir(f'{boenBody.cache_path}/buf')
                art_file = open(f'{boenBody.cache_path}/buf/random_art.png', 'wb')
                art_file.write(art.content)
                art_file.close()
                upload_url = boenBody.vk.photos.getMessagesUploadServer(peer_id=boenBody.peer_id)['upload_url']
                response = boenBody.vk._vk.http.post(upload_url, files={'photo': open(f'{boenBody.cache_path}/buf/random_art.png', 'rb')})
                attcm = boenBody.vk.photos.saveMessagesPhoto(**response.json())
                find_message += f'\nНо вот что-то похожее\nНу или мб это: {alt_res_url}'
                print(find_message)
                boenBody.send_message(boenBody.peer_id, find_message, boenBody.event.obj['id'], f'photo{attcm[0]["owner_id"]}_{attcm[0]["id"]}')
            except Exception as e:
                print('SEARCH FAILED')
                boenBody.send_message(boenBody.peer_id, f'Я не смог....\n{e}', boenBody.event.obj['id'])
                pass
    except NoSuchElementException as e:
        boenBody.send_message(boenBody.peer_id, f'Яндексы опять что-то намутили....\n{e}', boenBody.event.obj['id'])
    driver.quit()

def random_art(psi, boenBody):
    art = requests.get(f'https://thisanimedoesnotexist.ai/results/psi-{psi}/seed{random.randint(10000, 99999)}.png',
        stream=True,
        headers={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)",
            "Referer": "http://example.com"},
        timeout=5)
    if not os.path.exists(f'{boenBody.cache_path}/buf'):
        os.mkdir(f'{boenBody.cache_path}/buf')
    art_file = open(f'{boenBody.cache_path}/buf/random_art.png', 'wb')
    art_file.write(art.content)
    art_file.close()
    upload_url = boenBody.vk.photos.getMessagesUploadServer(peer_id=boenBody.peer_id)['upload_url']
    response = boenBody.vk._vk.http.post(upload_url, files={'photo': open(f'{boenBody.cache_path}/buf/random_art.png', 'rb')})
    attcm = boenBody.vk.photos.saveMessagesPhoto(**response.json())
    boenBody.send_message(boenBody.peer_id, 'Во', boenBody.event.obj['id'], f'photo{attcm[0]["owner_id"]}_{attcm[0]["id"]}')

if __name__ == '__main__':
    pass