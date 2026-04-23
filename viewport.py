from dataclasses import dataclass
from PIL.Image import Image


@dataclass
class Pixel:
    viewport: "Viewport"
    x: int
    y: int

    @property
    def color(self):
        return self.viewport.imgbuffer.getpixel((self.x, self.y))

    @color.setter
    def color(self, newvalue: float):
        self.viewport.imgbuffer.putpixel((self.x, self.y), newvalue)

    def __complex__(self):
        return complex(self.x, -self.y) * self.viewport.scale + self.viewport.offset


@dataclass
class Viewport:
    imgbuffer: Image
    center: complex
    width: float

    @property
    def scale(self):
        return self.width / self.imgbuffer.width

    @property
    def height(self):
        return self.scale * self.imgbuffer.height

    @property
    def offset(self):
        return self.center + complex(-self.width, self.height) / 2

    def __iter__(self):
        for y in range(self.imgbuffer.height):
            for x in range(self.imgbuffer.width):
                yield Pixel(self, x, y)
