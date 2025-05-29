import asyncio
import random
from typing import Dict, Set
from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        self.room_numbers_sent: Dict[int, Set[int]] = {}
        self.room_tasks: Dict[int, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
            self.room_numbers_sent[room_id] = set()
            self.room_tasks[room_id] = asyncio.create_task(self._send_random_numbers(room_id))

        self.active_connections[room_id][user_id] = websocket

    def disconnect(self, room_id: int, user_id: int):
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            del self.active_connections[room_id][user_id]

            # Если в комнате больше нет пользователей — чистим всё
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                self.room_tasks[room_id].cancel()
                del self.room_tasks[room_id]
                del self.room_numbers_sent[room_id]

    async def broadcast(self, message: str, room_id: int, sender_id: int):
        if room_id in self.active_connections:
            for user_id, connection in self.active_connections[room_id].items():
                await connection.send_json({
                    "type": "chat",
                    "text": message,
                    "is_self": user_id == sender_id
                })

    async def _send_random_numbers(self, room_id: int):
        while True:
            await asyncio.sleep(3)

            # Все числа уже отправлены
            if len(self.room_numbers_sent[room_id]) >= 100:
                self.room_numbers_sent[room_id].clear()

            available = [n for n in range(1, 101) if n not in self.room_numbers_sent[room_id]]
            number = random.choice(available)
            self.room_numbers_sent[room_id].add(number)

            # Рассылка всем пользователям комнаты
            for connection in self.active_connections.get(room_id, {}).values():
                await connection.send_json({
                    "type": "random_number",
                    "value": number
                })


