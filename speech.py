import speech

import speech_recognition as sr
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model = load_model('model.h5')
import json
import random
intents = json.loads(open('Intents.json').read())
words = pickle.load(open('texts.pkl','rb'))
classes = pickle.load(open('labels.pkl','rb'))

def listen_to_speech(audio_path):
    recognizer = sr.Recognizer()
    # with sr.Microphone() as source:
    #     print("Mendengarkan...")
    #     audio = recognizer.listen(source)
    audiowav = sr.AudioFile(audio_path)
    # Initialize recognizer class                                       

    with audiowav as source:
        print("Mendengarkan...")
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="id-ID")
        return text
    except sr.UnknownValueError:
        print("Maaf, saya tidak bisa mengerti audio tersebut.")
        return ""
    except sr.RequestError as e:
        print(f"Tidak dapat menghubungi layanan Google Speech Recognition; {e}")
        return ""
def convert_text_to_Audio(audio_path):
    recognizer = sr.Recognizer()
    # with sr.Microphone() as source:
    #     print("Mendengarkan...")
    #     audio = recognizer.listen(source)
    audiowav = sr.AudioFile(audio_path)
    # Initialize recognizer class                                       

    with audiowav as source:
        print("Mendengarkan...")
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="id-ID")
        return text
    except sr.UnknownValueError:
        print("Maaf, saya tidak bisa mengerti audio tersebut.")
        return ""
    except sr.RequestError as e:
        print(f"Tidak dapat menghubungi layanan Google Speech Recognition; {e}")
        return ""
def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res

# def chatbot_response(input_text):
#     responses = {
#         "halo": "Halo!",
#         "bagaimana kabarmu": "Saya hanyalah program komputer, tapi saya di sini untuk membantu!",
#         "selamat tinggal": "Selamat tinggal! Semoga harimu menyenangkan!",
#     }
#     return responses.get(input_text.lower(), "Saya tidak mengerti itu.")

if __name__ == "__main__":
    while True:
        spoken_text = listen_to_speech()
        if spoken_text:
            response = chatbot_response(spoken_text)
            print(f"Anda berkata: {spoken_text}")
            print(f"Chatbot: {response}")