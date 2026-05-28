import websockets, asyncio, json
from io import BytesIO, FileIO
from ftplib import FTP
from PIL import Image
import mandelbrot_utils
import mandelbrot_rust
import rich

from viewport import Viewport

MASTER = ("0.0.0.0", 8000)


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
        mandelbrotset = mandelbrot_rust.MandelbrotSet(
            1000, payloaddata["max_iteration"]
        )

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
        ftpclient = FTP()
        ftpclient.connect(MASTER[0], 2000)
        ftpclient.login(payloaddata["user"], payloaddata["password"])

        for index, img in enumerate(result):
            with BytesIO() as f:
                img.save(f, format="JPEG")
                f.seek(0)
                ftpclient.storbinary(f"STOR {payloaddata['segment'][index]}.jpg", f)
                print(f"Stored {index}/{len(result)}")
        await wsclient.send("finish")
        ftpclient.close()


if __name__ == "__main__":
    asyncio.run(main())
