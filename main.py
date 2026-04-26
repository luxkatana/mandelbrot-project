from PIL import Image
import matplotlib.cm
import mandelbrot_rust
from time import perf_counter
from viewport import Viewport
import numpy as np

colormap = matplotlib.cm.get_cmap("viridis").colors

MAX_ITERATION: int = 256


def paint(
    mandelbrot,
    viewport: Viewport,
    palette: tuple[int, ...],
    smooth: bool = True,
):
    for pixel in viewport:
        stability = mandelbrot.stability(complex(pixel), smooth, True)
        index = int(min(stability * len(palette), len(palette) - 1))
        pixel.color = palette[index % len(palette)]


def denormalize(palette) -> list[tuple]:
    return [(tuple(int(channel * 255) for channel in color)) for color in palette]


# begin = perf_counter()
# for y in range(0, img.height):
#     for x in range(0, img.width):
#         complex_number = complex(x - img.width / 2, img.height / 2 - y)
#         (mandelbrotset.get_iteration_count(complex_number, False))
#
# print((perf_counter() - begin) * 1000)
#
# exit(0)
if __name__ == "__main__":
    palette = denormalize(colormap)

    mandelbrotset = mandelbrot_rust.MandelbrotSet(1000, MAX_ITERATION)

    FPS = 30
    TOTAL_SECONDS = 10

    widths = np.geomspace(0.01, 0.001, FPS * TOTAL_SECONDS)
    begin = perf_counter()
    for index, width in enumerate(widths):
        print(f"Working on {index}")
        image = Image.new("RGB", (512, 512), 1)
        viewport = Viewport(
            image, center=(-0.743643887037151 + 0.13182590420533j), width=width
        )

        paint(mandelbrotset, viewport=viewport, palette=palette)
        with open(f"./img/{index}.jpg", "wb") as file:
            image.save(file)
    end = perf_counter()
    print(end - begin)

# for y in range(0, img.height):
#     for x in range(0, img.width):
#         complex_number = scale * complex(x - img.width / 2, img.height / 2 - y)
#         instability: float = 1 - mandelbrotset.stability(complex_number, True)
#         # Op de schaal van 0 tot 1: Hoe INSTABIEL is de complexe getal?
#         img.putpixel((x, y), int(instability * 255))
