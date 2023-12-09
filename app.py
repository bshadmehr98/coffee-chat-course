from sanic import Sanic
from sanic.response import json

from sanic_motor import BaseModel

from models.chat import Chat, ChatModel, Message
from uuid import uuid4
import datetime as dt
from sanic_ext import Extend


app = Sanic("CoffeeChat")

# Serves files from the static folder to the URL /static
app.static('/static', './static')

app.config.CORS_ORIGINS = "*"
Extend(app)

settings = dict(
    MOTOR_URI='mongodb://coffeechat:coffeechat@127.0.0.1:27017/coffeechat?authSource=coffeechat',
)
app.config.update(settings)

BaseModel.init_app(app)
