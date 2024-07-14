import asyncio
import websockets
import json

connected_clients = set()
chat_history = []

async def handle_client(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            chat_history.append(data)
            await broadcast(json.dumps(data))
    finally:
        connected_clients.remove(websocket)

async def broadcast(message):
    for client in connected_clients:
        await client.send(message)

async def main():
    server = await websockets.serve(handle_client, "localhost", 8765)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())