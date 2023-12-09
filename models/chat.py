from sanic_motor import BaseModel
import dataclasses
import datetime as dt
from models.base import BaseDataClass
from typing import List
from typing import Optional


class ChatModel(BaseModel):
    __coll__ = 'chats'
    __unique_fields__ = ['session_token']
    # __unique_fields__ = ['name, age']   # name and age for unique


@dataclasses.dataclass
class Message(BaseDataClass):
    text: str
    ts: dt.datetime
    from_user: Optional[bool] = False
    
    @staticmethod
    def to_object(mongo_obj):
        return Message(
            text=mongo_obj.text,
            ts=mongo_obj.ts,
            from_user=mongo_obj.from_user
        )


@dataclasses.dataclass
class Chat(BaseDataClass):
    session_token: str
    created_at: Optional[dt.datetime] = None
    messages: Optional[List[Message]] = None

    MODEL = ChatModel
    
    async def add_message(self, message):
        await ChatModel.update_one({"session_token": self.session_token}, {'$push': {'messages': message.to_dict()}})
        
    @classmethod
    async def get_by_session(cls, session_token):
        res = await ChatModel.find_one({"session_token": session_token})
        return Chat.to_object(res)
    
    @staticmethod
    def to_object(mongo_obj):
        return Chat(
            session_token=mongo_obj.session_token,
            created_at=mongo_obj.created_at,
            messages=[Message(**m) for m in mongo_obj.messages]
        )
