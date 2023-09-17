import numpy as np
from flask import Flask, app, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
import chatbot
from speech import listen_to_speech, chatbot_response


# Create flask app
flask_app = Flask(__name__)
flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vastunting.db"
db = SQLAlchemy()
db.init_app(flask_app)

class log_activity(db.Model):
    __tablename__ = 'Log_History'
    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.String, nullable=False, default=datetime.datetime.now())
    aktivitas = db.Column(db.String, nullable=False)

@flask_app.route("/database/create", methods=["GET"])
def createDatabase():
    with flask_app.app_context():
        db.create_all()
        return "Database Created Successfully!"

@flask_app.route('/chatbot')
def halchatbot():
    return render_template('chatbot.html')

@flask_app.route('/listen_speech', methods=['POST'])
def listen_speech():
    spoken_text = listen_to_speech()  # Call your listen_to_speech function here
    if spoken_text:
        response = chatbot_response(spoken_text)  # Call your chatbot_response function here
        return jsonify({"user_message": spoken_text, "bot_response": response})
    else:
        return jsonify({"error": "No speech detected"})

@flask_app.route('/get')
def chat():
    userText = request.args.get('msg')
    tanggal = datetime.datetime.now()
    tanggal_baru = tanggal.strftime('%Y-%m-%d %H:%M:%S')
    data_log = log_activity(
        tanggal=tanggal_baru,
        aktivitas="User Bertanya ke Chatbot",
    )
    db.session.add(data_log)
    db.session.commit()
    return chatbot.chatbot_response(userText)

@flask_app.route("/log")
def logactivity():
    return render_template('log_activity.html', logaktiv=log_activity.query.all())

if __name__ == "__main__":
    flask_app.run(host="", debug=True)
