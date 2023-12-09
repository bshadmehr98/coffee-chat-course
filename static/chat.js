// injectButton.js
var html_content = `
<div id="chat-container">
<div class="chat-box">
    <div class="chat-header">Chat Box</div>
    <div class="chat-body" id="chat-body">
        <!-- Add more messages as needed -->
    </div>
    <input type="text" class="chat-input" id="chat-input" placeholder="Type your message...">
    <button class="send-button" id="send-button">Send</button>
</div>
</div>

<button id="open-chat-btn">Chat</button>

<style>
body {
    margin: 0;
    font-family: Arial, sans-serif;
}

#open-chat-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 10px;
    background-color: #4CAF50;
    color: #fff;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

#chat-container {
    display: none;
    position: fixed;
    bottom: 80px;
    right: 20px;
    width: 300px;
    overflow: hidden;
}

body {
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #ecf0f1;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

.chat-box {
    width: 100%;
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.chat-header {
    background-color: #3498db;
    color: white;
    padding: 15px;
    text-align: center;
    font-weight: bold;
    border-radius: 10px 10px 0 0;
}

.chat-body {
    padding: 15px;
    height: 250px;
    overflow-y: scroll;
}

.message {
    margin-bottom: 15px;
}

.user-message {
    background-color: #3498db;
    color: white;
    padding: 10px;
    border-radius: 5px;
    display: block;
    max-width: 70%;
    word-wrap: break-word;
}

.other-message {
    background-color: #ecf0f1;
    padding: 10px;
    border-radius: 5px;
    display: block;
    max-width: 70%;
    word-wrap: break-word;
}

.chat-input {
    width: calc(100% - 30px);
    padding: 10px;
    border: none;
    border-top: 2px solid #3498db;
    outline: none;
    font-size: 14px;
    border-radius: 0;
}

.send-button {
    width: 100%;
    padding: 15px;
    background-color: #3498db;
    color: white;
    border: none;
    cursor: pointer;
    border-top: 2px solid #3498db;
    border-radius: 0 0 10px 10px;
    transition: background-color 0.3s;
}

.send-button:hover {
    background-color: #2980b9;
}

</style>
`
function getChat() {
    const chatToken = localStorage.getItem('chat-token');
    let getChatUrl = 'http://localhost:8000/chat/get';

    if (chatToken) {
        getChatUrl += `?token=${chatToken}`;
    }

    fetch(getChatUrl)
        .then(handleFetchResponse)
        .then(({ token, messages }) => {
            localStorage.setItem('chat-token', token);

            const socket = setupWebSocket(token);
            document.body.insertAdjacentHTML('beforeend', html_content);

            const chatBody = document.getElementById('chat-body');
            messages.forEach(({ from_user, text }) => {
                const messageType = from_user ? 'user-message' : 'other-message';
                const newMessage = `<div class="message ${messageType}">${text}</div>`;
                chatBody.insertAdjacentHTML('beforeend', newMessage);
            });

            setupChatInteractions(socket);
        })
        .catch(handleFetchError);
}

function handleFetchResponse(response) {
    if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
    }
    return response.json();
}

function handleFetchError(error) {
    console.error('Fetch error:', error);
}

function setupWebSocket(token) {
    const socket = new WebSocket(`ws://127.0.0.1:8000/chat/${token}`);

    socket.onopen = () => {
        socket.onmessage = ({ data }) => {
            var jsonData = JSON.parse(data);
            console.log(jsonData)
            var newMessage = "";
            if (jsonData.from_user){
                newMessage = `<div class="message user-message">${jsonData.message}</div>`;
            } else {
                new Audio('http://localhost:8000/static/tick.ogg').play();
                newMessage = `<div class="message other-message">${jsonData.message}</div>`;
            }
            document.getElementById('chat-body').insertAdjacentHTML('beforeend', newMessage);
        };
    };

    socket.onerror = error => {
        console.error('WebSocket error:', error);
    };

    return socket;
}

function setupChatInteractions(socket) {
    const chatContainer = document.getElementById('chat-container');
    const openChatBtn = document.getElementById('open-chat-btn');

    openChatBtn.addEventListener('click', () => {
        chatContainer.style.display = (chatContainer.style.display === 'block') ? 'none' : 'block';
    });

    const sendBtn = document.getElementById('send-button');
    sendBtn.addEventListener('click', () => {
        const inputValue = document.getElementById('chat-input').value.trim();
        if (inputValue) {
            document.getElementById('chat-input').value = '';
            const newMessage = `<div class="message user-message">${inputValue}</div>`;
            document.getElementById('chat-body').insertAdjacentHTML('beforeend', newMessage);
            socket.send(inputValue);
        }
    });
}

function initializeChat() {
    window.onload = getChat;
}

initializeChat();
