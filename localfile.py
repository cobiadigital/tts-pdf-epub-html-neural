import requests
import re
import bs4
from urllib.request import Request, urlopen
from google.cloud import texttospeech

from copy import copy
# url = Request('https://www.theverge.com/2021/1/21/22241066/spotify-anchor-sponsorships-ad-money-spend-podcasting', headers={'User-Agent': 'Mozilla/5.0'})
# response = urlopen(url).read()
response = open('derrida.txt','r', encoding='cp1252')
soup = bs4.BeautifulSoup(response, "lxml")

for tag in soup.find_all(True):
        tag.attrs = {}

header_tags = soup.find_all(["h1","h2","h3","h4","li"])

#hr_tag = soup.new_tag("hr", time="1s")

for header_tag in header_tags:
    header_tag.name = "p"
    header_tag.insert_after(soup.new_tag("hr"))

hr_tags = soup("hr")
for hr_tag in hr_tags:
    hr_tag.name = "break"
    hr_tag['time'] = '1s'

emphasis = soup(["em","i"])
for emph in emphasis:
    emph.name = "emphasis"
    emph['level'] = "moderate"


soup_exs = (soup(["p","break"]))
text = ""
for soup_ex in soup_exs:
    text += str(soup_ex)
f = open("output.txt", "a", encoding="utf-8")
f.write(text)
f.close()

client = texttospeech.TextToSpeechClient.from_service_account_json(
            'text-to-speech.json')
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, name="en-US-Wavenet-C"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.0,
)

def sentences_splitter(text, chunk=4980):
    text = re.sub(r'(</p>)', r'\1', text)
    result = []
    while text:
        if len(text) <= chunk:
            result.append("<speach>" + text + "</speach>")
            break
        found = False
        split_index=chunk
        while split_index > 0:
            if re.match(r'(</p>)', text[split_index - 1:]):
                found = True
                break
            split_index -= 1
        if not found:
            split_index = chunk
            while split_index > 0:
                if re.match(r'^(</p>)', text[split_index - 1:]):
                    found = True
                    break
                split_index -= 1
        split_index +=4
        if split_index == 0:
            split_index = chunk
        rest = text[split_index:]
        rest = re.sub(r'^(</p>)', '\1', rest)
        result.append("<speach>" + text[:split_index] + "</speach>")
        text = rest
    return result

def run_text(text, **kwargs):
    chunks = sentences_splitter(text)
    return "".join( chunk for chunk in chunks)

ssml_script = run_text(text)

def synthesize_ssml(text, **kwargs):
    chunks = sentences_splitter(text)
    return "".join(
        chunk for chunk in chunks)

audio_script = synthesize_ssml(text)

print(audio_script)
def synthesize_ssml(client, text, **kwargs):
    chunks = sentences_splitter(text)
    return b"".join(
        client.synthesize_speech(input=texttospeech.SynthesisInput(ssml=chunk), **kwargs).audio_content for chunk in chunks)

audio_content = synthesize_ssml(client, text, voice=voice, audio_config=audio_config)
with open("output.mp3", "wb") as out:
    out.write(audio_content)
    print('Audio content has been written')

