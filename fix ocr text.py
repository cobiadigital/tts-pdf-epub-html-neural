from google.cloud import texttospeech
import os
#from contextlib import closing
import bs4
import re

    with open('ThoughtsandLanguagepart1.txt', 'r') as file:
        response = file.read()

respo= re.sub(r'{}'.format(pattern),"",text)

f = open("fixed-text.txt", "a", encoding='utf-8')
f.write(output)
f.close()