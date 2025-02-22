## channel.py - a simple message channel
##

from flask import Flask, request, render_template, jsonify
import json
import requests
import datetime
from better_profanity import profanity
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from flask_cors import CORS
import random

# Initialize the sentiment analyzer
nltk.download('vader_lexicon')

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!' # change to something random, no matter what

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

HUB_URL = 'http://vm146.rz.uni-osnabrueck.de/hub'
HUB_AUTHKEY = 'Crr-K24d-2N'
CHANNEL_AUTHKEY = '0987654321'
CHANNEL_NAME = "Daily Gratitude"
CHANNEL_ENDPOINT = "http://localhost:5001" # don't forget to adjust in the bottom of the file

CHANNEL_FILE = 'messages.json'
CHANNEL_TYPE_OF_SERVICE = 'aiweb24:chat'

INITIAL_MESSAGE = {
    "content": "Welcome to Daily Gratitude! Share something positive today. 😊",
    "sender": "Daily Gratitude Team ✨",
    "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
    "extra": None
}


@app.cli.command('register')
def register_command():
    global CHANNEL_AUTHKEY, CHANNEL_NAME, CHANNEL_ENDPOINT

    # send a POST request to server /channels
    response = requests.post(HUB_URL + '/channels', headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
                             data=json.dumps({
                                "name": CHANNEL_NAME,
                                "endpoint": CHANNEL_ENDPOINT,
                                "authkey": CHANNEL_AUTHKEY,
                                "type_of_service": CHANNEL_TYPE_OF_SERVICE,
                             }))

    if response.status_code != 200:
        print("Error creating channel: "+str(response.status_code))
        print(response.text)
        return

def check_authorization(request):
    global CHANNEL_AUTHKEY
    # check if Authorization header is present
    if 'Authorization' not in request.headers:
        return False
    # check if authorization header is valid
    if request.headers['Authorization'] != 'authkey ' + CHANNEL_AUTHKEY:
        return False
    return True

@app.route('/health', methods=['GET'])
def health_check():
    global CHANNEL_NAME
    if not check_authorization(request):
        return "Invalid authorization", 400
    return jsonify({'name':CHANNEL_NAME}),  200

# GET: Return list of messages
@app.route('/', methods=['GET'])
def home_page():
    if not check_authorization(request):
        return "Invalid authorization", 400
    # fetch channels from server
    return jsonify(read_messages())

# POST: Send a message
@app.route('/', methods=['POST'])
def send_message():
    # fetch channels from server
    # check authorization header
    if not check_authorization(request):
        return "Invalid authorization", 400
    # check if message is present
    message = request.json

    if not message:
        return "No message", 400
    if not 'content' in message:
        return "No content", 400
    if not 'sender' in message:
        return "No sender", 400
    if not 'timestamp' in message:
        return "No timestamp", 400
    if not 'extra' in message:
        extra = None
    else:
        extra = message['extra']
    # add message to messages
    messages = read_messages()

    # returns the filtered message and whether it is censored
    censored_message = filter_message(message)
    messages.append(censored_message[0])
    # adds an answer to the message 
    messages.append({
    "content": generate_answer(censored_message[0],censored_message[1]), # based on the input sentiment
    "sender":" Daily Gratitude Team ✨",
    "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
    "extra": "affirmation"
    }) 

    save_messages(messages)
    return "OK", 200

    
def read_messages():
    global CHANNEL_FILE
    try:
        f = open(CHANNEL_FILE, 'r')
    except FileNotFoundError:
        return [INITIAL_MESSAGE]
    try:
        messages = json.load(f)
    except json.decoder.JSONDecodeError:
        messages = []

    f.close()
    messages = remove_old_messages(messages)

    # Ensure initial message is always first
    if not messages or messages[0]['content'] != INITIAL_MESSAGE['content']:
        messages.insert(0, INITIAL_MESSAGE)

    return messages

def filter_message(message):
    censored = False
    
    if profanity.contains_profanity(message['content']):
        message['content'] = profanity.censor(message['content'])
        censored = True
    if profanity.contains_profanity(message['sender']):
        message['sender'] = profanity.censor(message['sender'])
        censored = True
    # adds a keyword to the extra field to generate an affirmation on the client end
    message['extra'] = "affirmation"

    return message, censored
            
def sentiment_analysis(message):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(message['content'])
    return sentiment

def generate_answer(message, censored=False):
    # sentiment analysis
    sentiment = sentiment_analysis(message)

    positive = [
        "That sounds amazing! Thanks for sharing! 😊",
        "I'm so happy to hear that! Keep the good vibes going! 🎉",
        "Wow, that's wonderful! What else made your day great? 🌟",
        "That's truly inspiring! Keep embracing the positivity! 💛",
        "Your joy is contagious! Tell me more! 😃"
    ]

    negative = [
        "Try to focus on the positive! If you need help, try the affirmation button. 💡",
        "Remember, every day brings something good. Keep looking for it! 🌈",
        "I'm here to lift you up! What's one thing that made you smile today? 😊",
        "It's okay to have tough days, but don't forget how strong you are! 💪",
        "Sending you a virtual hug! 💖 Want to hear an affirmation?"
    ]

    neutral = [
        "Thanks for sharing! What else makes you feel good today? ☀️",
        "That's interesting! Would you like to dive deeper into that? 🤔",
        "Sounds like a balanced day! Any highlights you'd like to share? 🎭",
        "Sometimes neutral is just fine! What's something small that made you happy? 🍀",
        "I'd love to hear more! What's something you're grateful for today? 🙏"
    ]

    censor = [
        "Please stick to joyful language! 🌟",
        "Kindness is key! Let's focus on happy words! ✨",
        "This space is all about joy and gratitude! Try rewording that! 🌼",
        "Let's keep our word choice uplifting! 🌟",
        "Remember, words shape our emotions! Let's use them wisely! 💬"
    ]

    # profanity check
    if censored==True:
        return random.choice(censor)
    
    else:
        if sentiment['compound'] <= -0.05:
                return random.choice(negative)
            # if positive sentiment
        if sentiment['compound'] >= 0.05:
                return random.choice(positive)
            # if neutral sentiment
        if -0.05 < sentiment['compound'] < 0.05:
                return random.choice(neutral)
    
# removes any messages older than 1 day 
def remove_old_messages(messages):
    current_time = datetime.datetime.now()
    one_day_ago = current_time - datetime.timedelta(days=1)

    return [msg for msg in messages if datetime.datetime.strptime(msg['timestamp'][:-1], '%Y-%m-%dT%H:%M:%S.%f') >= one_day_ago]


def save_messages(messages):
    global CHANNEL_FILE
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(messages, f)


# Start development web server
# run flask --app channel.py register
# to register channel with hub

if __name__ == '__main__':
    app.run(port=5001, debug=True)
