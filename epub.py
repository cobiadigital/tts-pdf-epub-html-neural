import ebooklib
from ebooklib import epub
import codecs

def epub_to_html(filename):
    book = epub.read_epub('Learned_Optimism.epub')
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

    chapters = []
    for item in items:
        if 'introduction' in item.get_name():
            chapters.append(item.content)
    for item in items:
        chapters.append(item.content)

    return chapters

