from concurrent.futures import ProcessPoolExecutor
from functools import partial
import websockets, asyncio, json
from io import BytesIO
import progressbar
from time import perf_counter
from ftplib import FTP
from PIL import Image
import multiprocessing
import mandelbrot_utils
import mandelbrot_rust

from viewport import Viewport

MASTER = ("0.0.0.0", 8000)
FTP_PORT = 3000
N_PROCESSES: int = 5


def m_paint(payloaddata: dict, width: float) -> Image.Image:
    mandelbrotset = mandelbrot_rust.MandelbrotSet(1000, payloaddata["max_iteration"])
    img = Image.new("RGB", payloaddata["resolution"], 1)
    viewport = Viewport(
        img,
        center=complex(payloaddata["center_re"], payloaddata["center_im"]),
        width=width,
    )
    mandelbrot_utils.paint(mandelbrotset, viewport, mandelbrot_utils.palette)
    return img


def compute(payloaddata: dict):
    painting_modified = partial(m_paint, payloaddata)

    with multiprocessing.Pool(N_PROCESSES) as pool:
        print(f"Spawning {N_PROCESSES} processses")
        begin = perf_counter()
        result = pool.map(
            painting_modified,
            payloaddata["segment"],
        )
        end = perf_counter()
        print(f"Time taken for computation: {(end - begin):.2f} seconds")

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
        print("Connected, awaiting.")
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
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as pool:
            await loop.run_in_executor(pool, compute, payloaddata)


if __name__ == "__main__":
    asyncio.run(main())
