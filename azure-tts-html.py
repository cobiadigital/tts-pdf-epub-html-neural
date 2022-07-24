import azure.cognitiveservices.speech as speechsdk
import json
import bs4
import re
import os

def pollytext(response, voice):

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
    textBlocks = []

    while (len(rest) > 5000):
        begin = 0
        end = rest.rfind("</p>", 0, 5000) #rfind looks for the last case of the search term.
        if (end == -1):
            end = rest.rfind(". ", 0, 5000)
            textBlock = rest[begin:end+1]
            rest = rest[end+1:]
            textBlocks.append('''<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">
                     <voice name="'''+ voice + '''">
                         <prosody rate="0%" pitch="0%">''' + textBlock + "</p></prosody></voice></speak>")
            rest = "<p>" + rest

        else:
            textBlock = rest[begin:end+4]
            rest = rest[end+4:] #Remove the annoying "Dot" that otherwise starts each new block since you no longer start on that index.
            textBlocks.append('''<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">
                     <voice name="'''+ voice + '''">
                         <prosody rate="0%" pitch="0%">''' + textBlock + "</prosody></voice></speak>")
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

def synthesize_ssml(speech_config, response, voice):
    textBlocks = pollytext(response, voice)
    audio_data_list = []
    for textBlock in textBlocks:
        result = speech_synthesizer.speak_ssml_async(textBlock).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(textBlock)
            print("Speech synthesized for text")
            audio_data_list.append(result.audio_data)
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                 if cancellation_details.error_details:
                       print("Error details: {}".format(cancellation_details.error_details))
                       print("Did you set the speech resource key and region values?")
            break
    return b"".join(audio_data_list)

filename = 'ssml_text.html'
voice = 'en-US-JaneNeural'
split_tup = os.path.splitext(filename)
file_name = split_tup[0]
file_extension = split_tup[1]
filename = "Data/" + filename
openfile = open(filename, "r")
response = openfile.read()
audio_content = synthesize_ssml(speech_config, response, voice)
mp3_name = "output/" + file_name + "_.mp3"
with open(mp3_name, "wb") as out:
# Write the response to the output file.
    out.write(audio_content)
    print('Audio content written to file' + mp3_name)

