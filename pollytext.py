import bs4
import re

def pollytext(response):

# with open(filename, 'r', encoding='utf-8') as file:

    soup = bs4.BeautifulSoup(response, "lxml")

    for script_tag in soup.find_all("script"):
        script_tag.decompose()

    #find all epub header tags
    for epub_h1_tag in soup.find_all("p", class_=re.compile(r"H\d")):
        epub_h1_tag.attrs = {}
        hr_tag = soup.new_tag('hr')
        epub_h1_tag.insert_after(hr_tag)

    # remove footnote numbers
    for sup_tag in soup.find_all("sup"):
        sup_tag.decompose()

    #     for a_tag in soup.find_all("a"):
    #      a_tag.decompose()

    #Adding pause after headings and lists
    for header_tags in soup.find_all(["h1", "h2", "h3", "h4", "li"]):
        hr_tag = soup.new_tag('hr')
        header_tags.name = "p"
        header_tags.insert_after(hr_tag)


    #making epub's italics into emphasis
    for epub_i_tag in soup.find_all("span", class_="ePub-I"):
        epub_i_tag.attrs = {}
        epub_i_tag.name = "emphasis"
        epub_i_tag['level'] = "moderate"

    for em_tag in soup.find_all(["em", "i", "strong"]):
        em_tag.attrs = {}
        em_tag.name = "emphasis"
        em_tag['level'] = "moderate"

    #change <hr> to <break time='1s'>
    for break_tag in soup.find_all(["hr"]):
        break_tag.name = "break"
        break_tag['time'] = "1s"

    #removed because it was removing <hr> tags
    # for all_tags in soup.find_all():
    #     if len(all_tags.get_text(strip=True)) == 0:
    #         # Remove empty tag
    #         all_tags.decompose()

    #removed because it gets rid of the attrs that we just added
    # for tag in soup.find_all(True):
    #     tag.attrs = {}

    text = ""
    for accepted_tag in soup(["p", "break", "emphasis"]):
        text += str(accepted_tag)

    patterns = ["</?div(.*?)?", "</?span(.*?)?>", "</?a(.*?)?>", "</?svg(.*?)?>", "</?path(.*?)?>", "</?button(.*?)?>"]
    for pattern in patterns:
        text = re.sub(r'{}'.format(pattern), "", text)



    output = re.sub(u'[\u201c\u201d]', '"', text)
    print(len(output))
    sep = '.'
    rest = output

    #Because single invocation of the polly synthesize_speech api can
    # transform text with about 1,500 characters, we are dividing the
    # post into blocks of approximately 1,000 characters.
    textBlocks = []
    while (len(rest) > 1400):
        begin = 0
        end = rest.find("<p>", 1000)

        if (end == -1):
            end = rest.find(" ", 1000)

        textBlock = rest[begin:end]
        rest = rest[end:] #Remove the annoying "Dot" that otherwise starts each new block since you no longer start on that index.
        textBlocks.append("<speak>" + textBlock + "</speak>")
    textBlocks.append("<speak>" + rest + '<break time="3s"/></speak>')
    with open("output.txt", "w") as text:
        # Write the response to the output file.
        text.write(str(textBlocks))
    return textBlocks