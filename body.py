#!/usr/bin/python
# -*- coding: utf-8 -*-
import json, time, sys, subprocess, os, requests, random

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from selenium import webdriver
from vk_api import VkApi

from picture_processing import *
from utils import *

class BoenBot:

    def __init__(self):
        with open('boen_settings.json', encoding='utf-8') as json_file:
            self.BoenSettings = json.load(json_file)

        vkBotSession = VkApi(token=self.BoenSettings['accessToken'])
        self.longPoll = VkBotLongPoll(vkBotSession, self.BoenSettings['groupId'])
        self.vk = vkBotSession.get_api()
        random.seed()

        self.opts = webdriver.FirefoxOptions()
        self.opts.add_argument("--headless")
        self.opts.add_argument("--disable-gpu")

    def send_message(self, peer_id, message, reply = None, attach = None):
        self.vk.messages.send(
            peer_id=peer_id,
            message=message,
            attachment=attach,
            reply_to=reply,
            random_id=get_random_id(),
        )

    def mainloop(self):
        while True:
            try:
                for event in self.longPoll.listen():
                    self.event = event
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        self.from_id = event.obj['from_id']  # id пользователя, который отправил сообщение
                        self.peer_id = event.obj['peer_id']  # peer_id беседы или ЛС, откуда пришло сообщение
                        self.cache_path = f'{os.getcwd()}/casch/{self.peer_id}'
                        self.reply = event.obj['id']
                        
                        #print(event.obj)

                        #wall: event.obj['attachments'][i]['type'] == 'wall'
                        #photo on wall: event.obj['attachments'][i]['wall']['attachments'][j]['type'] == 'photo'
                        #event.obj['attachments'][i]['wall']['attachments'][j]['photo']['sizes'][3]['url']

                        self.message = event.obj['text'].lower() # Для регистронезависимости
                        print(f'__________________________________________________________________\n{time.ctime(time.time())[4:-5]}| Got message: "{self.message}" From: {self.from_id} In {self.peer_id}\n——————————————————————————————————————————————————————————————————')
                        
                        if self.message == 'ответь':
                            self.send_message(self.peer_id, 'Отвечаю', event.obj['id'])
                        
                        if self.message in ['боен молчи', 'боен молчать', ',jty vjkxb', ',jty vjkxfnm']:
                            if self.from_id != 155523158:
                                self.send_message(self.peer_id, random.choice(self.BoenSettings['accessDen']))
                                continue
                            self.send_message(self.peer_id, 'Как скажешь.....')
                            self.BoenSettings['mute'] = 1
                            continue
                        
                        if self.message in ['боен прости', 'боен привет']:
                            if self.from_id != 155523158:
                                self.send_message(self.peer_id, random.choice(self.BoenSettings['accessDen']))
                                continue
                            self.send_message(self.peer_id, random.choice(['Привет', 'Я скучал', 'Ага...', 'Я тут']))
                            self.BoenSettings['mute'] = 0
                            continue

                        if self.BoenSettings['mute'] == 1 or (self.from_id in self.BoenSettings['ignoredIDs']):
                            continue
                        
                        if self.message == 'боен арт' :
                            self.send_message(self.peer_id, 'Ща, погодь...', event.obj['id'])
                            psi = '1.0'
                            if 'софт' in self.message:
                                psi = '0.3'
                            if 'пиздец' in self.message:
                                psi = '2.0'
                            random_art(psi, self)
                            continue
                        
                        if 'reply_message' in event.obj:
                            if self.message in ['поиск', 'сурс']:
                                if event.obj['reply_message']['attachments'][0]['type'] == 'photo':
                                    photo = event.obj['reply_message']['attachments'][0]['photo']['sizes'][3]['url']
                                    search_image(photo, self)

                        for attach in event.obj['attachments']:
                            message_processing(attach, self)
                        
                        for i in range(len(event.obj['fwd_messages'])):
                            fwdflag = True
                            for member in self.vk.messages.getConversationMembers(peer_id=self.peer_id)['items']:
                                if event.obj['fwd_messages'][0]['from_id'] == member['member_id']: fwdflag = False
                                else: continue
                            if not fwdflag: continue
                            for attach in event.obj['fwd_messages'][i]['attachments']:
                                message_processing(attach, self)
                        
                        if self.message == 'боен пока':
                            if self.from_id != 155523158:
                                self.send_message(self.peer_id, random.choice(self.BoenSettings['accessDen']))
                                continue
                            self.send_message(self.peer_id, 'ок.....')
                            sys.exit()
                        
                        elif self.message == 'боен хуярь': #удаление дубликатов пикч в папке путем перекачивания из файла
                            if self.from_id != 155523158:
                                self.send_message(self.peer_id, random.choice(self.BoenSettings['accessDen']))
                                continue
                            self.send_message(self.peer_id, 'Дампаю хуйню...')
                            dump_file = open(f'{self.cache_path}/photos.txt', 'r')
                            for line in dump_file:
                                print(f'------------------------------------------\n{line}------------------------------------------')
                                if line == '\n':
                                    continue
                                img = requests.get(line, verify=False)
                                line = f'{line[:line.find(".jpg")]}.jpg'
                                img_file = open(f'{self.cache_path}/{line[-16:-1]}', 'wb')
                                img_file.write(img.content)
                                img_file.close()
                                self.BoenSettings['dumping'] = 1
                                walker(line[-16:-1], self)
                                self.BoenSettings['dumping'] = 0
                            dump_file.close()
                            self.send_message(self.peer_id, 'Вроде всё перекачал')
                        
                        elif self.message == 'боен чисти': #удаление дубликатов в текстовом файле
                            if self.from_id != 155523158:
                                self.send_message(self.peer_id, random.choice(self.BoenSettings['accessDen']))
                                continue
                            self.send_message(self.peer_id, 'Достаю вилку...')
                            dump_file = open(f'{self.cache_path}/photos.txt', 'r')
                            for line in dump_file:
                                print(line)
                                if line == '\n':
                                    continue
                                if line in self.BoenSettings['dump_str']:
                                    self.send_message(self.peer_id, '*чик*')
                                    print(f'removed {line}')
                                    continue
                                self.BoenSettings['dump_str'] += line
                            dump_file.close()
                            dump_file = open(f'{self.cache_path}/photos.txt', 'w')
                            dump_file.write(self.BoenSettings['dump_str'])
                            dump_file.close()
                            self.BoenSettings['dump_str'] = ''
                            self.send_message(self.peer_id, 'Вроде все дубликаты ссылок удалил')
                        
                        elif self.message == 'боен рестарт' or self.message == 'боен ресет': #рестарт
                            if self.from_id != 155523158:
                                self.send_message(self.peer_id, random.choice(self.BoenSettings['accessDen']))
                                continue
                            self.send_message(self.peer_id, 'Выхожу в окно')
                            #subprocess.Popen(['python.exe', 'restart.py'])
                            sys.exit()
                        
                        elif 'баян' in self.message or 'боян' in self.message or 'боен' in self.message :
                            self.send_message(self.peer_id, random.choice(['Это аккордеон', 'Не', 'Не не', 'Не не не', 'Да не', 'Обязательно', 'Я тута', 'Звал?', 'Кнешн', 'Нахуй']), self.reply, None)
                        print('|||||||||||||||||||||||||||||||||||||||||||||||||||||End of message|||||||||||||||||||||||||||||||||||||||||||||||||||||')
            except requests.exceptions.ReadTimeout:
                print('...................VK опять ебанулся...................')
                time.sleep(3)
                continue
                '''	time.sleep(3)
            except ssl.SSLCertVerificationError:
                print('...................VK опять ебанулся, но по-новому...................')'''
            '''
            except Exception:
                send_message(2000000001, random.choice(BoenSettings['errMsg']), None, None)
                time.sleep(3)'''
            if not sys.warnoptions:
                import warnings
                warnings.simplefilter('ignore')

if __name__ == '__main__':
    pass