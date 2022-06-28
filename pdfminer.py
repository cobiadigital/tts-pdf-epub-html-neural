from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import bs4
import re

fin = open('Data/IJNTCW_22-01-Grant.pdf', 'rb')
output_string = StringIO()
extract_text_to_fp(fin, output_string, laparams=LAParams(), output_type='html', codec=None)

soup = bs4.BeautifulSoup(output_string.getvalue(), "lxml")
for meta_tag in soup.find_all("meta"):
    meta_tag.decompose()


for header_tags in soup.find_all('span', attrs = {'style':'font-family: TimesNewRomanPSMT; font-size:12px'}):
#     end_tag = soup.new_tag('end')
#     start_tag = soup.new_tag('start')
    hr_tag = soup.new_tag('hr')
    header_tags.insert_after(hr_tag)

for secondary_header in soup.find_all('span', attrs = {'style':'font-family: GalliardStd-Bold; font-size:12px'}):
    hr_tag = soup.new_tag('hr')
    header_tags.insert_after(hr_tag)

for italics in soup.find_all('span', attrs = {'style':'font-family: TimesNewRomanPSMT; font-size:12px'}):
    italics.name = "em"

for brtags in soup.find_all('br'):
    brtags.decompose()

for break_tag in soup.find_all(["hr"]):
    break_tag.name = "break"
    break_tag['time'] = "1s"

for span_tag in soup.find_all(["span"]):
    span_tag.name = "p"

with open("output/soup.html", "w") as file:
    file.write(str(soup))

text = ""
for accepted_tag in soup(["p", "break"]):
    text += str(accepted_tag)
content_edited = re.sub('- ', '', soup)

# safe_text = raw.encode('utf-8', errors='ignore')
#
# safe_text = str(safe_text).replace("\n", "").replace("\\", "")
# print('--- safe text ---' )
# print( safe_text )


#java -Djava.awt.headless=true -jar /usr/local/Cellar/tika/1.5/libexec/tika-app-1.5.jar foo.pdf
