import cv2
import time
import math
import os
import threading
import PIL
import numpy as np
from PIL import Image, ImageTk
from multiprocessing import Pipe, Pool
from tkinter import filedialog
from tkinter import *



class Mandelbrot():

    __author__: "EnriqueMoran"

    __version__: "2.0"


    def __init__(self, n_iter, size, x=0, y=0, delta_x=0, delta_y=0, rotation=0, delta_rotation=0, zoom=1, zoom_ratio=0.9, send_frame_counter=None):
        self.iterations = n_iter    # number of iterations
        self.size = size    # width and height has the same value
        self.x = x    # initial coordinate (x, y)
        self.y = y
        self.delta_x = delta_x    # initial change in coordinates each frame
        self.delta_y = delta_y
        self.rotation = rotation
        self.delta_rotation = delta_rotation
        self.zoom = zoom
        self.zoom_ratio = zoom_ratio
        self.send_frame_counter = send_frame_counter
        self.values = np.zeros([self.size, self.size, 3])    # create matrix with 0's and 3 channels (RGB)
        radians = rotation * math.pi / 180
        self.pixel_x = 4 * zoom * math.cos(radians) / size
        self.pixel_y = 4 * zoom * math.sin(radians) / size


    def normalize(self, val, x=0, a=-2, b=2, min_val=0, max_val=None):
        if max_val == None:    # cant use max_val=self.size as argument default value
            max_val = self.size
        b = x + b * self.zoom    # x is the center of the interval, then normalize to [-2+x, 2+x]
        a = x + a * self.zoom
        return (b - a) * (val - min_val) / (max_val - min_val) + a


    def calc(self, c):    # OPTIMIZED FOR STANDARD MANDELBROT SET
        z_real = c.real
        z_imag = c.imag
        for i in range(self.iterations):
            real_sqr = z_real * z_real
            imag_sqr = z_imag * z_imag
            if real_sqr + imag_sqr > 4:    # splitting complex into real and imag components improves performance
                return i + 1 - math.log(math.log2(abs(complex(z_real, z_imag))))    # smooth coloring
            z_imag = 2 * z_real * z_imag + c.imag
            z_real = real_sqr - imag_sqr + c.real
        return self.iterations


    def run(self, ini_x, fin_x, ini_y, fin_y):
        offset = self.size / 2
        for i in range(ini_x, fin_x):
            for j in range(ini_y, fin_y):
                norm_i = (i - offset) * self.pixel_x + (j - offset) * self.pixel_y + self.x
                norm_j = -(i - offset) * self.pixel_y + (j - offset) * self.pixel_x + self.y
                c = complex(norm_i, norm_j)
                z = self.calc(c)
                if z == self.iterations:    # c is in Mandelbrot set
                    self.values[j, i] = (int(z), 255, 0)    # HSV values
                else:
                    self.values[j, i] = (int(z), 255, 255)
        return self.values


    def run_threads(self, pool):    # Parallelize calcs with 4 subprocesses
        p1 = pool.apply_async(self.run, (0, int(self.size / 2), 0, int(self.size / 2)))
        p2 = pool.apply_async(self.run, (0, int(self.size / 2), int(self.size / 2), self.size))
        p3 = pool.apply_async(self.run, (int(self.size / 2), self.size, 0, int(self.size / 2)))
        p4 = pool.apply_async(self.run, (int(self.size / 2), self.size, int(self.size / 2), self.size))

        r1 = (p1.get(timeout=1000))
        r2 = (p2.get(timeout=1000))
        r3 = (p3.get(timeout=1000))
        r4 = (p4.get(timeout=1000))

        for i in range(0, int(self.size / 2)):
            for j in range(0, int(self.size / 2)):
                self.values[i, j] = r1[i, j]

        for i in range(int(self.size / 2), self.size):
            for j in range(0, int(self.size)):
                self.values[i, j] = r2[i, j]

        for i in range(0, int(self.size / 2)):
            for j in range(int(self.size / 2), int(self.size)):
                self.values[i, j] = r3[i, j]

        for i in range(int(self.size / 2), self.size):
            for j in range(int(self.size / 2), self.size):
                self.values[i, j] = r4[i, j]
        return self.values


    def createGif(self, n_frames, path, save=False, pool=None):
        pool = pool or Pool(processes=4)
        frames = []
        for i in range(n_frames):
            frame = self.run_threads(pool).astype(np.uint8)
            frame = cv2.cvtColor(frame, cv2.COLOR_HSV2RGB)    # change frame from HSV to RGB
            img = PIL.Image.fromarray(frame, 'RGB')    # convert to PIL image format
            frames.append(img)
            if self.send_frame_counter:
                self.send_frame_counter.send(i + 1)

            self.zoom *= self.zoom_ratio    # zoom per frame
            self.x += self.delta_x
            self.y += self.delta_y
            self.delta_x *= self.zoom_ratio
            self.delta_y *= self.zoom_ratio
            self.rotation += self.delta_rotation
            radians = self.rotation * math.pi / 180
            self.pixel_x = 4 * self.zoom * math.cos(radians) / self.size
            self.pixel_y = 4 * self.zoom * math.sin(radians) / self.size

        frames += frames[-1:] * 5    # add 5 frames at last iteration
        return frames





class Gui():

    __author__: "EnriqueMoran"

    __version__: "1.0"


    def __init__(self):
        self.width = 710    # Window parameters
        self.height = 560
        self.icon_name = "mandelbrot_icon.ico"
        self.sample_image = "mandelbrot_set_sample.gif"

        self.x_coord = None    # Mandelbrot set parameters
        self.y_coord = None
        self.delta_x = None
        self.delta_y = None
        self.rotation = None
        self.delta_rotation = None
        self.zoom = None
        self.zoom_ratio = None
        self.frames = None
        self.iterations = None
        self.width_value = None
        self.height_value = None
        self.display = None
        self.images = None
        self.img = None
        self.gif = []
        self.stop_gif_thread = False
        self.gif_thread = None


    def initialize(self):
        root = Tk()

        default_x = StringVar(root, value='0')    # Default parameters
        default_y = StringVar(root, value='0')
        default_rotation = StringVar(root, value='0')
        default_zoom = StringVar(root, value='1')
        default_frames = StringVar(root, value='1')
        default_iterations = StringVar(root, value='500')
        default_size = StringVar(root, value='500')

        root.resizable(width=False, height=False)
        root.minsize(width=self.width, height=self.height)
        root.maxsize(width=self.width, height=self.height)

        root.title("Mandelbrot set gif generator")
        root.iconbitmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.icon_name))

        main_text = Label(root, text="Parameters")
        main_text.config(font=("DaunPenh", 17, "bold"))
        main_text.place(x=485, y=40)

        x_coordinate = Label(root, text="X:")
        x_coordinate.config(font=("DaunPenh", 10, "bold"))
        x_coordinate.place(x=485, y=100)
        x_entry = Entry(root, width=28, textvariable=default_x)
        x_entry.place(x=509, y=100)

        y_coordinate = Label(root, text="Y:")
        y_coordinate.config(font=("DaunPenh", 10, "bold"))
        y_coordinate.place(x=485, y=140)
        y_entry = Entry(root, width=28, textvariable=default_y)
        y_entry.place(x=509, y=140)

        zoom_text = Label(root, text="Initial zoom:")
        zoom_text.config(font=("DaunPenh", 10, "bold"))
        zoom_text.place(x=485, y=180)
        zoom_entry = Entry(root, width=17, textvariable=default_zoom)
        zoom_entry.place(x=573, y=180)

        rotation_text = Label(root, text="Rotation:")
        rotation_text.config(font=("DaunPenh", 10, "bold"))
        rotation_text.place(x=485, y=220)
        rotation_entry = Entry(root, width=17, textvariable=default_rotation)
        rotation_entry.place(x=573, y=220)

        n_frames = Label(root, text="N. frames:")
        n_frames.config(font=("DaunPenh", 10, "bold"))
        n_frames.place(x=485, y=260)
        frames_entry = Entry(root, width=19, textvariable=default_frames)
        frames_entry.place(x=562, y=260)

        iterations = Label(root, text="Iterations:")
        iterations.config(font=("DaunPenh", 10, "bold"))
        iterations.place(x=485, y=300)
        iterations_entry = Entry(root, width=19, textvariable=default_iterations)
        iterations_entry.place(x=560, y=300)

        size = Label(root, text="Size:")
        size.config(font=("DaunPenh", 10, "bold"))
        size.place(x=485, y=340)
        size_entry = Entry(root, width=22, textvariable=default_size)
        size_entry.place(x=540, y=340)


        def loadValues():
            x_coords = x_entry.get().split(' - ')
            if len(x_coords) == 2:
                self.x_coord = float(x_coords[0])
                final_x_coord = float(x_coords[1])
            else:
                self.x_coord = float(x_entry.get())
                final_x_coord = self.x_coord
            y_coords = y_entry.get().split(' - ')
            if len(y_coords) == 2:
                self.y_coord = float(y_coords[0])
                final_y_coord = float(y_coords[1])
            else:
                self.y_coord = float(y_entry.get())
                final_y_coord = self.y_coord
            zooms = zoom_entry.get().split(' - ')
            if len(zooms) == 2:
                self.zoom = float(zooms[0])
                frames = frames_entry.get()
                if frames == '':
                    self.frames = math.ceil((math.log(float(zooms[1])) - math.log(self.zoom)) / math.log(0.9)) + 1
                else:
                    self.frames = int(frames)
                self.zoom_ratio = math.exp((math.log(float(zooms[1])) - math.log(self.zoom)) / (self.frames - 1))
            else:
                self.zoom = float(zoom_entry.get())
                self.frames = int(frames_entry.get())
                self.zoom_ratio = 0.9
            if self.frames > 1:
                # 1 / (1 + zoom_ratio + zoom_ratio**2 + ...)
                delta_ratio = (self.zoom_ratio - 1) / (self.zoom_ratio ** (self.frames - 1) - 1)
                self.delta_x = (final_x_coord - self.x_coord) * delta_ratio
                self.delta_y = (final_y_coord - self.y_coord) * delta_ratio
            else:
                self.delta_x = 0
                self.delta_y = 0
            rotations = rotation_entry.get().split(' - ')
            if len(rotations) == 2:
                self.rotation = float(rotations[0])
                self.delta_rotation = (float(rotations[1]) - self.rotation) / (self.frames - 1)
            else:
                self.rotation = float(rotation_entry.get())
                self.delta_rotation = 0
            self.iterations = int(iterations_entry.get())
            self.size = int(size_entry.get())


        def captureOutput():
            status.configure(text="0 of " + str(self.frames) + " frames created")
            while True:
                    out = self.recv_frame_counter.recv()
                    status.configure(text=str(out) + " of " + str(self.frames) + " frames created")
                    if out == self.frames:
                            return None    # Kill thread
            return None


        def generateMandelbrot():
            generate_button['state'] = 'disabled'
            save_button['state'] = 'disabled'
            final_zoom.configure(text="Final zoom: generating")
            if self.gif_thread:
                self.stop_gif_thread = True
                self.gif_thread.join()

            mand = Mandelbrot(self.iterations, self.size, self.x_coord, self.y_coord, self.delta_x, self.delta_y, self.rotation, self.delta_rotation, self.zoom, self.zoom_ratio, self.send_frame_counter)
            self.images = mand.createGif(self.frames, "", pool=self.process_pool)

            self.stop_gif_thread = False
            self.gif_thread = threading.Thread(target=displayGif)
            self.gif_thread.start()

            generate_button['state'] = 'normal'
            save_button['state'] = 'normal'
            final_zoom.configure(text="Final zoom: " + str(mand.zoom))
            return None


        def displayGif():
            for frame in self.images:
                self.img = frame
                self.img = self.img.resize((455, 450))
                self.img = ImageTk.PhotoImage(self.img)
                self.gif.append(self.img)

            gif_image = Label(image=self.gif[0], borderwidth=5, relief="solid")

            while not self.stop_gif_thread:
                for i in self.gif:
                    gif_image.configure(image=i, borderwidth=5, relief="solid")
                    gif_image.place(x=10, y=25)
                    if self.stop_gif_thread:
                        break
                    time.sleep(0.1)    # slows gif display's speed


        def run():
            loadValues()
            self.recv_frame_counter, self.send_frame_counter = Pipe(False)
            self.send_frame_counter.send(0)
            self.gif = []
            generate_thread = threading.Thread(target=generateMandelbrot)
            capture_output= threading.Thread(target=captureOutput)
            capture_output.start()
            generate_thread.start()


        def save():
            save_path = filedialog.asksaveasfilename(initialdir="/", title="Select file", filetypes=(("gif files","*.gif"),("all files","*.*")))
            if save_path is not None:
                self.images[0].convert("RGB").save(save_path + ".gif", save_all=True, append_images=[i for i in self.images], loop=0, fps=20)


        self.process_pool = Pool(processes=4)
        generate_button = Button(root, text="Generate image", command=run)
        generate_button.place(x=490, y=385)

        save_button = Button(root, text="  Save image  ", command=save)
        save_button.place(x=610, y=385)

        img = PIL.Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.sample_image))
        img = img.resize((455, 450))
        img = ImageTk.PhotoImage(img)

        Label(image=img, borderwidth=5, relief="solid").place(x=10, y=25)

        final_zoom = Label(root, text="Final zoom:")
        final_zoom.config(font=("DaunPenh", 10, "bold"))
        final_zoom.place(x=25, y=505)

        status = Label(root, text="Status:")
        status.config(font=("System", 9, "bold"))
        status.place(x=480, y=430)

        status = Label(root, text="0 of 1 frames created")
        status.config(font=("System", 9))
        status.place(x=530, y=430)

        root.mainloop()





if __name__ == "__main__":

    window = Gui()
    window.initialize()
