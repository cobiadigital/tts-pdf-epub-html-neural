import json
from tika import parser
import bs4
import re
import os

def pollytext(response):

    pdf_parsed = parser.from_file(response, xmlContent=True)
    pdf_content = pdf_parsed["content"]
    soup = bs4.BeautifulSoup(pdf_content, "lxml")
    # for meta_tag in soup.find_all("meta"):
    #     meta_tag.decompose()

    with open("output/soup.html", "w") as file:
        file.write(str(soup))

    text = ""
    for accepted_tag in soup(["p", "break"]):
        text += str(accepted_tag)
    #fix line-break hyphens
    text = re.sub('-\n', '', text)
    text = re.sub('\n', ' ', text)
    # Get rid of p tags at end of page
    text = re.sub(r'(?<!\. )</p>.*?<p>', '', text)
    #text = re.sub(r'(?)\.<p>[0-9].*?p>', '', text)
    #remove http addresses
    text = re.sub(r'https*? ', '', text)
#     remove page numbers
    text = re.sub(r'<p>[0-9].*?p>', '', text)
    text = re.sub(r'<p>INTERNATIONAL JOURNAL OF NARRATIVE.*?p>', '', text)

    text = re.sub(u'\xa0', u' ', text)
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
        end = rest.rfind("</p>", 0, 1000) #rfind looks for the last case of the search term.

        if (end == -1):
            end = rest.rfind(". ", 0, 1000)
            textBlock = rest[begin:end+1]
            rest = rest[end+1:]
        else:
            textBlock = rest[begin:end+4]
            rest = rest[end+4:] #Remove the annoying "Dot" that otherwise starts each new block since you no longer start on that index.
            textBlocks.append('''
            <speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">
                 <voice name="en-GB-OliverNeural">
                     <prosody rate="0%" pitch="0%">
                         ''' + textBlock + "</prosody></voice></speak>")
    textBlocks.append("<speak>" + rest + '<break time="3s"/></speak>')
    with open("output.txt", "w") as text:
        # Write the response to the output file.
        text.write(str(textBlocks))
    return textBlocks

filename = 'subjects-of-technology-adhd.pdf'
split_tup = os.path.splitext(filename)
file_name = split_tup[0]
file_extension = split_tup[1]
filename = "Data/" + filename
textBlocks = pollytext(filename)