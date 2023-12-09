from sanic import Request, Websocket
import sanic
from models.chat import Chat, Message
from uuid import uuid4
import datetime as dt
from sanic.response import json as json_response
import json
import asyncio

def datetime_serializer(obj):
    if isinstance(obj, dt.datetime):
        return obj.isoformat()

app = sanic.Sanic.get_app("CoffeeChat")

chats = {}

async def notify_server_started_after_five_seconds():
    await asyncio.sleep(5)
    # print('Unsetting experts...')
    # app.add_task(notify_server_started_after_five_seconds())

app.add_task(notify_server_started_after_five_seconds())

@app.websocket("/chat/<token>")
async def user_chat(request: Request, ws: Websocket, token):
    if token not in chats:
        chats[token] = {"clients": [], "expert": None}
    chats[token]["clients"].append(ws)
    chat = await Chat.get_by_session(token)
    while True:
        message = await ws.recv()
        print(f"Found {len(chats[token]['clients'])} clients")
        for client in chats[token]["clients"]:
            if client != ws:
                data = {
                    "message": message,
                    "from_user": True
                }
                try:
                    await client.send(json.dumps(data))
                except sanic.exceptions.WebsocketClosed as e:
                    print("Removing closed connection")
                    chats[token]["clients"].remove(client)
        if chats[token]["expert"] is not None:
            try:
                await chats[token]["expert"].send(message)
            except sanic.exceptions.WebsocketClosed as e:
                chats[token]["expert"] = None
        await chat.add_message(Message(ts=dt.datetime.now(), from_user=True, text=message))


@app.route("/chat/get")
async def get_chat(request):
    token = request.args["token"][0] if "token" in request.args else None
    if token is None:
        token = str(uuid4())
        chat = Chat(session_token=token, created_at=dt.datetime.now(), messages=[])
        await chat.insert_one()
        return json_response({"token": token, "messages": []})
    else:
        chat = await Chat.get_by_session(token)
        return json_response({"token": token, "messages": json.loads(json.dumps(chat.to_dict()["messages"], default=datetime_serializer))})
    
    
@app.route("admin/chat/list")
@app.ext.template("admin_chat.html")
async def admin_list_chats(request):
    final_list = []
    for token in chats:
        final_list.append({
            "token": token,
            "expert_assigned": False if chats[token]["expert"] is None else True
        })
    return {"chats": final_list}


@app.route("admin/chat/<token>")
@app.ext.template("admin_chat.html")
async def admin_get_chats(request, token):
    final_list = []
    for token in chats:
        final_list.append({
            "token": token,
            "expert_assigned": False if chats[token]["expert"] is None else True
        })
    chat = await Chat.get_by_session(token)
    messages = chat.to_dict()["messages"]
    return {"chats": final_list, "messages": messages, "token": token}


@app.websocket("admin/chat/start/<token>")
async def admin_start_chat(request: Request, ws: Websocket, token):
    if token not in chats:
        chats[token] = {"clients": [], "expert": ws}
    chats[token]["expert"] = ws
    chat = await Chat.get_by_session(token)
    while True:
        message = await ws.recv()
        await chat.add_message(Message(ts=dt.datetime.now(), from_user=False, text=message))
        for client in chats[token]["clients"]:
            if client != ws:
                data = {
                    "message": message,
                    "from_user": False
                }
                try:
                    await client.send(json.dumps(data))
                except sanic.exceptions.WebsocketClosed as e:
                    print("Removing closed connection")
                    chats[token]["clients"].remove(client)
