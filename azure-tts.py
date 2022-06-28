import azure.cognitiveservices.speech as speechsdk
import json
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

    #remove references
    end = rest.rfind('References')
    rest = rest[0:end]
    #Because single invocation of the polly synthesize_speech api can
    # transform text with about 1,500 characters, we are dividing the
    # post into blocks of approximately 1,000 characters.
    textBlocks = []
    while (len(rest) > 5000):
        begin = 0
        end = rest.rfind("</p>", 0, 5000) #rfind looks for the last case of the search term.

        if (end == -1):
            end = rest.rfind(". ", 0, 5000)
            textBlock = rest[begin:end+1]
            rest = rest[end+1:]
            textBlocks.append('''<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">
                     <voice name="en-GB-OliviaNeural">
                         <prosody rate="0%" pitch="0%">''' + textBlock + "</p></prosody></voice></speak>")
        else:
            textBlock = rest[begin:end+4]
            rest = rest[end+4:] #Remove the annoying "Dot" that otherwise starts each new block since you no longer start on that index.
            textBlocks.append('''<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">
                     <voice name="en-GB-OliviaNeural">
                         <prosody rate="0%" pitch="0%">''' + textBlock + "</prosody></voice></speak>")
            rest = "<p>" + rest
    textBlocks.append("<speak>" + rest + '<break time="3s"/></speak>')
    with open("output.txt", "w") as text:
        # Write the response to the output file.
        text.write(str(textBlocks))
    return textBlocks

def get_keys(path):
    with open(path) as f:
        return json.load(f)
keys = get_keys(".secret/azure.json")
subscription_key = keys['subscription']
service_region = keys['region']
speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)# The language of the voice that speaks.

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Get text from the console and synthesize to the default speaker.


def synthesize_ssml(speech_config, response):
    textBlocks = pollytext(response)
    audio_data_list = []
    for textBlock in textBlocks:
        result = speech_synthesizer.speak_ssml_async(textBlock).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(textBlock)
            print("Speech synthesized for text")
            audio_data_list.append(result.audio_data)
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                 if cancellation_details.error_details:
                       print("Error details: {}".format(cancellation_details.error_details))
                       print("Did you set the speech resource key and region values?")
            break
    return b"".join(audio_data_list)

filename = 'subjects-of-technology-adhd.pdf'
split_tup = os.path.splitext(filename)
file_name = split_tup[0]
file_extension = split_tup[1]
filename = "Data/" + filename
audio_content = synthesize_ssml(speech_config, filename)
mp3_name = file_name + "_.mp3"
with open(mp3_name, "wb") as out:
# Write the response to the output file.
    out.write(audio_content)
    print('Audio content written to file' + mp3_name)

