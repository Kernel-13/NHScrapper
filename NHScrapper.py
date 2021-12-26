import os
import re
import sys
import json
import NHDB
import time
import shutil
import argparse
import requests
from tqdm import tqdm
from datetime import datetime
from bs4 import BeautifulSoup

ImageFileExtensions = ['.png', '.jpg', '.gif']
nh_options = None

def download_book(book):
	"""Downloads an entire book."""

	try:
		url = "https://nhentai.net/g/{}"
		nh_repository = "https://i.nhentai.net/galleries/{}/{}"
		response = requests.get(url.format(book))

		os.makedirs(book, exist_ok=True)
		book_info = get_book_info(book, response)
		num_pages = 1 if nh_options.peek else book_info['pages']

		for i in tqdm(range(1, num_pages+1), desc="Downloading Book {} ".format(book)):
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
		
		book_info['parodies'] 	= [tag.span.text for tag in gallery_info[0]]
		book_info['characters'] = [tag.span.text for tag in gallery_info[1]]
		book_info['tags'] 		= [tag.span.text for tag in gallery_info[2]]
		book_info['artists'] 	= [tag.span.text for tag in gallery_info[3]]
		book_info['groups'] 	= [tag.span.text for tag in gallery_info[4]]
		book_info['languages'] 	= [tag.span.text for tag in gallery_info[5]]
		book_info['categories'] = [tag.span.text for tag in gallery_info[6]]

		book_info['download_date'] 	= datetime.strftime(datetime.now(), "%Y/%m/%d %X")
		book_info['upload_unix'] 	= int(re.search(r"upload_date.......(\d+)", response.text)[1])
		book_info['upload_date'] 	= datetime.strftime(datetime.fromtimestamp(book_info['upload_unix']), "%Y/%m/%d %X")
		book_info['uploaded'] 		= gallery_info[8].text

		NHDB.add_book(book_info)

		json_content= json.dumps(book_info, indent = 4, ensure_ascii=False)
		json_path = os.path.join(book, '{}.json'.format(book))

		with open(json_path, 'w', encoding='utf-8') as fd:
			fd.write(json_content)

		if nh_options.json:
			book_info['pages'] = 0

		return book_info
	except KeyboardInterrupt:
		raise
	except Exception as e:
		raise

def main():
	
	for book in nh_options.books:
		if nh_options.remove:
			NHDB.delete_book(book)
		elif nh_options.stars:
			NHDB.rate_book(book, nh_options.stars[0])
		else:
			download_book(book)

	NHDB.conn.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	
	parser.add_argument('-b', '--books', help="IDs of the books you want to download.", nargs='+', metavar=('BOOK_ID'))
	parser.add_argument('-j', '--json', help="Downloads only the JSON file, not the images.", action='store_true')
	parser.add_argument('-p', '--peek', help="Downloads only the first page / cover of the book.", action='store_true')

	# Database Operations
	parser.add_argument('-rm', '--remove', help="Deletes both the book (folder) and entry in your DB.", action='store_true')
	parser.add_argument('-st', '--stars', help="Updates the rating value (0 to 5) of one book", nargs=1, metavar=('STARS'))

	nh_options = parser.parse_args()
	main()