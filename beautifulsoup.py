import bs4
from urllib.request import Request, urlopen
from copy import copy
url = Request('https://benbrenner.com/Text/betterstories.html', headers={'User-Agent': 'Mozilla/5.0'})
response = urlopen(url).read()
soup = bs4.BeautifulSoup(response, "lxml")



p_tags = soup("p")
for p_tag in p_tags:
    if p_tag.attrs:
        del p_tag.attrs

header_tags = soup.find_all(["h1","h2","h3","h4","li"])

#hr_tag = soup.new_tag("hr", length="1")

for header_tag in header_tags:
    if header_tag.attrs:
        del header_tag.attrs
    header_tag.name = "p"
    header_tag.insert_after(soup.new_tag("hr", length="1"))

hr_tags = soup("hr")
for hr_tag in hr_tags:
    hr_tag.name = "break"

emphasis = soup(["em","i"])
for emph in emphasis:
    emph.name = "emphasis"
    emph['level'] = "moderate"

print(soup.body.prettify())
text = str(soup(["p","break"]))







import bs4
from urllib.request import Request, urlopen
from copy import copy
markup = '<html><head><title>testing</test><body><h1>heading text</h1><h2>header 2</h2><p style="margin-left: 0">I linked to <i>example.com</i></p> <p style="margin-left: 0">second paragraph <i>example.com</i></p></body></html>'
soup = bs4.BeautifulSoup(markup, "lxml")


li_tags = ol_tags[0].children



emphasis = soup(["em","i"])
for emph in emphasis:
    emph.name = "emphasis"
    emph['level'] = "moderate"

header_tags = soup.find_all(["h1","h2","h3","h4"])
for header_tag in header_tags:
    header_tag.name = "p"
    header_tag.insert_after("<break length='1'")

p_tags = soup.find_all(["p"])
for p_
if p_tags[0].attrs:
    del ol_tags[0].attrs

new_p_tag = soup.new_tag("p")
new_p_tag.contents = p_tags[0].contents
p_tags[0].replace_with(new_p_tag)


root = soup.find('li').parent
for content in list(root.contents):
    if content.name == 'li':
        if (content.contents):
            content.insert_before("<list-item>")




    if (p.contents):
        root.contents.append(p)
    if (root.name == 'p'):
        root.unwrap()

        ol_tags = soup.find_all("ol")
        if ol_tags[0].attrs:
            del ol_tags[0].attrs
        for child in ol_tags[0].children:
            print(child.name)
            del child.attrs

text_list = "<speech>"
p_tags = soup.find_all(["p", "h1", "h2", "h3"])
for p_tag in p_tags:
    if p_tag.attrs:
        del p_tag.attrs
    p_tag_element = p_tag.extract()
    text_list += p_tag_element
text = "<speech>".join(text_list)