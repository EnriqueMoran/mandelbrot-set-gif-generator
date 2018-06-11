import time
import math
from ctypes import windll
from PIL import Image


class Mandelbrot():

    def __init__(self, iteration_depth, src_image, dst_image):
        self.iteration_depth = iteration_depth
        self.src_image = src_image
        self.dst_image = dst_image
        self.img = Image.open(self.src_image)
        self.pixels = self.img.load()
        self.pixel_values = {(i, j) : (0, 0, 0) for i in range(int(-self.img.size[0] / 2),  int(self.img.size[0] / 2)) for j in range(int(-self.img.size[1] / 2), int(self.img.size[1] / 2))}

    def drawFractal(self, pixel_colors):
        def intToRGB(n):
            return n & 255, (n >> 8) & 255, (n >> 16) & 255 

        for i in range(self.img.size[0]):
            for j in range(self.img.size[1]):
                val_i = i - self.img.size[0] / 1.3    # center image
                val_j = j - self.img.size[1] / 1.9
                value = self.mandelbrot(complex(val_i * 2 / self.img.size[0], val_j * 2 / self.img.size[1]))    # Normalize i and j between [-2, 2]
                if value == self.iteration_depth:
                    self.pixel_values[i,j] = (0, 0 ,0)
                    self.pixels[i, j] = self.pixel_values[(int(i - self.img.size[0] / 2) ,int(j - self.img.size[1] / 2))]
                else:
                    val = value * 255 / self.iteration_depth
                    blue, green, red = intToRGB(value)
                    self.pixel_values[(i,j)] = (blue, green, red)
                    self.pixels[i, j] = self.pixel_values[(i,j)]
        self.img.save(self.dst_image)


    def mandelbrot(self, c, z = 0j):
        z = (z * z) + c
        cont = 0
        while cont < self.iteration_depth:
            if z.real > 2.0:
                return cont
            else:
                z = (z * z) + c
            cont += 1
        return cont




if __name__ == "__main__":
    src_image = "mandelbrot_background_3500x3500.png"
    dst_image = "mandelbrot_background_3500x3500.png"
    t0 = time.time()
    mandelbrot = Mandelbrot(700, src_image, dst_image)
    mandelbrot.drawFractal(mandelbrot.pixels)
    t1 = time.time()
    print("Fractal generated in ",  t1 - t0, " seconds.")
