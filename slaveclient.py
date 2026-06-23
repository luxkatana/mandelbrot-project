from concurrent.futures import ProcessPoolExecutor
from multiprocessing.connection import Connection
import warnings
import websockets, asyncio, json
from io import BytesIO
import progressbar
from ftplib import FTP
import os
from PIL import Image
from multiprocessing import Process, Pipe, cpu_count
import mandelbrot_utils
import mandelbrot_rust

from viewport import Viewport

MASTER = ("0.0.0.0", 8000)
FTP_PORT = 3000
N_PROCESSES: int = -1
if __name__ == "__main__":
    if N_PROCESSES == -1:
        print(
            f"N_PROCESSES = multiprocessing.cpu_count() # Which is {cpu_count()}, using all cores"
        )
        N_PROCESSES = cpu_count()
    elif N_PROCESSES > cpu_count():
        warnings.warn(
            f"N_processes is higher than cpu_count, which may cause problems."
        )


def compute(center: complex, payloaddata: dict, transmitter: Connection, pid: int):
    mandelbrotset = mandelbrot_rust.MandelbrotSet(1000, payloaddata["max_iteration"])
    result: list[Image.Image] = []
    segmentlen = len(payloaddata["segment"])
    for index, width in enumerate(payloaddata["segment"], start=1):
        img = Image.new("RGB", payloaddata["resolution"], 1)
        width: float
        viewport = Viewport(img, center=center, width=width)
        mandelbrot_utils.paint(mandelbrotset, viewport, mandelbrot_utils.palette)
        result.append(img)
        if index % 10 == 0:
            transmitter.send({"pid": pid, "total": segmentlen, "done": index})

    ftpclient = FTP()
    ftpclient.connect(MASTER[0], FTP_PORT)
    ftpclient.login(payloaddata["user"], payloaddata["password"])
    print("Sending files with ftp...")
    for index, img in progressbar.progressbar(enumerate(result)):
        with BytesIO() as f:
            img.save(f, format="JPEG")
            f.seek(0)
            ftpclient.storbinary(f"STOR {payloaddata['segment'][index]}.jpg", f)
    ftpclient.close()


async def main(transmitter: Connection):
    async with websockets.connect(
        f"ws://{MASTER[0]}:{MASTER[1]}/attend", ping_interval=None
    ) as wsclient:
        payloaddata = await wsclient.recv()
        payloaddata: dict[str] = json.loads(payloaddata)
        """
        payloaddata = {
        "segment": list[float],
        "user": str,
        "password": str,
         "center_re": CENTER.real(), # float
         "center_im": CENTER.imag(), # float
         "resolution": [width, height] # list[int, int]
        }
        """
        center = complex(payloaddata["center_re"], payloaddata["center_im"])
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as pool:
            await loop.run_in_executor(
                pool, compute, center, payloaddata, transmitter, os.getpid()
            )


def run_process(transmitter: Connection):
    asyncio.run(main(transmitter))


if __name__ == "__main__":
    print(f"Spawning {N_PROCESSES} processes.")
    processes: set[Process] = set()
    transmitter, receiver = Pipe()
    for _ in range(N_PROCESSES):

        process = Process(target=run_process, args=(transmitter,))
        process.start()
        processes.add(process)

    while len(processes) > 0:
        if receiver.poll() is True:
            status: dict[str] = receiver.recv()
            processid: int = status["pid"]
            print(f"Process {processid} {status['done']}/{status['total']}")

        for process in processes:
            if process.is_alive() is False:
                processes.remove(process)


# asyncio.run(main())
