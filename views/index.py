from sanic import Sanic
from sanic.response import json

from sanic_motor import BaseModel

from models.chat import Chat, ChatModel, Message
from uuid import uuid4
import datetime as dt


app = Sanic.get_app("CoffeeChat")


@app.route("/")
async def home(request):
    messages = [Message("salam", dt.datetime.now()), Message("Hi", dt.datetime.now())]
    chat = Chat(session_token="35adf507-7ebf-448d-8238-fe9718f803b3")
    await chat.add_message(Message("hello", dt.datetime.now()))
    return json({"status": "ok"})