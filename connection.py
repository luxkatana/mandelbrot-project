import os
from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
import signal
from mandelbrot_utils import CENTER, FPS, HEIGHT, MAX_ITERATION, WIDTH, create_segments
import cv2
import ftp
from threading import Thread
import progressbar
import numpy as np
from threading import Lock
import asyncio

api = FastAPI()
# api.attendees: set[WebSocket]
api.attendees = []
api.ftpserver = None
ongoingLock = Lock()
attendeeslistLock = Lock()

api.segments = []
FTP_ADDR = ("0.0.0.0", 3000)


async def background():
    authorizer = ftp.create_authorizer()
    print("Background function is running")
    await asyncio.sleep(10)  # TODO: make it longer
    ongoingLock.acquire_lock()  # Locked
    print(f"len(api.attendees): {len(api.attendees)}")
    segments = create_segments(len(api.attendees))
    api.segments = segments

    for index, client in enumerate(api.attendees):
        client: WebSocket
        segment: np.ndarray = segments[index]
        user, password = ftp.create_user(authorizer)
        await client.send_json(
            {
                "segment": segment.tolist(),
                "user": user,
                "password": password,
                "center_re": CENTER.real,
                "center_im": CENTER.imag,
                "resolution": [WIDTH, HEIGHT],
                "max_iteration": MAX_ITERATION,
            }
        )  # JSON list of floats

        # await client.close()

    ftpserver = ftp.create_ftp_server(authorizer, FTP_ADDR)
    api.ftpserver = ftpserver
    print("Ftp running")
    Thread(target=ftpserver.serve_forever).start()


async def merge_ftp_result():
    output = cv2.VideoWriter(
        "./output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), FPS, (WIDTH, HEIGHT)
    )
    for segment in progressbar.progressbar(api.segments):
        for frame in segment:
            frame: float
            img = cv2.imread(f"./mandelbrot_buffer/{frame}.jpg")
            output.write(img)
    output.release()
    output = None


@api.websocket("/attend")
async def attend(websocket: WebSocket):
    await websocket.accept()
    if ongoingLock.locked() is True:
        raise WebSocketException(
            status.WS_1013_TRY_AGAIN_LATER
        )  # Late, already computing.
    api.attendees.append(websocket)
    if len(api.attendees) == 1:  # Starting server.
        await asyncio.create_task(background())
    while True:
        try:
            await websocket.receive_text()
        except WebSocketDisconnect as e:
            print("Reason: ", e.code)
            if e.code == 1000:
                attendeeslistLock.acquire()
                del api.attendees[api.attendees.index(websocket)]
                attendeeslistLock.release()
                if len(api.attendees) == 0:
                    api.ftpserver.close()
                    asyncio.create_task(merge_ftp_result())
                    os.kill(os.getpid(), signal.SIGTERM)
                break
