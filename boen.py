#!/usr/bin/python
# -*- coding: utf-8 -*-

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import sys, requests, os, cv2, time, random, subprocess, concurrent.futures, json
from pathlib import Path
from skimage.measure import compare_ssim
import numpy as np

boenkill = 0
with open('boen_settings.json') as json_file:
    BoenSettings = json.load(json_file)

def check(files, diffBase):
	i = 0
	for notBase in files:
		'''
		i += 1
		bar_len = 40
		total = len(files)
		filled_len = int(round(bar_len * i / float(total)))
		percents = round(100.0 * i / float(total), 1)
		bar = '=' * filled_len + '-' * (bar_len - filled_len)
		sys.stdout.write('[%s] %s%s\r' % (bar, percents, '%'))
		sys.stdout.flush()
		'''
		if type(notBase) != np.ndarray:
			continue
		(diffRes, diff) = compare_ssim(diffBase, notBase, full=True)
		if diffRes > 0.7:
			print('БРАТАН WARNING: SSIM: '+str(diffRes)+' with '+photo[-15:-4])
		if diffRes > 0.95:
			if dumping == 0:
				#send_message(peer_id, random.choice(boenMessage), reply)
				upload_url = vk.photos.getMessagesUploadServer(peer_id=peer_id)['upload_url']
				response = vk._vk.http.post(upload_url, files={'photo': open(cache_path+'/'+photo[-15:], 'rb')})
				attcm = vk.photos.saveMessagesPhoto(**response.json())
				vk.messages.send(
					peer_id=peer_id,
					message=(random.choice(boenMessage) + ' @id' + str(from_id)),
					attachment='photo'+str(attcm[0]['owner_id'])+'_'+str(attcm[0]['id']),
					reply_to=event.obj['id'],
					random_id=get_random_id(),
				)
				#cv2.imshow('image', notBase)
				#cv2.waitKey(5000)
				#cv2.destroyAllWindows()
			print('Dublicate removed with SSIM: '+str(diffRes)+' with '+photo[-15:-4])
			boenkill = 1
			break
	return 228

def send_message(peer_id, message, reply):
	vk.messages.send(
		peer_id=peer_id,
		message=message,
		reply_to=reply,
		random_id=get_random_id(),
	)

def walker(cache_path, photo, boenkill):
	base = cv2.imread(cache_path+'/'+photo)
	base = cv2.resize(base, (320, 320), interpolation=cv2.INTER_AREA)
	diffBase = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
	data = np.load(cache_path+'/big_pic.npz', allow_pickle=True)
	files = data['arr_0']
	data.close()
	executor = concurrent.futures.ThreadPoolExecutor()
	f1 = executor.submit(check, files[0:999], diffBase)
	f2 = executor.submit(check, files[1000:1999], diffBase)
	f3 = executor.submit(check, files[2000:2999], diffBase)
	f4 = executor.submit(check, files[3000:], diffBase)
	while not f1.done():
		time.sleep(1)
	while not f2.done():
		time.sleep(1)
	while not f3.done():
		time.sleep(1)
	while not f4.done():
		time.sleep(1)
	os.remove(cache_path+'/'+photo)
	if not boenkill:
		files = np.append(files, [diffBase, [photo]])
		np.savez_compressed(cache_path+'/big_pic', files)
		boenkill = 0
	if(len(files) > 2000):
		os.remove(str(sorted(Path(cache_path).iterdir(), key=os.path.getmtime)[0]))

if not sys.warnoptions:
	import warnings
	warnings.simplefilter('ignore')

accessToken = BoenSettings['accessToken']
groupId = BoenSettings['groupId']
dumping = BoenSettings['dumping']
mute = BoenSettings['mute']
dump_str = BoenSettings['dump_str']
accessDen = BoenSettings['accessDen']
fwdMessage = BoenSettings['fwdMessage']
boenMessage = BoenSettings['boenMessage']
errMsg = BoenSettings['errMsg']

vkBotSession = VkApi(token=accessToken)
longPoll = VkBotLongPoll(vkBotSession, groupId)
vk = vkBotSession.get_api()
random.seed()

while True:
	try:
		for event in longPoll.listen():
			if event.type == VkBotEventType.MESSAGE_NEW:
				from_id = event.obj['from_id']  # id пользователя, который отправил сообщение
				peer_id = event.obj['peer_id']  # peer_id беседы или ЛС, откуда пришло сообщение
				cache_path = os.getcwd()+'/casch/'+str(peer_id)
				reply = event.obj['id']
				#wall: event.obj['attachments'][i]['type'] == 'wall'
				#photo on wall: event.obj['attachments'][i]['wall']['attachments'][j]['type'] == 'photo'
				#event.obj['attachments'][i]['wall']['attachments'][j]['photo']['sizes'][3]['url']

				message = event.obj['text'].lower() # Для регистронезависимости
				print('__________________________________________________________________\n'+time.ctime(time.time())[4:-5]+'| Got message: "'+message+'" From: '+str(from_id)+' In '+str(peer_id)+'\n——————————————————————————————————————————————————————————————————')
				if message == 'ответь':
					vk.messages.send(
						peer_id=peer_id,
						message='Отвечаю',
						reply_to=event.obj['id'],
						random_id=get_random_id(),
					)
				if message == 'боен молчи' or message == 'боен молчать' or message == ',jty vjkxb' or message == ',jty vjkxfnm':
					if from_id != 155523158:
						send_message(peer_id, random.choice(accessDen), None)
						continue
					send_message(peer_id, 'Как скажешь.....', None)
					mute = 1
					continue
				if message == 'боен прости' or message == 'боен привет' or message == ',jty ghjcnb' or message == ',jty ghbdtn':
					if from_id != 155523158:
						send_message(peer_id, random.choice(accessDen), None)
						continue
					send_message(peer_id, random.choice(['Привет', 'Я скучал', 'Ага...', 'Я тут']), None)
					mute = 0
					continue
				if mute == 1 or from_id == 387761721:
					continue
				if 'боен арт' in message:
					vk.messages.send(
						peer_id=peer_id,
						message=('Ща, погодь...'),
						reply_to=event.obj['id'],
						random_id=get_random_id(),
					)
					psi = '1.0'
					if 'софт' in message:
						psi = '0.3'
					if 'пиздец' in message:
						psi = '2.0'
					art = requests.get('https://thisanimedoesnotexist.ai/results/psi-' + psi + '/seed'+str(random.randint(10000, 99999))+'.png', stream=True, headers={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)", "Referer": "http://example.com"}, timeout=5)
					if not os.path.exists(cache_path + '/buf'):
						os.mkdir(cache_path + '/buf')
					art_file = open(cache_path+'/buf/random_art.png', 'wb')
					art_file.write(art.content)
					art_file.close()
					upload_url = vk.photos.getMessagesUploadServer(peer_id=peer_id)['upload_url']
					response = vk._vk.http.post(upload_url, files={'photo': open(cache_path+'/buf/random_art.png', 'rb')})
					attcm = vk.photos.saveMessagesPhoto(**response.json())
					vk.messages.send(
						peer_id=peer_id,
						message=('Во'),
						attachment='photo'+str(attcm[0]['owner_id'])+'_'+str(attcm[0]['id']),
						reply_to=event.obj['id'],
						random_id=get_random_id(),
					)
					continue
				for i in range(len(event.obj['attachments'])):
					if event.obj['attachments'][i]['type'] == 'photo':
						photo = event.obj['attachments'][i]['photo']['sizes'][3]['url']
						print('\nGet picture: '+photo+'\nfrom '+str(peer_id))
						img = requests.get(photo, verify=False)
						photo = photo[:photo.find('.jpg')] + '.jpg'
						if not os.path.exists(cache_path):
							os.mkdir(cache_path)
							f = open(cache_path+'/photos.txt', 'w')
							f.close()
							cumout = np.zeros((1, 1, 1))
							np.savez_compressed(cache_path+'/big_pic', cumout)
						if photo[-15:-4]+'diff.npz' in os.listdir(path=cache_path):
							print('This photo is existed')
							send_message(peer_id, random.choice(fwdMessage), None)
							continue
						img_file = open(cache_path+'/'+photo[-15:], 'wb')
						img_file.write(img.content)
						img_file.close()
						walker(cache_path, photo[-15:], boenkill)
						f = open(cache_path+'/photos.txt', 'a+')
						f.write(photo+'\n')
						f.close()
					elif event.obj['attachments'][i]['type'] == 'wall':
						if 'copy_history' in event.obj['attachments'][i]['wall']:
							for j in range(len(event.obj['attachments'][i]['wall']['copy_history'][0]['attachments'])):
								if event.obj['attachments'][i]['wall']['copy_history'][0]['attachments'][j]['type'] == 'photo':
									photo = event.obj['attachments'][i]['wall']['copy_history'][0]['attachments'][j]['photo']['sizes'][3]['url']
									print('\nGet picture: '+photo+'\nfrom '+str(peer_id))
									img = requests.get(photo, verify=False)
									photo = photo[:photo.find('.jpg')] + '.jpg'
									if not os.path.exists(cache_path):
										os.mkdir(cache_path)
										f = open(cache_path+'/photos.txt', 'w')
										f.close()
									if photo[-15:-4]+'diff.npz' in os.listdir(path=cache_path):
										print('This photo is existed')
										send_message(peer_id, random.choice(fwdMessage), None)
										continue
									img_file = open(cache_path+'/'+photo[-15:], 'wb')
									img_file.write(img.content)
									img_file.close()
									walker(cache_path, photo[-15:], boenkill)
									f = open(cache_path+'/photos.txt', 'a+')
									f.write(photo+'\n')
									f.close()
							continue
						for j in range(len(event.obj['attachments'][i]['wall']['attachments'])):
							if event.obj['attachments'][i]['wall']['attachments'][j]['type'] == 'photo':
								photo = event.obj['attachments'][i]['wall']['attachments'][j]['photo']['sizes'][3]['url']
								print('\nGet picture: '+photo+'\nfrom '+str(peer_id))
								img = requests.get(photo, verify=False)
								photo = photo[:photo.find('.jpg')] + '.jpg'
								if not os.path.exists(cache_path):
									os.mkdir(cache_path)
									f = open(cache_path+'/photos.txt', 'w')
									f.close()
								if photo[-15:-4]+'diff.npz' in os.listdir(path=cache_path):
									print('This photo is existed')
									send_message(peer_id, random.choice(fwdMessage), None)
									continue
								img_file = open(cache_path+'/'+photo[-15:], 'wb')
								img_file.write(img.content)
								img_file.close()
								walker(cache_path, photo[-15:], boenkill)
								f = open(cache_path+'/photos.txt', 'a+')
								f.write(photo+'\n')
								f.close()
				for i in range(len(event.obj['fwd_messages'])):
					for j in range(len(event.obj['fwd_messages'][i]['attachments'])):
						if event.obj['fwd_messages'][i]['attachments'][j]['type'] == 'photo':
							photo = event.obj['fwd_messages'][i]['attachments'][j]['photo']['sizes'][3]['url']
							print('\nGet fwd picture: '+photo+'\nfrom '+str(peer_id))
							img = requests.get(photo, verify=False)
							photo = photo[:photo.find('.jpg')] + '.jpg'
							if not os.path.exists(cache_path):
								os.mkdir(cache_path)
								f = open(cache_path+'/photos.txt', 'w')
								f.close()
							if photo[-15:-4]+'diff.npz' in os.listdir(path=cache_path):
								print('This photo is existed')
								send_message(peer_id, 'СУКА\nА..\nПростите, ложная тревога', None)
								break
							img_file = open(cache_path+'/'+photo[-15:], 'wb')
							img_file.write(img.content)
							img_file.close()
							walker(cache_path, photo[-15:], boenkill)
							f = open(cache_path+'/photos.txt', 'a+')
							f.write(photo+'\n')
							f.close()
						elif event.obj['fwd_messages'][i]['attachments'][j]['type'] == 'wall':
							for k in range(len(event.obj['fwd_messages'][i]['attachments'][j]['wall']['attachments'])):
								if event.obj['fwd_messages'][i]['attachments'][j]['wall']['attachments'][k]['type'] == 'photo':
									photo = event.obj['fwd_messages'][i]['attachments'][j]['wall']['attachments'][k]['photo']['sizes'][3]['url']
									print('\nGet picture: '+photo+'\nfrom '+str(peer_id))
									img = requests.get(photo, verify=False)
									photo = photo[:photo.find('.jpg')] + '.jpg'
									if not os.path.exists(cache_path):
										os.mkdir(cache_path)
										f = open(cache_path+'/photos.txt', 'w')
										f.close()
									if photo[-15:-4]+'diff.npz' in os.listdir(path=cache_path):
										print('This photo is existed')
										send_message(peer_id, random.choice(fwdMessage), None)
										continue
									img_file = open(cache_path+'/'+photo[-15:], 'wb')
									img_file.write(img.content)
									img_file.close()
									walker(cache_path, photo[-15:], boenkill)
									f = open(cache_path+'/photos.txt', 'a+')
									f.write(photo+'\n')
									f.close()
				if message == 'боен пока' or message == ',jty gjrf':
					if from_id != 155523158:
						send_message(peer_id, random.choice(accessDen), None)
						continue
					send_message(peer_id, 'ок.....', None)
					sys.exit()
				elif message == 'боен хуярь' or message == ',jty [ezhm': #удаление дубликатов пикч в папке путем перекачивания из файла
					if from_id != 155523158:
						send_message(peer_id, random.choice(accessDen), None)
						continue
					send_message(peer_id, 'Дампаю хуйню...', None)
					dump_file = open(cache_path+'/photos.txt', 'r')
					for line in dump_file:
						print('------------------------------------------\n'+line+'------------------------------------------')
						if line == '\n':
							continue
						img = requests.get(line, verify=False)
						line = line[:line.find('.jpg')] + '.jpg'
						img_file = open(cache_path+'/'+line[-16:-1], 'wb')
						img_file.write(img.content)
						img_file.close()
						dumping = 1
						walker(cache_path, line[-16:-1], boenkill)
						dumping = 0
					dump_file.close()
					send_message(peer_id, 'Вроде всё перекачал', None)
				elif message == ',jty xbcnb' or message == 'боен чисти': #удаление дубликатов в текстовом файле
					if from_id != 155523158:
						send_message(peer_id, random.choice(accessDen), None)
						continue
					send_message(peer_id, 'Достаю вилку...', None)
					dump_file = open(cache_path+'/photos.txt', 'r')
					for line in dump_file:
						print(line)
						if line == '\n':
							continue
						if line in dump_str:
							send_message(peer_id, '*чик*', None)
							print('removed '+line)
							continue
						dump_str += line
					dump_file.close()
					dump_file = open(cache_path+'/photos.txt', 'w')
					dump_file.write(dump_str)
					dump_file.close()
					dump_str = ''
					send_message(peer_id, 'Вроде все дубликаты ссылок удалил', None)
				elif message == ',jty htcnfhn' or message == 'боен рестарт' or message == ',jty htctn' or message == 'боен ресет': #рестарт
					if from_id != 155523158:
						send_message(peer_id, random.choice(accessDen), None)
						continue
					send_message(peer_id, 'Я ща', None)
					subprocess.Popen(['python.exe', 'restart.py'])
					sys.exit()
				elif 'баян' in message or 'боян' in message or 'боен' in message :
					send_message(peer_id, random.choice(['Это аккордеон', 'Не', 'Не не', 'Не не не', 'Да не', 'Обязательно', 'Я тута', 'Звал?', 'Кнешн', 'Нахуй']), reply)
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
		send_message(2000000001, random.choice(errMsg), None)
		time.sleep(3)'''