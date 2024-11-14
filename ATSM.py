import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from google.cloud import storage
from PyAudio import RecAUD
from google.cloud import speech_v1p1beta1 as speech

numberOfSpeakers = int(input("Please enter number of speakers (up to 6 people may participate): "))
chosenSpeaker = int(input("Please enter the # of the speaker to be analyzed: "))

guiAUD = RecAUD()

#Line below authenticates just as well as "os.environ" - however we are still stuck even after auth
#storage_client = storage.Client.from_service_account_json('Project ATWM-a83e05b28663.json')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/davidkarimi/PycharmProjects/ATSM/Project ATWM-a83e05b28663.json"

def create_bucket(bucket_name):
    """Creates a new bucket."""
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name)
    print('Bucket {} created'.format(bucket.name))  ## have program automatically name new buckets in unique ways to prevent naming conflicts


name = "gcspeechstorage0"
string = name[0:15]
counter = int(name[15:])

while True:
    try:

        gcspeechstorage = string + str(counter)
        create_bucket(gcspeechstorage)
        break

    except:

        counter = counter + 1


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


upload_blob(gcspeechstorage, "/Users/davidkarimi/PycharmProjects/ATSM/output.wav", "output.wav")

gcs_uri = "gs://gcspeechstorage{}/output.wav".format(counter)

# [START speech_transcribe_async_gcs]
def transcribe_gcs(gcs_uri):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    #from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    from google.cloud.speech_v1p1beta1 import enums
    from google.cloud.speech_v1p1beta1 import types

    if os.path.exists('speechToAnalyze.txt'):
        os.remove('speechToAnalyze.txt')

    speech_file = "/Users/davidkarimi/PycharmProjects/ATSM/output.wav"

    with open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = speech.types.RecognitionAudio(uri=gcs_uri)

    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code='en-US',
        enable_speaker_diarization=True,
        diarization_speaker_count=numberOfSpeakers,)

    client = speech.SpeechClient()

    print('Waiting for operation to complete...')

    response = client.recognize(config, audio)

    result = response.results[-1]

    words_info = result.alternatives[0].words

    speakerOneSentence = ""
    speakerTwoSentence = ""
    speakerThreeSentence = ""
    speakerFourSentence = ""
    speakerFiveSentence = ""
    speakerSixSentence = ""

    for word_info in words_info:
        if word_info.speaker_tag == 1:
            speakerOneSentence = speakerOneSentence + " " + word_info.word
        elif word_info.speaker_tag == 2:
            speakerTwoSentence = speakerTwoSentence + " " + word_info.word
        elif word_info.speaker_tag == 3:
            speakerThreeSentence = speakerThreeSentence + " " + word_info.word
        elif word_info.speaker_tag == 4:
            speakerFourSentence = speakerFourSentence + " " + word_info.word
        elif word_info.speaker_tag == 5:
            speakerFiveSentence = speakerFiveSentence + " " + word_info.word
        elif word_info.speaker_tag == 6:
            speakerSixSentence = speakerSixSentence + " " + word_info.word



    tag = 1
    speaker = ""

    for word_info in words_info:
        if word_info.speaker_tag == tag:
            speaker = speaker + " " + word_info.word

        else:
            print("speaker {}: {}".format(tag, speaker))
            tag = word_info.speaker_tag
            speaker = "" + word_info.word

    if numberOfSpeakers == 2:
        print(u"Speaker 1: {}".format(speakerOneSentence))
        print(u"Speaker 2: {}".format(speakerTwoSentence))
    elif numberOfSpeakers == 3:
        print(u"Speaker 1: {}".format(speakerOneSentence))
        print(u"Speaker 2: {}".format(speakerTwoSentence))
        print(u"Speaker 3: {}".format(speakerThreeSentence))
    elif numberOfSpeakers == 4:
        print(u"Speaker 1: {}".format(speakerOneSentence))
        print(u"Speaker 2: {}".format(speakerTwoSentence))
        print(u"Speaker 3: {}".format(speakerThreeSentence))
        print(u"Speaker 4: {}".format(speakerFourSentence))
    elif numberOfSpeakers == 5:
        print(u"Speaker 1: {}".format(speakerOneSentence))
        print(u"Speaker 2: {}".format(speakerTwoSentence))
        print(u"Speaker 3: {}".format(speakerThreeSentence))
        print(u"Speaker 4: {}".format(speakerFourSentence))
        print(u"Speaker 5: {}".format(speakerFiveSentence))
    elif numberOfSpeakers == 6:
        print(u"Speaker 1: {}".format(speakerOneSentence))
        print(u"Speaker 2: {}".format(speakerTwoSentence))
        print(u"Speaker 3: {}".format(speakerThreeSentence))
        print(u"Speaker 4: {}".format(speakerFourSentence))
        print(u"Speaker 5: {}".format(speakerFiveSentence))
        print(u"Speaker 6: {}".format(speakerSixSentence))

    speakerCounter = 1

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        transcribedSpeechFile = open('speechToAnalyze.txt', 'a+')  # this is where a text file is made with the transcribed speech

        transcribedSpeechFile.write(format(result.alternatives[0].transcript))

        transcribedSpeechFile.close()

        confidencePercentage = result.alternatives[0].confidence
        confidencePercentage = confidencePercentage * 100

        print("Confidence level of speaker {}'s transcription: {}%".format(speakerCounter, round(confidencePercentage, 2)))
        speakerCounter = speakerCounter + 1
# [END speech_transcribe_async_gcs]

if __name__ == '__main__':
    transcribe_gcs(gcs_uri)


audio_rec = open('speechToAnalyze.txt', 'r')

sid = SentimentIntensityAnalyzer()
for sentence in audio_rec:
    ss = sid.polarity_scores(sentence)
    for k in ss:
        print('{0}: {1}, '.format(k, ss[k]), end='')
    print()