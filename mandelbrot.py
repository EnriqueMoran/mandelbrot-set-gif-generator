import time
import math
from ctypes import windll
from PIL import Image


class Mandelbrot():

    def __init__(self, image_width, image_heigth, iteration_depth, image_path):
        self.image_width = image_width
        self.image_heigth = image_heigth
        self.iteration_depth = iteration_depth
        self.image_path = image_path
        self.pixel_values = {(i, j) : (0, 0, 0) for i in range(int(-self.image_width / 2),  int(self.image_width / 2)) for j in range(int(-self.image_heigth / 2), int(self.image_heigth / 2))}
        self.img = Image.new("RGB", (self.image_width, self.image_heigth))
        self.pixels = self.img.load()
        

    def drawFractal(self, pixel_colors):
        def intToRGB(n):
            return n & 255, (n >> 8) & 255, (n >> 16) & 255 

        for i in range(self.image_width):
            for j in range(self.image_heigth):
                val_i = i - self.image_width / 1.3    # Center image
                val_j = j - self.image_heigth / 1.9
                value = self.mandelbrot(complex(val_i * 2 / self.image_width, val_j * 2 / self.image_heigth))    # Normalize i and j between [-2, 2]
                if value == self.iteration_depth:
                    self.pixel_values[i,j] = (0, 0 ,0)
                    self.pixels[i, j] = self.pixel_values[(int(i - self.image_width / 2) ,int(j - self.image_heigth / 2))]
                else:
                    val = value * 255 / self.iteration_depth
                    blue, green, red = intToRGB(value)
                    self.pixel_values[(i,j)] = (blue, green, red)
                    self.pixels[i, j] = self.pixel_values[(i,j)]
        self.img.save(self.image_path)


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
    image_path = "mandelbrot.png"
    t0 = time.time()
    iterations = 700
    image_width = 500
    image_heigth = 500
    mandelbrot = Mandelbrot(image_width, image_heigth, iterations, image_path)
    mandelbrot.drawFractal(mandelbrot.pixels)
    t1 = time.time()
    print("Fractal generated in ",  t1 - t0, " seconds.")
