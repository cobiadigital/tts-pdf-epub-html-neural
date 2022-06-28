from tika import parser
import bs4
import re
from google.cloud import texttospeech
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
    text = re.sub('-\n', '', text)
    text = re.sub('\n', ' ', text)
    # Get rid of p tags at end of page
    text = re.sub(r'<p>[0-9].*?p>', '', text)
    text = re.sub(r'(?<!\. )</p>.*?<p>', '', text)
    #text = re.sub(r'(?)\.<p>[0-9].*?p>', '', text)
    #remove http addresses
    text = re.sub(r'https.*? ', '', text)
    text = re.sub(r'\.[0-9]', '.', text)

#     remove page numbers
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
        textBlocks.append("<speak>" + textBlock + "</speak>")
    textBlocks.append("<speak>" + rest + '<break time="3s"/></speak>')
    with open("output.txt", "w") as text:
        # Write the response to the output file.
        text.write(str(textBlocks))
    return textBlocks

client = texttospeech.TextToSpeechClient.from_service_account_json(
    '.secret/text-to-speech.json')

voice = texttospeech.VoiceSelectionParams(
    language_code="en-GB", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, name="en-US-Wavenet-E"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.0,
)
# def epub_contents(filename):
#     book = epub.read_epub(filename)
#     items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
#     return filename, chapter_names

def synthesize_ssml(client, response, **kwargs):
    textBlocks = pollytext(response)
    print(textBlocks) #fortest
    return b"".join(
        client.synthesize_speech(input=texttospeech.SynthesisInput(ssml=textBlock), **kwargs).audio_content for textBlock in textBlocks)
    print(textBlocks) #fortest

filename = 'subjects-of-technology-adhd.pdf'
split_tup = os.path.splitext(filename)
file_name = split_tup[0]
file_extension = split_tup[1]
filename = "Data/" + filename
audio_content = synthesize_ssml(client, filename, voice=voice, audio_config=audio_config)
mp3_name = file_name + "_.mp3"
with open(mp3_name, "wb") as out:
# Write the response to the output file.
    out.write(audio_content)
    print('Audio content written to file' + mp3_name)

# safe_text = raw.encode('utf-8', errors='ignore')
#
# safe_text = str(safe_text).replace("\n", "").replace("\\", "")
# print('--- safe text ---' )
# print( safe_text )


#java -Djava.awt.headless=true -jar /usr/local/Cellar/tika/1.5/libexec/tika-app-1.5.jar foo.pdf
