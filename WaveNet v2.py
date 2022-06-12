from google.cloud import texttospeech
import ebooklib
from ebooklib import epub
import os
#from contextlib import closing
import bs4
import re
# import pollytext

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
    #add a pause after a break_tag
    for header_tags in soup.find_all(["br"]):
        hr_tag = soup.new_tag('hr')
        header_tags.insert_before(hr_tag)

    #Adding pause after headings and lists
    for header_tags in soup.find_all(["h1", "h2", "h3", "h4", "li"]):
        hr_tag = soup.new_tag('hr')
        header_tags.name = "p"
        header_tags.insert_before(hr_tag)
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
    for accepted_tag in soup(["p", "break"]):
        text += str(accepted_tag)

    patterns = ["</?div.*?>", "</?span.*?>", "</?a.*?>", "</?svg.*?>", "</?path.*?>", "</?button.*?>"]
    for pattern in patterns:
        text = re.sub(r'{}'.format(pattern), "", text)


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
            textBlocks.append("<speak>" + textBlock + "</speak>")
    textBlocks.append("<speak>" + rest + '<break time="3s"/></speak>')
    with open("output.txt", "w") as text:
        # Write the response to the output file.
        text.write(str(textBlocks))
    return textBlocks

client = texttospeech.TextToSpeechClient.from_service_account_json(
    'text-to-speech.json')

voice = texttospeech.VoiceSelectionParams(
    language_code="en-GB", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, name="en-GB-Wavenet-C"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.0,
)
# def epub_contents(filename):
#     book = epub.read_epub(filename)
#     items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
#     return filename, chapter_names

def epub_to_html(filename, type):
    book = epub.read_epub(filename)
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    chapter_names = []
    chapters_list = []
    if type == 'approved':
  #      approved_chapters = ['frontmatter','introduction', 'chapter', 'conclusion','backmatter']
       approved_chapters = ['c13', 'c14', 'c15']

    else:
        approved_chapters = [type]
    for item in items:
        for ch_name in approved_chapters:
            if ch_name in item.get_name():
                chapter_names.append(item.get_name())
                chapters_list.append(item.content)
        else:
            pass
    return chapters_list

def synthesize_ssml(client, response, **kwargs):
    textBlocks = pollytext(response)
    print(textBlocks) #fortest
    return b"".join(
        client.synthesize_speech(input=texttospeech.SynthesisInput(ssml=textBlock), **kwargs).audio_content for textBlock in textBlocks)
    print(textBlocks) #fortest

filename = 'JohnKnox.epub'
sec_type = 'chapter_03'
split_tup = os.path.splitext(filename)
file_name = split_tup[0]
file_extension = split_tup[1]
number = 0
if file_extension == '.epub':
    chapters = epub_to_html(filename, sec_type)
    for chapter in chapters:
        audio_content = synthesize_ssml(client, chapter, voice=voice, audio_config=audio_config)
        mp3_name = file_name + str(number) + "_.mp3"
        with open(mp3_name, "wb") as out:
            out.write(audio_content)
            print('Audio content written to file' + mp3_name)
        number += 1
else:
    with open(filename, 'r', encoding='utf-8') as file:
        response = file.read()
    audio_content = synthesize_ssml(client, response, voice=voice, audio_config=audio_config)
    mp3_name = file_name + "_.mp3"
    with open(mp3_name, "wb") as out:
    # Write the response to the output file.
        out.write(audio_content)
        print('Audio content written to file' + mp3_name)
    #
    # for textBlock in textBlocks:
    #     synthesis_input = texttospeech.SynthesisInput(ssml=textBlock)
    #     response.append = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    #
    #     # Save the audio stream returned by Amazon Polly on Lambda's temp
    #     # directory. If there are multiple text blocks, the audio stream
    #     # will be combined into a single file.
    #
    #     with open("output.mp3", "wb") as out:
    #         # Write the response to the output file.
    #         out.write(response.audio_content)
    #         print('Audio content written to file "output.mp3"')
    #
    # with closing(response.audio_content) as stream:
    #     output = os.path.join('tmp', outputfilename + '.mp3')
    #     with open(output, "ab") as file:
    #         out.write(stream)