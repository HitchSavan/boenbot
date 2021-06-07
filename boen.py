#!/usr/bin/python
# -*- coding: utf-8 -*-

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys, requests, os, cv2, time, random, subprocess, concurrent.futures, json
from pathlib import Path
from skimage.measure import compare_ssim
import numpy as np

with open('boen_settings.json', encoding='utf-8') as json_file:
    BoenSettings = json.load(json_file)

vkBotSession = VkApi(token=BoenSettings['accessToken'])
longPoll = VkBotLongPoll(vkBotSession, BoenSettings['groupId'])
vk = vkBotSession.get_api()
random.seed()

opts = webdriver.FirefoxOptions()
opts.add_argument("--headless")

def check(files, diffBase, photo):
	i = 0
	for pic in files:
		''' 									#progressbar
		i += 1
		bar_len = 40
		total = len(files)
		filled_len = int(round(bar_len * i / float(total)))
		percents = round(100.0 * i / float(total), 1)
		bar = '=' * filled_len + '-' * (bar_len - filled_len)
		sys.stdout.write('[%s] %s%s\r' % (bar, percents, '%'))
		sys.stdout.flush()
		'''
		if 'diff.npz' not in pic or pic == 'photos.txt' or pic == f'{photo[:-4]}diff.npz':
			continue
		data = np.load(f'{cache_path}/{pic}')
		notBase = data['arr_0']
		data.close()
		(diffRes, diff) = compare_ssim(diffBase, notBase, full=True)
		if diffRes > 0.7:
			print(f'БРАТАН WARNING: SSIM: {diffRes} with {pic[:-8]}')
		if diffRes > 0.95:
			if BoenSettings['dumping'] == 0:
				upload_url = vk.photos.getMessagesUploadServer(peer_id=peer_id)['upload_url']
				response = vk._vk.http.post(upload_url, files={'photo': open(f'{cache_path}/{photo}', 'rb')})
				attcm = vk.photos.saveMessagesPhoto(**response.json())
				send_message(peer_id, f'{random.choice(BoenSettings["boenMessage"])} @id{from_id}', event.obj['id'], f'photo{attcm[0]["owner_id"]}_{attcm[0]["id"]}')
				#cv2.imshow('image', notBase)           #image showing
				#cv2.waitKey(5000)
				#cv2.destroyAllWindows()
			os.remove(f'{cache_path}/{photo[:-4]}diff.npz')
			print(f'Dublicate removed with SSIM: {diffRes} with {pic[:-8]}')
			break
	return 228

def send_message(peer_id, message, reply, attach):
	vk.messages.send(
		peer_id=peer_id,
		message=message,
		attachment=attach,
		reply_to=reply,
		random_id=get_random_id(),
	)

def walker(cache_path, photo):
	base = cv2.imread(f'{cache_path}/{photo}')
	base = cv2.resize(base, (320, 320), interpolation=cv2.INTER_AREA)
	diffBase = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
	np.savez_compressed(f'{cache_path}/{photo[-15:-4]}diff', diffBase)
	files = os.listdir(path=cache_path)
	executor = concurrent.futures.ThreadPoolExecutor()
	stream1 = executor.submit(check, files[0:499], diffBase, photo)
	stream2 = executor.submit(check, files[500:999], diffBase, photo)
	stream3 = executor.submit(check, files[1000:1499], diffBase, photo)
	stream4 = executor.submit(check, files[1500:], diffBase, photo)
	while not stream1.done():
		time.sleep(1)
	while not stream2.done():
		time.sleep(1)
	while not stream3.done():
		time.sleep(1)
	while not stream4.done():
		time.sleep(1)
	os.remove(f'{cache_path}/{photo}')
	if(len(files) > 2000):
		try:
			os.remove(str(sorted(Path(cache_path).iterdir(), key=os.path.getmtime)[0]))
		except IsADirectoryError:
			os.remove(str(sorted(Path(cache_path).iterdir(), key=os.path.getmtime)[1]))

def get_photo(raw_photo):
	img = requests.get(raw_photo, verify=False)
	photo = f'{raw_photo[raw_photo.find(".jpg")-11:raw_photo.find(".jpg")]}.jpg'
	if not os.path.exists(cache_path):
		os.mkdir(cache_path)
		f = open(f'{cache_path}/photos.txt', 'w')
		f.close()
	if f'{photo[:-4]}diff.npz' in os.listdir(path=cache_path):
		print('This photo is existed')
		
		fwdflag = True
		for member in vk.messages.getConversationMembers(peer_id=peer_id)['items']:
			if len(event.obj['fwd_messages']) != 0 and event.obj['fwd_messages'][0]['from_id'] == member['member_id']: fwdflag = False
			else: continue
		if not fwdflag: return 0

		img_file = open(f'{cache_path}/{photo}', 'wb')
		img_file.write(img.content)
		img_file.close()
		base = cv2.imread(f'{cache_path}/{photo}')
		base = cv2.resize(base, (320, 320), interpolation=cv2.INTER_AREA)
		diffBase = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
		np.savez_compressed(f'{cache_path}/{photo[:-4]}difftest', diffBase)
		

		data = np.load(f'{cache_path}/{photo[:-4]}diff.npz')
		notBase = data['arr_0']
		data.close()
		(diffRes, diff) = compare_ssim(diffBase, notBase, full=True)
		if diffRes > 0.7:
			print(f'FWD БРАТАН WARNING: SSIM: {diffRes} with {photo}')
		if diffRes > 0.95:
			if BoenSettings['dumping'] == 0:
				upload_url = vk.photos.getMessagesUploadServer(peer_id=peer_id)['upload_url']
				response = vk._vk.http.post(upload_url, files={'photo': open(f'{cache_path}/{photo}', 'rb')})
				attcm = vk.photos.saveMessagesPhoto(**response.json())
				send_message(peer_id, f'{random.choice(BoenSettings["fwdMessage"])} @id{from_id}', event.obj['id'], f'photo{attcm[0]["owner_id"]}_{attcm[0]["id"]}')
			os.remove(f'{cache_path}/{photo[:-4]}difftest.npz')
			print(f'Dublicate removed with SSIM: {diffRes} with {photo}')
		else:
			os.rename(f'{cache_path}/{photo[:-4]}difftest.npz', f'{cache_path}/{photo[:-5]}{random.randint(0, 9)}diff.npz')
		return 0
	img_file = open(f'{cache_path}/{photo}', 'wb')
	img_file.write(img.content)
	img_file.close()
	walker(cache_path, photo)
	f = open(f'{cache_path}/photos.txt', 'a+')
	f.write(f'{raw_photo}\n')
	f.close()

def search_image(image_url_to_find):
	send_message(peer_id, 'Ща, погодь', None, None)
	find_message = ''
	
	driver = webdriver.Firefox(executable_path=f'{os.getcwd()}/geckodriver', firefox_options=opts) #для убунту
	#driver = webdriver.Firefox(executable_path=f'{os.getcwd()}/geckodriver.exe') #для винды
	driver.implicitly_wait(10)

	driver.get('https://yandex.ru/images/')

	search_button_element = driver.find_element_by_xpath('/html/body/header/div/div[2]/div[1]/form/div[1]/span/span/div[2]/button')
	search_button_element.click()

	search_element = driver.find_element_by_name('cbir-url')
	search_element.send_keys(image_url_to_find)
	search_element.send_keys(Keys.RETURN)

	alt_res_element = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[1]/div/div[1]/div[1]/div[2]/div[2]/div[1]/ul/li[1]/div/div[1]/a')
	alt_res_url = alt_res_element.get_attribute('href')

	try:
		res_element = driver.find_element_by_partial_link_text('Твиттер')
		print(res_element.text)
		print(res_element.get_attribute('href'))
		
		find_message += f'{res_element.text}: {res_element.get_attribute("href")}\nИли это (первая ссылка): {alt_res_element.get_attribute("href")}'
		send_message(peer_id, find_message, event.obj['id'], None)
	except:
		find_message += f'В твиттере нема...'
		try:
			similar_images = driver.find_elements_by_class_name('cbir-similar__thumb')
			random.choice(similar_images[:5]).click()

			res_element = driver.find_element_by_class_name('MMImage-Origin')
			res_img_url = res_element.get_attribute('src')

			art = requests.get(res_img_url, stream=True, headers={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)", "Referer": "http://example.com"}, timeout=5)
			if not os.path.exists(f'{cache_path}/buf'):
				os.mkdir(f'{cache_path}/buf')
			art_file = open(f'{cache_path}/buf/random_art.png', 'wb')
			art_file.write(art.content)
			art_file.close()
			upload_url = vk.photos.getMessagesUploadServer(peer_id=peer_id)['upload_url']
			response = vk._vk.http.post(upload_url, files={'photo': open(f'{cache_path}/buf/random_art.png', 'rb')})
			attcm = vk.photos.saveMessagesPhoto(**response.json())
			print(find_message)
			find_message += f'\nНо вот что-то похожее\nНу или мб это: {alt_res_url}'
			print(find_message)
			send_message(peer_id, find_message, event.obj['id'], f'photo{attcm[0]["owner_id"]}_{attcm[0]["id"]}')
		except:
			pass
		
	driver.quit()

if not sys.warnoptions:
	import warnings
	warnings.simplefilter('ignore')


while True:
	try:
		for event in longPoll.listen():
			if event.type == VkBotEventType.MESSAGE_NEW:
				from_id = event.obj['from_id']  # id пользователя, который отправил сообщение
				peer_id = event.obj['peer_id']  # peer_id беседы или ЛС, откуда пришло сообщение
				cache_path = f'{os.getcwd()}/casch/{peer_id}'
				reply = event.obj['id']
				
				#print(event.obj)

				#wall: event.obj['attachments'][i]['type'] == 'wall'
				#photo on wall: event.obj['attachments'][i]['wall']['attachments'][j]['type'] == 'photo'
				#event.obj['attachments'][i]['wall']['attachments'][j]['photo']['sizes'][3]['url']

				message = event.obj['text'].lower() # Для регистронезависимости
				print(f'__________________________________________________________________\n{time.ctime(time.time())[4:-5]}| Got message: "{message}" From: {from_id} In {peer_id}\n——————————————————————————————————————————————————————————————————')
				
				if message == 'ответь':
					send_message(peer_id, 'Отвечаю', event.obj['id'], None)
				
				if message in ['боен молчи', 'боен молчать', ',jty vjkxb', ',jty vjkxfnm']:
					if from_id != 155523158:
						send_message(peer_id, random.choice(BoenSettings['accessDen']), None, None)
						continue
					send_message(peer_id, 'Как скажешь.....', None, None)
					BoenSettings['mute'] = 1
					continue
				
				if message in ['боен прости', 'боен привет']:
					if from_id != 155523158:
						send_message(peer_id, random.choice(BoenSettings['accessDen']), None, None)
						continue
					send_message(peer_id, random.choice(['Привет', 'Я скучал', 'Ага...', 'Я тут']), None, None)
					BoenSettings['mute'] = 0
					continue

				if BoenSettings['mute'] == 1 or from_id == 387761721:
					continue
				
				if message == 'боен арт' :
					send_message(peer_id, 'Ща, погодь...', event.obj['id'], None)
					psi = '1.0'
					if 'софт' in message:
						psi = '0.3'
					if 'пиздец' in message:
						psi = '2.0'
					art = requests.get(f'https://thisanimedoesnotexist.ai/results/psi-{psi}/seed{random.randint(10000, 99999)}.png', stream=True, headers={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)", "Referer": "http://example.com"}, timeout=5)
					if not os.path.exists(f'{cache_path}/buf'):
						os.mkdir(f'{cache_path}/buf')
					art_file = open(f'{cache_path}/buf/random_art.png', 'wb')
					art_file.write(art.content)
					art_file.close()
					upload_url = vk.photos.getMessagesUploadServer(peer_id=peer_id)['upload_url']
					response = vk._vk.http.post(upload_url, files={'photo': open(f'{cache_path}/buf/random_art.png', 'rb')})
					attcm = vk.photos.saveMessagesPhoto(**response.json())
					send_message(peer_id, 'Во', event.obj['id'], f'photo{attcm[0]["owner_id"]}_{attcm[0]["id"]}')
					continue
				
				if 'reply_message' in event.obj:
					if message in ['поиск', 'сурс']:
						if event.obj['reply_message']['attachments'][0]['type'] == 'photo':
							photo = event.obj['reply_message']['attachments'][0]['photo']['sizes'][3]['url']
							search_image(photo)

				for i in range(len(event.obj['attachments'])):
					if event.obj['attachments'][i]['type'] == 'photo':
						photo = event.obj['attachments'][i]['photo']['sizes'][3]['url']
						print(f'\nGet picture: {photo}\nfrom {peer_id}')
						if message in ['поиск', 'сурс']:
							search_image(photo)
							continue
						get_photo(photo)
					if event.obj['attachments'][i]['type'] == 'wall':
						if 'copy_history' in event.obj['attachments'][i]['wall']:
							for j in range(len(event.obj['attachments'][i]['wall']['copy_history'][0]['attachments'])):
								if event.obj['attachments'][i]['wall']['copy_history'][0]['attachments'][j]['type'] == 'photo':
									photo = event.obj['attachments'][i]['wall']['copy_history'][0]['attachments'][j]['photo']['sizes'][3]['url']
									print(f'\nGet picture: {photo}\nfrom {peer_id}')
									if message in ['поиск', 'сурс']:
										search_image(photo)
										continue
									get_photo(photo)
							continue
						for j in range(len(event.obj['attachments'][i]['wall']['attachments'])):
							if event.obj['attachments'][i]['wall']['attachments'][j]['type'] == 'photo':
								photo = event.obj['attachments'][i]['wall']['attachments'][j]['photo']['sizes'][3]['url']
								print(f'\nGet picture: {photo}\nfrom {peer_id}')
								if message in ['поиск', 'сурс']:
									search_image(photo)
									continue
								get_photo(photo)
				
				for i in range(len(event.obj['fwd_messages'])):
					fwdflag = True
					for member in vk.messages.getConversationMembers(peer_id=peer_id)['items']:
						if event.obj['fwd_messages'][0]['from_id'] == member['member_id']: fwdflag = False
						else: continue
					if not fwdflag: continue
					for j in range(len(event.obj['fwd_messages'][i]['attachments'])):
						if event.obj['fwd_messages'][i]['attachments'][j]['type'] == 'photo':
							photo = event.obj['fwd_messages'][i]['attachments'][j]['photo']['sizes'][3]['url']
							print(f'\nGet fwd picture: {photo}\nfrom {peer_id}')
							if message in ['поиск', 'сурс']:
								search_image(photo)
								continue
							get_photo(photo)
						elif event.obj['fwd_messages'][i]['attachments'][j]['type'] == 'wall':
							for k in range(len(event.obj['fwd_messages'][i]['attachments'][j]['wall']['attachments'])):
								if event.obj['fwd_messages'][i]['attachments'][j]['wall']['attachments'][k]['type'] == 'photo':
									photo = event.obj['fwd_messages'][i]['attachments'][j]['wall']['attachments'][k]['photo']['sizes'][3]['url']
									print(f'\nGet picture: {photo}\nfrom {peer_id}')
									if message in ['поиск', 'сурс']:
										search_image(photo)
										continue
									get_photo(photo)
				
				if message == 'боен пока':
					if from_id != 155523158:
						send_message(peer_id, random.choice(BoenSettings['accessDen']), None, None)
						continue
					send_message(peer_id, 'ок.....', None, None)
					sys.exit()
				
				elif message == 'боен хуярь': #удаление дубликатов пикч в папке путем перекачивания из файла
					if from_id != 155523158:
						send_message(peer_id, random.choice(BoenSettings['accessDen']), None, None)
						continue
					send_message(peer_id, 'Дампаю хуйню...', None, None)
					dump_file = open(f'{cache_path}/photos.txt', 'r')
					for line in dump_file:
						print(f'------------------------------------------\n{line}------------------------------------------')
						if line == '\n':
							continue
						img = requests.get(line, verify=False)
						line = f'{line[:line.find(".jpg")]}.jpg'
						img_file = open(f'{cache_path}/{line[-16:-1]}', 'wb')
						img_file.write(img.content)
						img_file.close()
						BoenSettings['dumping'] = 1
						walker(cache_path, line[-16:-1])
						BoenSettings['dumping'] = 0
					dump_file.close()
					send_message(peer_id, 'Вроде всё перекачал', None, None)
				
				elif message == 'боен чисти': #удаление дубликатов в текстовом файле
					if from_id != 155523158:
						send_message(peer_id, random.choice(BoenSettings['accessDen']), None, None)
						continue
					send_message(peer_id, 'Достаю вилку...', None, None)
					dump_file = open(f'{cache_path}/photos.txt', 'r')
					for line in dump_file:
						print(line)
						if line == '\n':
							continue
						if line in BoenSettings['dump_str']:
							send_message(peer_id, '*чик*', None, None)
							print(f'removed {line}')
							continue
						BoenSettings['dump_str'] += line
					dump_file.close()
					dump_file = open(f'{cache_path}/photos.txt', 'w')
					dump_file.write(BoenSettings['dump_str'])
					dump_file.close()
					BoenSettings['dump_str'] = ''
					send_message(peer_id, 'Вроде все дубликаты ссылок удалил', None, None)
				
				elif message == 'боен рестарт' or message == 'боен ресет': #рестарт
					if from_id != 155523158:
						send_message(peer_id, random.choice(BoenSettings['accessDen']), None, None)
						continue
					send_message(peer_id, 'Выхожу в окно', None, None)
					#subprocess.Popen(['python.exe', 'restart.py'])
					sys.exit()
				
				elif 'баян' in message or 'боян' in message or 'боен' in message :
					send_message(peer_id, random.choice(['Это аккордеон', 'Не', 'Не не', 'Не не не', 'Да не', 'Обязательно', 'Я тута', 'Звал?', 'Кнешн', 'Нахуй']), reply, None)
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