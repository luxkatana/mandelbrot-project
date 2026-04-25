import mandelbrotset
import numpy as np

mandelbrot = mandelbrotset.MandelbrotSet(1000, 256)
height = 512
width = 512
for x in range(width):
    for y in range(height):
        c = complex(x - (width / 2), (height / 2) - y)
        print(mandelbrot.get_iteration_count(c))
