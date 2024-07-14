import asyncio
import websockets
import json
import os
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 使用絕對路徑
chat_history_file = os.path.abspath("chat_history.json")
chat_history = []

def initialize_chat_history():
    if not os.path.exists(chat_history_file):
        save_chat_history()
    else:
        load_chat_history()
    logging.info(f"Chat history initialized. File path: {chat_history_file}")

def load_chat_history():
    global chat_history
    try:
        with open(chat_history_file, 'r') as f:
            chat_history = json.load(f)
        logging.info("Chat history loaded successfully")
    except IOError as e:
        logging.error(f"Error loading chat history: {e}")
        chat_history = []

def save_chat_history():
    try:
        with open(chat_history_file, 'w') as f:
            json.dump(chat_history, f)
        logging.info(f"Chat history saved to {chat_history_file}")
    except IOError as e:
        logging.error(f"Error saving chat history: {e}")

async def handle_client(websocket, path):
    try:
        for message in chat_history:
            await websocket.send(json.dumps(message))
        
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get('type') == 'clear_history':
                    chat_history.clear()
                    save_chat_history()
                    await broadcast(json.dumps({"type": "history_cleared"}))
                    logging.info("Chat history cleared")
                else:
                    chat_history.append(data)
                    save_chat_history()
                    await broadcast(json.dumps(data))
                    logging.info(f"New message received and broadcasted: {data}")
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON received: {message}")
            except Exception as e:
                logging.error(f"Error handling message: {e}")
    finally:
        connected.remove(websocket)
        logging.info("Client disconnected")

async def broadcast(message):
    for client in connected:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            logging.warning("Failed to send message to a client due to closed connection")

connected = set()

async def ws_handler(websocket, path):
    connected.add(websocket)
    logging.info("New client connected")
    try:
        await handle_client(websocket, path)
    finally:
        connected.remove(websocket)

async def main():
    initialize_chat_history()
    server = await websockets.serve(ws_handler, "localhost", 8000)
    logging.info("WebSocket server started on localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())