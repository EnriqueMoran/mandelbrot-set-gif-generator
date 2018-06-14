import time
import math
import random
from ctypes import windll
from PIL import Image


class Mandelbrot():

    __author__: "EnriqueMoran"

    def transformInterval(self, e1, e2, s1, s2, x):    # Transform [0, image_width] and [0, image_heigth] into [-2, 2] interval
        return (s1 - s2) / (e1 - e2) * (x - e1) + s1

    def __init__(self, image_width, image_heigth, image_path, iteration_depth = 100, zoom = 1, x0 = 0, y0 = 0, c = 0j):
        self.image_width = image_width
        self.image_heigth = image_heigth
        self.iteration_depth = iteration_depth    # Used on escape time algorithm
        self.image_path = image_path    # Where the resultant image will be saved
        self.zoom = zoom
        self.c = c    # C on z = z^2 + c equation
        self.s1_x = x0 + 2 * -zoom  # Initial x coordinate
        self.s2_x = x0 + 2 * zoom
        self.s2_y = y0 + 2 * zoom  # Initial y coordinate
        self.s1_y = y0 + 2 * -zoom
        self.img = Image.new("RGB", (self.image_width, self.image_heigth))
        self.pixels = self.img.load()
        

    def drawFractal(self, pixel_colors, save = True):

        def intToRGB(n):    # Convert integer into RGB value
            return n & 255, (n >> 8) & 255, (n >> 16) & 255 

        for i in range(self.image_width):
            for j in range(self.image_heigth):
                val_i = self.transformInterval(0, self.image_width, self.s1_x, self.s2_x, i)    # Normalize i and j between [-2, 2]
                val_j = self.transformInterval(0, self.image_heigth, self.s1_y, self.s2_y, j)
                value = self.mandelbrot(complex(val_i, val_j))
                if value == self.iteration_depth:
                    self.pixels[i, j] = (0, 0 ,0)
                else:
                    blue, green, red = intToRGB(value)
                    self.pixels[i, j] = (blue, green, red)
        if save:
            self.img.save(self.image_path)    # Save every frame
        return self.img


    def mandelbrot(self, c, z = None):
        if z == None:
            z = self.c
        else:
            z = (z * z) + c
        n_iter = 0    # Number of iterations to escape
        while n_iter < self.iteration_depth:
            if z.real > 2.0:    # Escape condition
                return n_iter
            else:
                z = (z * z) + c
            n_iter += 1
        return n_iter


    def createGif(self, x, y, n_frames, initial_zoom, zoom_per_frame, path, iterations, save_frames = False):
        images = []
        zoom = initial_zoom
        t00 = time.time()
        for i in range(n_frames):
            t0 = time.time()
            mand = Mandelbrot(image_width, image_heigth, image_path, iterations, zoom, x0, y0)
            img = Image.new("RGB", (image_width, image_heigth))
            img = mand.drawFractal(mandelbrot.pixels, save_frames)    # save_frames by default: dont save each frame
            name = "frame" + str(i + 1) + ".gif"
            images.append(img)
            t1 = time.time()
            print("Frame number ", str(i + 1), " generated. Time taken: ", str(t1 - t0))
            zoom -= 4 * zoom / zoom_per_frame
        t11 = time.time()
        print("Gif created, time taken: ", str(t11 - t00))
        img.save(path, save_all = True, append_images = [i for i in images], loop = 0, duration = 250)
