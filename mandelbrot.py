import time
import math
import random
from multiprocess.pool import Pool
from ctypes import windll
from PIL import Image


class Mandelbrot():

    __author__ : "EnriqueMoran"

    __version__ : "1.2"

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


    def drawFractal(self, x0, y0, x1, y1):
        image_width = self.image_width
        image_height = self.image_height
        s1_x = self.s1_x
        s2_x = self.s2_x
        s1_y = self.s1_y
        s2_y = self.s2_y
        iteration_depth = self.iteration_depth

        def transformInterval(e1, e2, s1, s2, x):    # Transform [0, image_width] and [0, image_height] into [-2, 2] interval
            return (s1 - s2) / (e1 - e2) * (x - e1) + s1

        def mandelbrot(c, z = None):
            z = 0j
            n_iter = 0    # Number of iterations to escape
            while n_iter < iteration_depth and z.real * z.real + z.imag * z.imag < 2.0 * 2.0 and not math.isnan(z.real) and not  math.isnan(z.imag):
                z = (z * z) + c
                n_iter += 1
            if n_iter == iteration_depth:
                return iteration_depth
            else:
                return n_iter + 1 - math.log(math.log2(abs(z)))

        def intToRGB(n):    # Convert integer into RGB value
            return n & 255, (n >> 8) & 255, (n >> 16) & 255

        def draw(x0, y0, x1, y1):
            t_img = Image.new("HSV", (int(x1) - int(x0), int(y1) - int(y0)))
            pixels = t_img.load()
            for i in range(int(x0), int(x1)):
                for j in range(int(y0), int(y1)):
                    val_i = transformInterval(0, image_width, s1_x, s2_x, i)    # Normalize i and j between [-2, 2]
                    val_j = transformInterval(0, image_height, s1_y, s2_y, j)
                    value = mandelbrot(complex(val_i, val_j))
                    if value == iteration_depth:
                        pixels[i % (int(x1) - int(x0)), j % (int(y1) - int(y0))] = (int(value), 255 , 0)
                    else:
                        pixels[i % (int(x1) - int(x0)), j % (int(y1) - int(y0))] = (int(value), 255, 255)
            return t_img

        #with Pool(processes = 4) as pool:
        #    p1, p2, p3, p4 = pool.starmap(draw, [(0, 0, image_width / 2, image_height / 2), (image_width / 2, 0, image_width, image_height / 2), (0, image_height / 2, image_width / 2, image_height), (image_width / 2, image_height / 2, image_width, image_height)])
        with Pool(processes = 1) as pool:
            p1 = pool.starmap(draw, [(0, 0, image_width / 2, image_height / 2)])
            pool.close()
            pool.join()
            img = Image.new("HSV", (image_width, image_height))
            #img.paste(p1, (0, 0))
            #img.paste(p2, (int(image_width / 2), 0))
            #img.paste(p3, (0, int(image_height / 2)))
            #img.paste(p4, ((int(image_width / 2), int(image_height / 2))))

        return p1


    def createGif(self, x, y, n_frames, initial_zoom, zoom_per_frame, path, iterations, save_frames = False):
        images = []
        zoom = initial_zoom
        t00 = time.time()
        for i in range(n_frames):
            t0 = time.time()
            mand = Mandelbrot(self.image_width, self.image_height, path, iterations, zoom, x, y)
            t_img = mand.drawFractal(0, 0, self.image_width, self.image_height)

            images.append(t_img)
            t1 = time.time()
            print("Frame number ", str(i + 1), " generated. Time taken: ", str(t1 - t0))
            zoom -= 4 * zoom / zoom_per_frame

        t11 = time.time()
        print("Gif created, time taken: ", str(t11 - t00))
        t_img.convert("RGB").save(path, save_all = True, append_images = [i for i in images], loop = 0, duration = 250)



if __name__ == "__main__":

    image_path = "mandelbrot_test_thread.gif"
    iterations = 500
    image_width = 500
    image_heigth = 500
    n_frames = 1
    frames_per_zoom = 10
    image_zoom = 1
    x_coordinate = 0
    y_coordinate = 0

    mandelbrot = Mandelbrot(image_width, image_heigth, image_path)
    mandelbrot.createGif(x_coordinate, y_coordinate, n_frames, image_zoom, frames_per_zoom, image_path, iterations)
