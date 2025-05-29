// Получаем данные из скрытого элемента
const roomData = document.getElementById("room-data");
const roomId = roomData.getAttribute("data-room-id");
const username = roomData.getAttribute("data-username");
const userId = roomData.getAttribute("data-user-id");

const ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}/${userId}?username=${username}`);

ws.onopen = () => {
    console.log("Соединение установлено");
};

ws.onclose = () => {
    console.log("Соединение закрыто");
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "chat") {
        appendChatMessage(data.text, data.is_self);
    } else if (data.type === "random_number") {
        appendRandomNumber(data.value);
    }
};

function appendChatMessage(text, isSelf) {
    const messages = document.getElementById("messages");
    const message = document.createElement("div");

    message.className = isSelf
        ? "p-2 my-1 bg-blue-500 text-white rounded-md self-end max-w-xs ml-auto"
        : "p-2 my-1 bg-gray-200 text-black rounded-md self-start max-w-xs";

    message.textContent = text;
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
}

function appendRandomNumber(number) {
    const box = document.getElementById("random-numbers");
    const numberEl = document.createElement("div");
    numberEl.className = "text-yellow-800";
    numberEl.textContent = `🎲 ${number}`;
    box.appendChild(numberEl);
    box.scrollTop = box.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById("messageInput");
    if (input.value.trim()) {
        ws.send(input.value);
        input.value = '';
    }
}

document.getElementById("messageInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendMessage();
    }
});

