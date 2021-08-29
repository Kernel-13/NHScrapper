import os
import re
import sys
import json
import time
import shutil
import requests
from tqdm import tqdm
from datetime import datetime
from bs4 import BeautifulSoup

ImageFileExtensions = ['.png', '.jpg', '.gif']

def download_book(book):
	"""Downloads an entire book."""

	try:
		url = "https://nhentai.net/g/{}"
		nh_repository = "https://i.nhentai.net/galleries/{}/{}"
		response = requests.get(url.format(book))

		os.makedirs(book, exist_ok=True)
		book_info = get_book_info(book, response)

		for i in tqdm(range(1, book_info['pages']+1), desc="Downloading Book {} ".format(book)):
			try:
				for ext in ImageFileExtensions:
					filename =  str(i) + ext
					image = requests.get(nh_repository.format(book_info['gallery_id'], filename), stream=True)
					time.sleep(3)

					if image.status_code != 404:

						file_path = os.path.join(book, str(i).zfill(3) + ext)
						image.raw.decode_content = True

						fd = open(file_path, "wb")
						shutil.copyfileobj(image.raw, fd)
						fd.close()
						break

			except Exception as e:
				raise

	except Exception as e:
		raise

def get_book_info(book, response):
	"""Saves a book's information into a JSON file, and returns a dict with said information.

	Arguments:
    book -- String. The book ID
    response -- Response object. Contains the book's page information
    """
	try:
		soup = BeautifulSoup(response.text, "html.parser")
		gallery_info = soup.find_all(class_='tags')
		book_info = {}
		book_info['title'] 			= soup.h1.text		
		book_info['title_original']	= soup.h2.text 		
		book_info['title_pretty']	= soup.title.text.split('»')[0].strip()
		
		book_info['book_id'] = int(book)
		book_info['gallery_id'] = int(soup.find_all('img')[2]['src'].split('/')[-2])
		book_info['pages'] 		= int(gallery_info[7].span.text)
		
		book_info['parodies'] 	= [x.span.text for x in gallery_info[0]]
		book_info['characters'] = [x.span.text for x in gallery_info[1]]
		book_info['tags'] 		= [x.span.text for x in gallery_info[2]]
		book_info['artists'] 	= [x.span.text for x in gallery_info[3]]
		book_info['groups'] 	= [x.span.text for x in gallery_info[4]]
		book_info['languages'] 	= [x.span.text for x in gallery_info[5]]
		book_info['categories'] = [x.span.text for x in gallery_info[6]]

		book_info['download_date'] 	= datetime.strftime(datetime.now(), "%d/%m/%y %X")
		book_info['upload_unix'] 	= int(re.search(r"upload_date.......(\d+)", response.text)[1])
		book_info['upload_date'] 	= datetime.strftime(datetime.fromtimestamp(book_info['upload_unix']), "%d/%m/%y %X")
		book_info['uploaded'] 		= gallery_info[8].text

		json_content= json.dumps(book_info, indent = 4, ensure_ascii=False)
		json_path = os.path.join(book, '{}.json'.format(book))

		with open(json_path, 'w', encoding='utf-8') as fd:
			fd.write(json_content)

		return book_info
	except KeyboardInterrupt:
		raise
	except Exception as e:
		raise

if __name__ == '__main__':
	for book in sys.argv[1:]:
		download_book(book)
