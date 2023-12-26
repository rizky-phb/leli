import numpy as np
import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
import base64,json,random,pickle
import chatbot
import chatbot_adi
from speech import listen_to_speech, chatbot_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model


# Create flask app
flask_app = Flask(__name__)
flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vastunting.db"
db = SQLAlchemy()
db.init_app(flask_app)
flask_app.config['FOLDER_AUDIO_INPUT'] = "./static/recorder2/input/"
flask_app.config['FOLDER_AUDIO_OUTPUT'] = "./static/recorder2/output/"
ALLOWED_EXTENSIONS = set(['mp3', 'wav', 'mp4'])
def allowed_file(filename):     
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
class log_activity(db.Model):
    __tablename__ = 'Log_History'
    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.String, nullable=False, default=datetime.datetime.now())
    aktivitas = db.Column(db.String, nullable=False)

@flask_app.route('/')
def index():
    return jsonify({"api": "hello world"})

@flask_app.route("/database/create", methods=["GET"])
def createDatabase():
    with flask_app.app_context():
        db.create_all()
        return "Database Created Successfully!"

@flask_app.route('/chatbot')
def halchatbot():
    return render_template('chatbot.html')

@flask_app.route('/coba_input')
def record():
    return render_template('record.html')
@flask_app.route('/listen_audio', methods=['POST'])
def listen_audio():
    if 'audio_data' not in request.files:
        return jsonify({"msg":"tidak ada form audio_data","bot_response":""})
    file = request.files['audio_data']
    print(file.filename)
    if file.filename == '':
        return jsonify({"msg":"tidak ada file audio_data yang dipilih","bot_response":""})
    if file and allowed_file(file.filename):
        #filename = secure_filename(file.filename)
        filename = "temp.wav"
        save_path = os.path.join(flask_app.config['FOLDER_AUDIO_INPUT'] , filename)
        file.save(save_path)
        spoken_text = listen_to_speech(save_path)  # Call your listen_to_speech function here
        print(spoken_text)
        if spoken_text:
            response = chatbot_response(spoken_text)  # Call your chatbot_response function here
            print(response)
            return jsonify({"user_message": spoken_text, "bot_response": response})
        else:
            print("no spech")
            return jsonify({"bot_response":"maaf ulangi kembali voice note anda atau ketik saja biar lebih mudah kami proses"})
    else:
        return jsonify({"msg":"format file salah","bot_response":""})

@flask_app.route('/listen_base64', methods=['POST'])
def listen_base64():
    encode_string = request.form["audio"]
    wav_file = open("temp.wav", "wb")
    decode_string = base64.b64decode(encode_string)
    wav_file.write(decode_string)                
               

@flask_app.route('/listen_speech', methods=['POST'])
def listen_speech():
    encode_string = base64.b64encode(open("audio.wav", "rb").read())
    wav_file = open("temp.wav", "wb")
    decode_string = base64.b64decode(encode_string)
    wav_file.write(decode_string)
    spoken_text = listen_to_speech()  # Call your listen_to_speech function here
    print(spoken_text)
    if spoken_text:
        response = chatbot_response(spoken_text)  # Call your chatbot_response function here
        print(response)
        return jsonify({"user_message": spoken_text, "bot_response": response})
    else:
        print("no spech")
        return jsonify({"bot_response": "No speech detected"})

@flask_app.route('/get')
def chat():

    model = load_model('model.h5',compile=False)
    intents = json.loads(open('Intents.json').read())
    words = pickle.load(open('texts.pkl','rb'))
    classes = pickle.load(open('labels.pkl','rb'))


    userText = request.args.get('msg')
    tanggal = datetime.datetime.now()
    tanggal_baru = tanggal.strftime('%Y-%m-%d %H:%M:%S')
    data_log = log_activity(
        tanggal=tanggal_baru,
        aktivitas="User Bertanya ke Chatbot",
    )
    print(data_log)
    db.session.add(data_log)
    db.session.commit()
    respon = chatbot.chatbot_response(userText,model,words,classes,intents)
    print(respon)
    return respon

@flask_app.route("/log")
def logactivity():
    return render_template('log_activity.html', logaktiv=log_activity.query.all())
@flask_app.route('/chatbot_adi/get')
def chatbot_adi():

  model = load_model('chatbot_adi/model.h5',compile=False)
  intents = json.loads(open('chatbot_adi/content.json').read())
  words = pickle.load(open('chatbot_adi/texts.pkl','rb'))
  classes = pickle.load(open('chatbot_adi/labels.pkl','rb'))

  userText = request.args.get('msg')
  tanggal = datetime.datetime.now()
  tanggal_baru = tanggal.strftime('%Y-%m-%d %H:%M:%S')
  data_log = log_activity(
      tanggal=tanggal_baru,
      aktivitas="User Bertanya "+userText+" ke Chatbot Adi",
  )
  print(data_log)
  db.session.add(data_log)
  db.session.commit()

  respon = [chatbot.chatbot_response(userText,model,words,classes,intents)]
  print(respon)
  return respon
CORS(flask_app)

#ssl_context='adhoc',
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", debug=True)
