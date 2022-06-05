from collections import defaultdict

from starlette.websockets import WebSocket


class ConnectionManager:

    def __init__(self):
        self.connections: dict = defaultdict(dict)

    def get_members_room(self, room_name: int):
        try:
            return self.connections[room_name]
        except Exception as e:
            print(e)
            return None

    async def connect(self, websocket: WebSocket, room_name: int):
        await websocket.accept()
        if self.connections[room_name] == {} or len(self.connections[room_name]) == 0:
            self.connections[room_name] = []
        self.connections[room_name].append(websocket)
        print(f"CONNECTIONS : {self.connections[room_name]}")

    def remove(self, websocket: WebSocket, room_name: int):
        self.connections[room_name].remove(websocket)
        print(
            f"CONNECTION REMOVED\nREMAINING CONNECTIONS : {self.connections[room_name]}"
        )

    async def send_to_room(self, message: dict, room_name: int):
        living_connections = []
        while len(self.connections[room_name]) > 0:
            websocket = self.connections[room_name].pop()
            await websocket.send_json(message)
            living_connections.append(websocket)
        self.connections[room_name] = living_connections
