import time
import math
import random
from ctypes import windll
from PIL import Image


class Mandelbrot():

    __author__ : "EnriqueMoran"

    __version__ : "0.36.1"

    def transformInterval(self, e1, e2, s1, s2, x):    # Transform [0, image_width] and [0, image_height] into [-2, 2] interval
        return (s1 - s2) / (e1 - e2) * (x - e1) + s1

    def __init__(self, image_width, image_height, image_path, iteration_depth = 100, zoom = 1, x0 = 0, y0 = 0):
        self.image_width = image_width
        self.image_height = image_height
        self.iteration_depth = iteration_depth    # Used on escape time algorithm
        self.image_path = image_path    # Where the resultant image will be saved
        self.zoom = zoom
        self.s1_x = x0 + 2 * -zoom  # Initial x coordinate
        self.s2_x = x0 + 2 * zoom
        self.s2_y = y0 + 2 * -zoom  # Initial y coordinate
        self.s1_y = y0 + 2 * zoom
        self.img = Image.new("HSV", (self.image_width, self.image_height))
        self.pixels = self.img.load()
        

    def drawFractal(self, pixel_colors, save = True):

        def intToRGB(n):    # Convert integer into RGB value
            return n & 255, (n >> 8) & 255, (n >> 16) & 255 

        for i in range(self.image_width):
            for j in range(self.image_height):
                val_i = self.transformInterval(0, self.image_width, self.s1_x, self.s2_x, i)    # Normalize i and j between [-2, 2]
                val_j = self.transformInterval(0, self.image_height, self.s1_y, self.s2_y, j)
                value = self.mandelbrot(complex(val_i, val_j))
                if value == self.iteration_depth:
                    self.pixels[i, j] = (int(value), 255 ,0)
                else:
                    #blue, green, red = intToRGB(value)
                    self.pixels[i, j] = (int(value), 255, 255)
        if save:
            self.img.convert("RGB").save(self.image_path)    # Save every frame
        return self.img


    def mandelbrot(self, c, z = None):
        z = 0j
        n_iter = 0    # Number of iterations to escape
        while n_iter < self.iteration_depth and z.real * z.real + z.imag * z.imag < 2.0 * 2.0 and not math.isnan(z.real) and not  math.isnan(z.imag):
            z = (z * z) + c
            n_iter += 1
        if n_iter == self.iteration_depth:
            return self.iteration_depth
        else:
            return n_iter + 1 - math.log(math.log2(abs(z)))

    def createGif(self, x, y, n_frames, initial_zoom, zoom_per_frame, path, iterations, save_frames = False):
        images = []
        zoom = initial_zoom
        t00 = time.time()
        for i in range(n_frames):
            t0 = time.time()
            mand = Mandelbrot(self.image_width, self.image_height, path, iterations, zoom, x, y)
            img = Image.new("HSV", (self.image_width, self.image_height))
            img = mand.drawFractal(mand.pixels, save_frames)    # save_frames by default: dont save each frame
            name = "frame" + str(i + 1) + ".gif"
            images.append(img)
            t1 = time.time()
            #print("Frame number ", str(i + 1), " generated. Time taken: ", str(t1 - t0))
            zoom -= 4 * zoom / zoom_per_frame
        t11 = time.time()
        #print("Gif created, time taken: ", str(t11 - t00))
        #img.convert("RGB").save(path, save_all = True, append_images = [i for i in images], loop = 0, duration = 250)
        return images