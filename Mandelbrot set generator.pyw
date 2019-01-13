import cv2
import time
import math
import os
import threading
import PIL
import io
import numpy as np
from PIL import Image, ImageTk
from multiprocessing import Pool
from tkinter import filedialog
from contextlib import redirect_stdout
from tkinter import *



class Mandelbrot():

    __author__: "EnriqueMoran"

    __version__: "2.0"


    def __init__(self, n_iter, size, x=0, y=0, zoom=1):
        self.iterations = n_iter    # number of iterations
        self.size = size    # width and height has the same value
        self.x = x    # initial coordinate (x, y)
        self.y = y
        self.zoom = zoom
        self.values = np.zeros([self.size, self.size, 3])    # create matrix with 0's and 3 channels (RGB)
        self.norm_width = [self.normalize(x, self.x) for x in range(size)]
        self.norm_height = [self.normalize(y, self.y) for y in range(size)]


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
        for i in range(ini_x, fin_x):
            for j in range(ini_y, fin_y): 
                norm_i = self.norm_width[i]
                norm_j = self.norm_height[-j]
                c = complex(norm_i, norm_j)
                z = self.calc(c)
                if z == self.iterations:    # c is in Mandelbrot set
                    self.values[j, i] = (int(z), 255, 0)    # HSV values
                else:
                    self.values[j, i] = (int(z), 255, 255)
        return self.values


    def run_threads(self):    # Parallelize calcs with 4 subprocesses
        with Pool(processes=4) as pool:
            p1 = pool.apply_async(self.run, (0, int(self.size / 2), 0, int(self.size / 2)))
            p2 = pool.apply_async(self.run, (0, int(self.size / 2), int(self.size / 2), self.size))
            p3 = pool.apply_async(self.run, (int(self.size / 2), self.size, 0, int(self.size / 2)))
            p4 = pool.apply_async(self.run, (int(self.size / 2), self.size, int(self.size / 2), self.size))
            
            r1 = (p1.get(timeout=1000))
            r2 = (p2.get(timeout=1000))
            r3 = (p3.get(timeout=1000))
            r4 = (p4.get(timeout=1000))

            pool.close()
            pool.join()

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


    def createGif(self, n_frames, path, save=False):
        frames = []
        for i in range(n_frames):
            frame = self.run_threads().astype(np.uint8)
            frame = cv2.cvtColor(frame, cv2.COLOR_HSV2RGB)    # change frame from HSV to RGB
            img = PIL.Image.fromarray(frame, 'RGB')    # convert to PIL image format
            frames.append(img)
            print(str(i + 1))

            self.zoom -= 0.1 * self.zoom    # zoom per frame
            self.norm_width = [self.normalize(x, self.x) for x in range(self.size)]    # actualize x and y coordinates
            self.norm_height = [self.normalize(y, self.y) for y in range(self.size)]   # according to new zoom

        frames += frames[-1:] * 5    # add 5 frames at last iteration
        return frames





class Gui():

    __author__: "EnriqueMoran"

    __version__: "1.0"


    def __init__(self):
        self.width = 710    # Window parameters
        self.height = 560
        self.icon_name = "\\mandelbrot_icon.ico"
        self.sample_image = "\\mandelbrot_set_sample.gif" 

        self.x_coord = None    # Mandelbrot set parameters
        self.y_coord = None
        self.zoom = None
        self.frames = None
        self.iterations = None
        self.width_value = None
        self.height_value = None
        self.display = None
        self.images = None
        self.img = None
        self.gif = []


    def initialize(self):
        root = Tk()

        default_x = StringVar(root, value='0')    # Default parameters
        default_y = StringVar(root, value='0')
        default_zoom = StringVar(root, value='1')
        default_frames = StringVar(root, value='1')
        default_iterations = StringVar(root, value='500')
        default_size = StringVar(root, value='500')

        root.resizable(width=False, height=False)
        root.minsize(width=self.width, height=self.height)
        root.maxsize(width=self.width, height=self.height)

        root.title("Mandelbrot set gif generator")
        root.iconbitmap(os.path.dirname(os.path.abspath(__file__)) + self.icon_name)

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

        n_frames = Label(root, text="N. frames:")
        n_frames.config(font=("DaunPenh", 10, "bold"))
        n_frames.place(x=485, y=220)
        frames_entry = Entry(root, width=19, textvariable=default_frames)
        frames_entry.place(x=562, y=220)

        iterations = Label(root, text="Iterations:")
        iterations.config(font=("DaunPenh", 10, "bold"))
        iterations.place(x=485, y=260)
        iterations_entry = Entry(root, width=19, textvariable=default_iterations)
        iterations_entry.place(x=560, y=260)

        size = Label(root, text="Size:")
        size.config(font=("DaunPenh", 10, "bold"))
        size.place(x=485, y=300)
        size_entry = Entry(root, width=22, textvariable=default_size)
        size_entry.place(x=540, y=300)


        def loadValues():
            self.x_coord = float(x_entry.get())
            self.y_coord = float(y_entry.get())
            self.zoom = float(zoom_entry.get())
            self.frames = int(frames_entry.get())
            self.iterations = int(iterations_entry.get())
            self.size = int(size_entry.get())


        def captureOutput():
            f = io.StringIO()    # Capture print output
            status.configure(text="0 of " + str(self.frames) + " frames created")
            while True:
                with redirect_stdout(f):
                    out = f.getvalue()
                    status.configure(text=out.strip()[-1:] + " of " + str(self.frames) + " frames created")   # TO FIX
                    time.sleep(0.4)    # Memory error
                    try:
                        if int(out.strip()[-1:]) == self.frames:
                            return None    # Kill thread
                    except:
                        pass
            return None


        def generateMandelbrot():
            generate_button['state'] = 'disabled'
            save_button['state'] = 'disabled'
            final_zoom.configure(text="Final zoom: generating")

            mand = Mandelbrot(self.iterations, self.size, self.x_coord, self.y_coord, self.zoom)
            self.images = mand.createGif(self.frames, "")

            gif_thread = threading.Thread(target=displayGif)
            gif_thread.start()

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

            while True:
                for i in self.gif:
                    gif_image.configure(image=i, borderwidth=5, relief="solid")
                    gif_image.place(x=10, y=25)
                    time.sleep(0.1)    # slows gif display's speed


        def run():
            loadValues()
            status.configure(text="0 of " + str(self.frames) + " frames created.")
            self.gif = []
            generate_thread = threading.Thread(target=generateMandelbrot)
            capture_output= threading.Thread(target=captureOutput)
            capture_output.start()
            generate_thread.start()


        def save():
            save_path = filedialog.asksaveasfilename(initialdir="/", title="Select file", filetypes=(("gif files","*.gif"),("all files","*.*")))
            self.images[0].convert("RGB").save(save_path + ".gif", save_all=True, append_images=[i for i in self.images], loop=0, fps=20)


        generate_button = Button(root, text="Generate image", command=run)
        generate_button.place(x=490, y=365)

        save_button = Button(root, text="  Save image  ", command=save)
        save_button.place(x=610, y=365)

        img = PIL.Image.open(os.path.dirname(os.path.abspath(__file__)) + self.sample_image)
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