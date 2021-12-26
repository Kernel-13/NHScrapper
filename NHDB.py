import os
import shutil
import sqlite3

conn = sqlite3.connect('NHDatabase.db')
cursor = conn.cursor()

def add_book(book_info):
	"""Adds a book to the database.

	Arguments:
    book_info -- Dictionary containing the book's information
    """
	try:
		cursor.execute("INSERT OR IGNORE INTO Books VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (book_info['book_id'],
			book_info['title'], book_info['title_original'], book_info['title_pretty'], book_info['pages'], ', '.join(book_info['artists']), ', '.join(book_info['groups']),
			', '.join(book_info['parodies']), ', '.join(book_info['characters']), ', '.join(book_info['tags']), ', '.join(book_info['categories']),
			', '.join(book_info['languages']), book_info['download_date'], book_info['upload_date'], 0, book_info['gallery_id'],))
		conn.commit()
	except sqlite3.IntegrityError as e:
		raise

def delete_book(book_id):
	"""Deletes a book from the database and deletes the folder associated with it.

	Arguments:
    book_id -- String.
    """
	shutil.rmtree(book_id, ignore_errors=True)
	cursor.execute("DELETE FROM Books WHERE book_id=?", (int(book_id),))
	conn.commit()

def rate_book(book_id, rating):
	"""Updates the rating value of a book.

	Arguments:
    book_id -- String
    rating -- Integer. Will be converted otherwise.
    """
	try:
		rating = int(rating)
	except ValueError:
		print("You need to enter a number between 0 and 5.")
		return

	if rating < 0: 		rating = 0
	elif rating > 5:	rating = 5

	cursor.execute("UPDATE Books SET book_rate=? WHERE book_id=?", (rating, int(book_id),))
	conn.commit()
