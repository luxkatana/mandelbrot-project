from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from mandelbrot_utils import create_segments
import ftp
import numpy as np
from threading import Lock
import asyncio

api = FastAPI()
# api.attendees: set[WebSocket]
api.attendees = set()
ongoingLock = Lock()
FTP_ADDR = ("127.0.0.1", 2000)


async def background():
    authorizer = ftp.create_authorizer()
    print("Background function is running")
    await asyncio.sleep(10)  # TODO: make it longer
    ongoingLock.acquire_lock()  # Locked
    print(f"len(api.attendees): {len(api.attendees)}")
    segments = create_segments(len(api.attendees))

    for index, client in enumerate(api.attendees):
        client: WebSocket
        segment: np.ndarray = segments[index]
        user, password = ftp.create_user(authorizer)
        await client.send_json(
            {"segment": segment.tolist(), "user": user, "password": password}
        )  # JSON list of floats

        print("Data sent to client ", index)
        await client.close()

    ftpserver = ftp.create_ftp_server(authorizer, FTP_ADDR)
    print("Ftp running")
    ftpserver.serve_forever()
    print("FTP closed")


@api.websocket("/attend")
async def attend(websocket: WebSocket):
    await websocket.accept()
    if ongoingLock.locked() is True:
        raise WebSocketException(
            status.WS_1013_TRY_AGAIN_LATER
        )  # Late, already computing.
    api.attendees.add(websocket)
    if len(api.attendees) == 1:  # Starting server.
        print("Start")
        await asyncio.create_task(background())
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
    except WebSocketDisconnect:
        ...
