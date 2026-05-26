import websockets, asyncio, json
from PIL import Image
import mandelbrot_utils
import mandelbrot_rust
import rich

from viewport import Viewport

MASTER = ("127.0.0.1", 8000)


async def main():
    async with websockets.connect(f"ws://{MASTER[0]}:{MASTER[1]}/attend") as wsclient:
        payloaddata = await wsclient.recv()
        payloaddata: dict[str] = json.loads(payloaddata)
        """
        payloaddata = {
        "segment": [float...],
        "user": str,
        "password": str,
         "center_re": CENTER.real(),
         "center_im": CENTER.imag(),
         "resolution": [width, height]
        }
        """
    mandelbrotset = mandelbrot_rust.MandelbrotSet(1000, payloaddata["max_iteration"])

    center = complex(payloaddata["center_re"], payloaddata["center_im"])

    result: list[Image.Image] = []
    for width in payloaddata["segment"]:
        img = Image.new("RGB", payloaddata["resolution"], 1)
        width: float
        viewport = Viewport(img, center=center, width=width)
        mandelbrot_utils.paint(mandelbrotset, viewport, mandelbrot_utils.palette)
        print("Compute finish ", width)
        result.append(img)

    rich.print(payloaddata)


if __name__ == "__main__":
    asyncio.run(main())
