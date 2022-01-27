import bs4
import requests
import re

response = open('Appreciative Living Ch2','r', encoding='utf-8')

soup = bs4.BeautifulSoup(response, "lxml")

for tag in soup.find_all(True):
    tag.attrs = {}

for script_tag in soup.find_all("script"):
    script_tag.decompose()

for a_tag in soup.find_all("a"):
    a_tag.decompose()

for header_tags in soup.find_all(["h1","h2","h3","h4","li"]):
    header_tags.name = "p"
    header_tags.insert_after("hr")

for em_tag in soup.find_all(["em","i","strong"]):
    em_tag.name = "emphasis"
    em_tag['level'] = "moderate"

for break_tag in soup.find_all(["hr"]):
    break_tag.name = "break"
    break_tag['time'] = "1s"

for all_tags in soup.find_all():
    if len(all_tags.get_text(strip=True)) == 0:
        # Remove empty tag
        all_tags.extract()

text = ""
for accepted_tag in soup(["p","break","emphasis"]):
    text += str(accepted_tag)

patterns =["</?div>","</?span>","</?a>","</?svg>","</?path>","</?button>"]
for pattern in patterns:
    text = re.sub(r'{}'.format(pattern),"",text)


output = re.sub(u'[\u201c\u201d]','"',text)

f = open("output.txt", "a", encoding='utf-8')
f.write(output)
f.close()