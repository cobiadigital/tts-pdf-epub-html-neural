import azure.cognitiveservices.speech as speechsdk
import json
import os


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
    opn
    audio_data_list = []
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

    return result.audio_data

filename = 'ssml_text.pdf'
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

