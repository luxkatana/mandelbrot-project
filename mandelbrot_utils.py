from PIL import Image
import matplotlib.cm
import mandelbrot_rust
from time import perf_counter
from viewport import Viewport
from threading import Thread
import numpy as np
import cv2

colormap = matplotlib.cm.get_cmap("viridis").colors

MAX_ITERATION: int = 256

FPS = 30
TOTAL_SECONDS = 2
WIDTH = 512
HEIGHT = 512
N_SEGMENTS: int = 14
CENTER: complex = -0.743643887037151 + 0.13182590420533j


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

video = cv2.VideoWriter(
    "./output.mp4", cv2.VideoWriter_fourcc(*"MP4V"), FPS, (WIDTH, HEIGHT)
)
mandelbrotset = mandelbrot_rust.MandelbrotSet(1000, MAX_ITERATION)
palette = denormalize(colormap)


def generate_from_segment(segment: list[float], idx: int, results: list):
    result = []
    for index, width in enumerate(segment):
        img = Image.new("RGB", (WIDTH, HEIGHT), 1)
        viewport = Viewport(img, center=CENTER, width=width)
        paint(mandelbrotset, viewport, palette)  # Hier wordt gegenereerd
        print(f"Thread {idx}: {index}/{len(segment)}")
        result.append(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))
    results[idx] = result


def create_segments(amount_of_segments: int) -> list[list[float]]:
    widths = np.geomspace(0.01, 0.001, FPS * TOTAL_SECONDS)

    return np.array_split(widths, amount_of_segments)


if __name__ == "__main__":
    segments = generate_from_segment(N_SEGMENTS)

    allthreads: list[Thread] = []
    begin = perf_counter()
    results = []
    for index, segment in enumerate(segments):
        t = Thread(target=generate_from_segment, args=(segment, index, results))
        allthreads.append(t)
        t.start()
        results.append(0)
    for thread in allthreads:
        thread.join()

    print("Compute finish")
    for part in results:
        part: list[list]
        for image in part:
            video.write(image)
    video.release()

    print("Everything finished.")
    print(type(results[0]))
    print(perf_counter() - begin)
    exit(0)

    for index, width in enumerate(widths):
        print(f"Working on {index}")
        image = Image.new("RGB", (WIDTH, HEIGHT), 1)
        viewport = Viewport(
            image, center=(-0.743643887037151 + 0.13182590420533j), width=width
        )

        paint(mandelbrotset, viewport=viewport, palette=palette)
        image_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        video.write(image_array)

    video.release()
    end = perf_counter()
    print(end - begin)
