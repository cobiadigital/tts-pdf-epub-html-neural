import pdftotree
import bs4
import re

pdf_file = "Data/IJNTCW_22-01-Grant.pdf"

pdftotree.parse(pdf_file, html_path=None, model_type=None, model_path=None, favor_figures=False, visualize=False)

soup = bs4.BeautifulSoup(pdf_content, "lxml")S
for meta_tag in soup.find_all("meta"):
    meta_tag.decompose()

with open("output/soup.html", "w") as file:
    file.write(str(soup))

content_edited = re.sub('\n', ' ', pdf_content)

content_edited = re.sub('\n\n\n', '', pdf_content)
content_edited = re.sub('\n', ' ', content_edited)
content_edited = re.sub('- ', '', content_edited)
with open('output/content_edited.txt', "w") as file:
    file.write(pdf_content)


# safe_text = raw.encode('utf-8', errors='ignore')
#
# safe_text = str(safe_text).replace("\n", "").replace("\\", "")
# print('--- safe text ---' )
# print( safe_text )


#java -Djava.awt.headless=true -jar /usr/local/Cellar/tika/1.5/libexec/tika-app-1.5.jar foo.pdf
