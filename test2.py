import bs4
import requests
import re

url = 'http://www.nytimes.com/2021/04/19/well/mind/covid-mental-health-languishing.html'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
request = requests.get(url, headers=headers)
response = request.content

soup = bs4.BeautifulSoup(response, "lxml")

for tag in soup.find_all(True):
    tag.attrs = {}

for script_tag in soup.find_all("script"):
    script_tag.decompose()

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

original_chunk_size = 4970
chunks = []
while len(text) > 0:
    chunk_size = original_chunk_size
    if len(text) < chunk_size:
        chunks.append("<speech>" + text + "</speech>")
        print("full text:" + chunks[0])
        break
    while chunk_size > 0:
        if re.match(r'</p>$',text[:chunk_size]) == False:
            chunk_size -= 1
        else:
            chunk_size += 4
            chunks.append("<speech>" + text[:chunk_size] + "</speech>")
            chunk_num = (len(chunks))
            print(chunk_num + )
            text = text[chunk_size:]
            chunk_size = original_chunk_size
            break
            break
    if chunk_size == 0:
        chunks.append("<speech>" + text + "</speech>")
        break

