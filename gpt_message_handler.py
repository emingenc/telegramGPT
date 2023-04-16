
import os
from dotenv import load_dotenv
from datetime import datetime
import sqlalchemy as db
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

engine = db.create_engine("sqlite:///db.sqlite3")
connection = engine.connect()
metadata = db.MetaData()


try:
    conversations = db.Table('conversations', metadata,
                             autoload=True, autoload_with=engine)
except:
    conversations = db.Table('conversations',
                             metadata,
                             db.Column('id', db.Integer, primary_key=True),
                             db.Column('user_id', db.Integer),
                             db.Column('user_name', db.String),
                             db.Column('user_message', db.String),
                             db.Column('message_id', db.Integer),
                             db.Column('bot_response', db.String),
                             db.Column('created_at', db.DateTime, default=datetime.now))

    metadata.create_all(engine)


# Function to send a message to the OpenAI chatbot model and return its response
def send_message(message_log):
    # Use OpenAI's ChatCompletion API to get the chatbot's response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # The name of the OpenAI chatbot model to use
        # The conversation history up to this point, as a list of dictionaries
        messages=message_log,
        # The maximum number of tokens (words or subwords) in the generated response
        max_tokens=3800,
        # The stopping sequence for the generated response, if any (not used here)
        stop=None,
        # The "creativity" of the generated response (higher temperature = more creative)
        temperature=0.7,
    )

    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response.choices[0].message.content


def handle_response(text, user, message_id) -> str:
    # If this is the first request, get the user's input and add it to the conversation history
    # if you want it to run gpt over last x messages, 
    # you can replace the get_message_log_static() with get_message_log(user.id)
    # message_log = get_message_log(user.id)[-x:]
    message_log = get_message_log_static()
    user_input = text
    message_log.append({"role": "user", "content": user_input})
    # Send the conversation history to the chatbot and get its response
    print(message_log, len(str(message_log)))
    response = send_message(message_log)
    message_log.append({"role": "assistant", "content": response})
    first_request = False
    save_to_db(user_input, response, user, message_id)
    return response


def save_to_db(user_input, bot_response, user, message_id):
    now = datetime.now()
    query = db.insert(conversations).values(user_id=user.id, user_name=user.username, user_message=user_input,
                                            message_id=message_id, bot_response=bot_response, created_at=now)
    ResultProxy = connection.execute(query)
    print(ResultProxy.inserted_primary_key)


def get_message_log(user_id):
    message_log = [
        {"role": "system", "content": "Your name is telegramGPT. You are an expert in every field. You are trying your best to help your emin. ask the users name"}
    ]
    query = db.select([conversations]).where(
        conversations.columns.user_id == user_id)
    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchall()
    for row in ResultSet:
        message_log.append({"role": "user", "content": row[3]})
        message_log.append({"role": "assistant", "content": row[5]})
    return message_log


def get_message_log_static():
    message_log = [
        {"role": "system", "content": "Your name is telegramGPT. You are an expert in every field. You are trying your best to help."}
    ]
    return message_log
