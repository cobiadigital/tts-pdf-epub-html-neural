from google.cloud import texttospeech
import os
#from contextlib import closing
import bs4
import re

client = texttospeech.TextToSpeechClient.from_service_account_json(
    'text-to-speech.json')

voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, name="en-US-Wavenet-G"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.0,
)

def pollytext(filename):

    # with open(filename, 'r', encoding='utf-8') as file:

    with open(filename, 'r', encoding='utf-8') as file:
        response = file.read()

    soup = bs4.BeautifulSoup(response, "lxml")

    for tag in soup.find_all(True):
        tag.attrs = {}

    for script_tag in soup.find_all("script"):
        script_tag.decompose()

    for a_tag in soup.find_all("a"):
        a_tag.decompose()

    for header_tags in soup.find_all(["h1", "h2", "h3", "h4", "li"]):
        header_tags.name = "p"
        header_tags.insert_after("hr")

    for em_tag in soup.find_all(["em", "i", "strong"]):
        em_tag.name = "emphasis"
        em_tag['level'] = "moderate"

    for break_tag in soup.find_all(["hr"]):
        break_tag.name = "break"
        break_tag['time'] = "1s"

    for all_tags in soup.find_all():
        if len(all_tags.get_text(strip=True)) == 0:
            # Remove empty tag
            all_tags.extract()

    text = ""
    for accepted_tag in soup(["p", "break", "emphasis"]):
        text += str(accepted_tag)

    patterns = ["</?div>", "</?span>", "</?a>", "</?svg>", "</?path>", "</?button>"]
    for pattern in patterns:
        text = re.sub(r'{}'.format(pattern), "", text)

    output = re.sub(u'[\u201c\u201d]', '"', text)

    sep = '.'
    outputfilename = filename.split(sep, 1)[0]

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
    textBlocks.append("<speak>" + rest + "</speak>")
    with open("output.txt", "w") as text:
        # Write the response to the output file.
        text.write(str(textBlocks))
    return textBlocks

def synthesize_ssml(client, filename, **kwargs):
    textBlocks = pollytext(filename)
    return b"".join(
        client.synthesize_speech(input=texttospeech.SynthesisInput(ssml=textBlock), **kwargs).audio_content for textBlock in textBlocks)


filename = 'ch8.txt'
audio_content = synthesize_ssml(client, filename, voice=voice, audio_config=audio_config)

with open("output.mp3", "wb") as out:
    # Write the response to the output file.
    out.write(audio_content)
    print('Audio content written to file "output.mp3"')
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