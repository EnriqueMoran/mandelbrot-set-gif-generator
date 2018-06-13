import time
import math
import random
from ctypes import windll
from PIL import Image


class Mandelbrot():

    __author__: "EnriqueMoran"

    def transformInterval(self, e1, e2, s1, s2, x):
        return (s1 - s2) / (e1 - e2) * (x - e1) + s1

    def __init__(self, image_width, image_heigth, iteration_depth, image_path, zoom = 2, x0 = -2, y0 = -2, c = 0j):
        self.image_width = image_width
        self.image_heigth = image_heigth
        self.iteration_depth = iteration_depth
        self.image_path = image_path
        self.zoom = zoom
        self.c = c    # C on z = z^2 + c equation
        self.s1_x = x0 + 2 * -zoom  # Initial x coordinate
        self.s2_x = x0 + 2 * zoom
        self.s2_y = y0 + 2 * zoom  # Initial y coordinate
        self.s1_y = y0 + 2 * -zoom
        self.img = Image.new("RGB", (self.image_width, self.image_heigth))
        self.pixels = self.img.load()
        

    def drawFractal(self, pixel_colors, save = True):
        def intToRGB(n):
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
            self.img.save(self.image_path)
        return self.img


    def mandelbrot(self, c, z = None):
        if z == None:
            z = self.c
        else:
            z = (z * z) + c
        cont = 0
        while cont < self.iteration_depth:
            if z.real > 2.0:
                return cont
            else:
                z = (z * z) + c
            cont += 1
        return cont


    def createGif(self, n_frames, zoom_per_frame, path):
        img = Image.new("RGB", (self.image_width, self.image_heigth))
        images = []
        frame_counter = 1
        for i in range(n_frames):
            self.zoom = self.zoom / zoom_per_frame
            self.s2_x += self.s2_x * self.zoom if self.s2_x >= 0 else self.s2_x + self.s2_x * -self.zoom
            self.s1_y += self.s1_y * self.zoom if self.s1_y >= 0 else self.s1_y + self.s1_y * -self.zoom
            t0 = time.time()
            img_aux = Image.new("RGB", (self.image_width, self.image_heigth))
            img_aux = self.drawFractal(self.pixels, False)
            name = "frame" + str(frame_counter) + ".gif"
            img_aux.save(name)
            images.append(img_aux)
            t1 = time.time()
            print("Frame number ", frame_counter, " saved. Time used: ", str(t1 - t0))
            frame_counter += 1
        img.save(path, save_all = True, append_images = [i for i in images])





if __name__ == "__main__":
    image_path_png = "prueba.png"
    image_path = "gif_definitivo.gif"
    t0 = time.time()
    iterations = 1000
    image_width = 500
    image_heigth = 500

    image_zoom =  0.5
    x0 =  -0.16070135
    y0 =  1.0375665

    mandelbrot = Mandelbrot(image_width, image_heigth, iterations, image_path, image_zoom, x0, y0)

    def getInitialPoints(n):
        res = (0, 0, 0)
        for i in range(n):
            x = random.uniform(-2.0, 2.0)
            y = random.uniform(-2.0, 2.0)
            val = mandelbrot.mandelbrot(complex(x, y))
            candidate = (x, y, val)
            if candidate[2] > res[2]:
                res = candidate
        return res[0], res[1]

    #x0, y0 = getInitialPoints(300)
    print(x0, y0)
    #mandelbrot.__init__(image_width, image_heigth, iterations, image_path, image_zoom, x0, y0)

    #mandelbrot.drawFractal(mandelbrot.pixels)
    #mandelbrot.createGif(3, 100, "pruebagif.gif")
    #t1 = time.time()
    #print("Fractal generated in ",  t1 - t0, " seconds.")

    def createGif(x, y, n_frames, initial_zoom, zoom_per_frame, path):
        images = []
        zoom = initial_zoom
        for i in range(n_frames):
            t0 = time.time()
            mand = Mandelbrot(image_width, image_heigth, iterations, image_path, zoom, x0, y0)
            img = Image.new("RGBA", (image_width, image_heigth))
            img = mand.drawFractal(mandelbrot.pixels, False)
            name = "frame" + str(i + 1) + ".gif"
            images.append(img)
            t1 = time.time()
            print("Frame number ", str(i + 1), " generated. Time taken: ", str(t1 - t0))
            zoom -= 4 * zoom / zoom_per_frame
        img.save(path, save_all = True, append_images = [i for i in images], loop = 0, duration = 250)

    createGif(x0, y0, 60, image_zoom, 10, image_path)
    t1 = time.time()
    print("Gif created, time taken: ", str(t1 - t0))


