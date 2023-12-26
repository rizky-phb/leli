import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('popular')
from keras.models import load_model
chatbot_adi_model = load_model('chatbot_adi/model.h5')
import json
import random
chatbot_adi_intens = json.loads(open('chatbot_adi/content.json').read())
chatbot_adi_words = pickle.load(open('chatbot_adi/texts.pkl','rb'))
chatbot_adi_classes = pickle.load(open('chatbot_adi/labels.pkl','rb'))

def adi_clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def adi_bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = adi_clean_up_sentence(sentence)
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

def adi_predict_class(sentence, model):
    # filter out predictions below a threshold
    p = adi_bow(sentence, chatbot_adi_words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": chatbot_adi_classes[r[0]], "probability": str(r[1])})
    return return_list

def adi_getResponse(ints, intents_json):
    print(ints)
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def adi_chatbot_response(msg):
    ints = predict_class(msg, chatbot_adi_model)    
    res = adi_getResponse(ints, chatbot_adi_intens)
    print(res)
    return res



