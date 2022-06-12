from google.cloud import texttospeech
import os
import json
import re
import bs4

def parse_json(response):
#Open Json file
    #load sub key
    json_list = response["E"]["L"][0]["D"]
    #creat empty list
    text_content = ""
    #Run through json_list for contents of everything in J key
    for text_item in json_list:
        if text_item['B'] == "p":
            text_content = text_content + "<p>" + text_item["J"] + "</p>"
    text_content


    soup = bs4.BeautifulSoup(text_content, "lxml")
    for a_tag in soup.find_all("a"):
        a_tag.decompose()

    text = ""
    for accepted_tag in soup(["p", "break"]):
        text += str(accepted_tag)
    text = text.replace('\xad', '')
    text = re.sub(u'\xa0', u' ', text)
    output = text
    print(len(output))
    sep = '.'
    rest = output
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

    with open("ginjesus.txt", "w") as text:
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

def synthesize_ssml(client, response, **kwargs):
    textBlocks = parse_json(response)
    print(textBlocks) #fortest
    return b"".join(
        client.synthesize_speech(input=texttospeech.SynthesisInput(ssml=textBlock), **kwargs).audio_content for textBlock in textBlocks)
    print(textBlocks) #fortest

filename = 'ginjesus.json'
sec_type = 'approved'
split_tup = os.path.splitext(filename)
file_name = split_tup[0]
file_extension = split_tup[1]
with open(filename, 'r') as file:
    response = json.load(file)
    audio_content = synthesize_ssml(client, response, voice=voice, audio_config=audio_config)
    mp3_name = file_name + "_.mp3"
    with open(mp3_name, "wb") as out:
    # Write the response to the output file.
        out.write(audio_content)
        print('Audio content written to file' + mp3_name)