#!/usr/bin/python
# -*- coding: utf-8 -*-
import random, os, cv2, time, concurrent.futures, requests
import numpy as np

from skimage.metrics import structural_similarity as compare_ssim
from pathlib import Path

from utils import search_image

def check(files, diffBase, photo, boenBody):
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
		data = np.load(f'{boenBody.cache_path}\\{pic}')
		notBase = data['arr_0']
		data.close()
		(diffRes, diff) = compare_ssim(diffBase, notBase, full=True)
		if diffRes > 0.7:
			print(f'БРАТАН WARNING: SSIM: {diffRes} with {pic[:-8]}')
		if diffRes > 0.95:
			if boenBody.BoenSettings['dumping'] == 0:
				upload_url = boenBody.vk.photos.getMessagesUploadServer(peer_id=boenBody.peer_id)['upload_url']
				response = boenBody.vk._vk.http.post(upload_url, files={'photo': open(f'{boenBody.cache_path}\\{photo}', 'rb')})
				attcm = boenBody.vk.photos.saveMessagesPhoto(**response.json())
				boenBody.send_message(boenBody.peer_id, f'{random.choice(boenBody.BoenSettings["boenMessage"])} @id{boenBody.from_id}', boenBody.event.obj['id'], f'photo{attcm[0]["owner_id"]}_{attcm[0]["id"]}')
				#cv2.imshow('image', notBase)		   #image showing
				#cv2.waitKey(5000)
				#cv2.destroyAllWindows()
			os.remove(f'{boenBody.cache_path}\\{photo[:-4]}diff.npz')
			print(f'Dublicate removed with SSIM: {diffRes} with {pic[:-8]}')
			break
	return 228

def walker(photo, boenBody):
	base = cv2.imread(f'{boenBody.cache_path}\\{photo}')
	base = cv2.resize(base, (320, 320), interpolation=cv2.INTER_AREA)
	diffBase = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
	np.savez_compressed(f'{boenBody.cache_path}\\{photo[-15:-4]}diff', diffBase)
	files = os.listdir(path=boenBody.cache_path)
	executor = concurrent.futures.ThreadPoolExecutor()
	stream1 = executor.submit(check, files[0:499], diffBase, photo, boenBody)
	stream2 = executor.submit(check, files[500:999], diffBase, photo, boenBody)
	stream3 = executor.submit(check, files[1000:1499], diffBase, photo, boenBody)
	stream4 = executor.submit(check, files[1500:], diffBase, photo, boenBody)
	while not stream1.done():
		time.sleep(1)
	while not stream2.done():
		time.sleep(1)
	while not stream3.done():
		time.sleep(1)
	while not stream4.done():
		time.sleep(1)
	os.remove(f'{boenBody.cache_path}\\{photo}')
	if(len(files) > 2000):
		try:
			os.remove(str(sorted(Path(boenBody.cache_path).iterdir(), key=os.path.getmtime)[0]))
		except IsADirectoryError:
			os.remove(str(sorted(Path(boenBody.cache_path).iterdir(), key=os.path.getmtime)[1]))

def get_photo(raw_photo, boenBody):
	img = requests.get(raw_photo, verify=False)
	photo = f'{raw_photo[raw_photo.find(".jpg")-11:raw_photo.find(".jpg")]}.jpg'
	if not os.path.exists(boenBody.cache_path):
		os.makedirs(boenBody.cache_path)
		f = open(f'{boenBody.cache_path}\\photos.txt', 'w')
		f.close()
	if f'{photo[:-4]}diff.npz' in os.listdir(path=boenBody.cache_path):
		print('This photo is existed')
		
		fwdflag = True
		for member in boenBody.vk.messages.getConversationMembers(peer_id=boenBody.peer_id)['items']:
			if len(boenBody.event.obj['fwd_messages']) != 0 and boenBody.event.obj['fwd_messages'][0]['from_id'] == member['member_id']: fwdflag = False
			else: continue
		if not fwdflag: return 0

		img_file = open(f'{boenBody.cache_path}\\{photo}', 'wb')
		img_file.write(img.content)
		img_file.close()
		base = cv2.imread(f'{boenBody.cache_path}\\{photo}')
		base = cv2.resize(base, (320, 320), interpolation=cv2.INTER_AREA)
		diffBase = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
		np.savez_compressed(f'{boenBody.cache_path}\\{photo[:-4]}difftest', diffBase)
		

		data = np.load(f'{boenBody.cache_path}\\{photo[:-4]}diff.npz')
		notBase = data['arr_0']
		data.close()
		(diffRes, diff) = compare_ssim(diffBase, notBase, full=True)
		if diffRes > 0.7:
			print(f'FWD БРАТАН WARNING: SSIM: {diffRes} with {photo}')
		if diffRes > 0.95:
			if boenBody.BoenSettings['dumping'] == 0:
				upload_url = boenBody.vk.photos.getMessagesUploadServer(peer_id=boenBody.peer_id)['upload_url']
				response = boenBody.vk._vk.http.post(upload_url, files={'photo': open(f'{boenBody.cache_path}\\{photo}', 'rb')})
				attcm = boenBody.vk.photos.saveMessagesPhoto(**response.json())
				boenBody.send_message(boenBody.peer_id, f'{random.choice(boenBody.BoenSettings["fwdMessage"])} @id{boenBody.from_id}', boenBody.event.obj['id'], f'photo{attcm[0]["owner_id"]}_{attcm[0]["id"]}')
			os.remove(f'{boenBody.cache_path}\\{photo[:-4]}difftest.npz')
			print(f'Dublicate removed with SSIM: {diffRes} with {photo}')
		else:
			os.rename(f'{boenBody.cache_path}\\{photo[:-4]}difftest.npz', f'{boenBody.cache_path}\\{photo[:-5]}{random.randint(0, 9)}diff.npz')
		return 0
	img_file = open(f'{boenBody.cache_path}\\{photo}', 'wb')
	img_file.write(img.content)
	img_file.close()
	walker(photo, boenBody)
	f = open(f'{boenBody.cache_path}\\photos.txt', 'a+')
	f.write(f'{raw_photo}\n')
	f.close()

def message_processing(attach, boenBody):
	if attach['type'] == 'photo':
		photo = attach['photo']['sizes'][3]['url']
		print(f'\nGet picture: {photo}\nfrom {boenBody.peer_id}')
		if boenBody.message in ['поиск', 'сурс']:
			search_image(photo, boenBody)
			return 'continue'
		get_photo(photo, boenBody)
	elif attach['type'] == 'wall':
		if 'copy_history' in attach['wall']:
			for j in range(len(attach['wall']['copy_history'][0]['attachments'])):
				if attach['wall']['copy_history'][0]['attachments'][j]['type'] == 'photo':
					photo = attach['wall']['copy_history'][0]['attachments'][j]['photo']['sizes'][3]['url']
					print(f'\nGet picture: {photo}\nfrom {boenBody.peer_id}')
					if boenBody.message in ['поиск', 'сурс']:
						search_image(photo, boenBody)
						continue
					get_photo(photo, boenBody)
			return 'continue'
		for j in range(len(attach['wall']['attachments'])):
			if attach['wall']['attachments'][j]['type'] == 'photo':
				photo = attach['wall']['attachments'][j]['photo']['sizes'][3]['url']
				print(f'\nGet picture: {photo}\nfrom {boenBody.peer_id}')
				if boenBody.message in ['поиск', 'сурс']:
					search_image(photo, boenBody)
					continue
				get_photo(photo, boenBody)

if __name__ == '__main__':
	pass