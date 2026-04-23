from PIL import Image
import matplotlib.cm
from math import log2
from viewport import Viewport

colormap = matplotlib.cm.get_cmap("viridis").colors

MAX_ITERATION: int = 256


class MandelbrotSet:
    escape_radius: float = 1000

    def get_iteration_count(self, c: complex, smooth: bool = False) -> int:
        z = 0
        for n in range(MAX_ITERATION):
            z = z**2 + c
            if abs(z) > self.escape_radius:
                if smooth is True:
                    return n + 1 - log2(abs(z))
                return n
        return MAX_ITERATION

    def __contains__(self, c: complex) -> bool:
        return self.stability(c, True) == 1

    def stability(self, c: complex, smooth: bool, clamp: bool = True) -> float:
        stable: float = self.get_iteration_count(c, smooth) / MAX_ITERATION
        return max(0, min(stable, 1.0)) if clamp else stable


def paint(
    mandelbrot: MandelbrotSet,
    viewport: Viewport,
    palette: tuple[int, ...],
    smooth: bool = True,
):
    for pixel in viewport:
        stability = mandelbrot.stability(complex(pixel), smooth)
        index = int(min(stability * len(palette), len(palette) - 1))
        pixel.color = palette[index % len(palette)]


def denormalize(palette) -> list[tuple]:
    return [(tuple(int(channel * 255) for channel in color)) for color in palette]


palette = denormalize(colormap)

mandelbrotset = MandelbrotSet()


image = Image.new("RGB", (512, 512), 1)
# for y in range(0, img.height):
#     for x in range(0, img.width):
#         complex_number = scale * complex(x - img.width / 2, img.height / 2 - y)
#         instability: float = 1 - mandelbrotset.stability(complex_number, True)
#         # Op de schaal van 0 tot 1: Hoe INSTABIEL is de complexe getal?
#         img.putpixel((x, y), int(instability * 255))
viewport = Viewport(image, center=-0.74364 + 0.13182733j, width=0.00012068)

paint(mandelbrotset, viewport=viewport, palette=palette)
image.show()
