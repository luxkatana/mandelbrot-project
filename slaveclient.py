from concurrent.futures import ProcessPoolExecutor
import websockets, asyncio, json
from io import BytesIO
import progressbar
from ftplib import FTP
from PIL import Image
import multiprocessing
import mandelbrot_utils
import mandelbrot_rust

from viewport import Viewport

MASTER = ("0.0.0.0", 8000)
FTP_PORT = 3000
N_PROCESSES: int = 5


def compute(center: complex, payloaddata: dict):
    mandelbrotset = mandelbrot_rust.MandelbrotSet(1000, payloaddata["max_iteration"])
    result: list[Image.Image] = []
    for width in progressbar.progressbar(payloaddata["segment"]):
        img = Image.new("RGB", payloaddata["resolution"], 1)
        width: float
        viewport = Viewport(img, center=center, width=width)
        mandelbrot_utils.paint(mandelbrotset, viewport, mandelbrot_utils.palette)
        result.append(img)

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


async def main():
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
            await loop.run_in_executor(pool, compute, center, payloaddata)


if __name__ == "__main__":
    print(f"Spawning {N_PROCESSES} processes.")
    processes: set[multiprocessing.Process] = set()
    for _ in range(N_PROCESSES):
        process = multiprocessing.Process(target=lambda: asyncio.run(main()))
        process.start()
        processes.add(process)
    for process in processes:
        process.join()

    # asyncio.run(main())
