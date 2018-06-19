import mandelbrot
import os
import sys
import time
import threading
from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk

class Main():

    __author__ : "EnriqueMoran"

    __version__ : "0.1"

    def __init__(self, window_width, window_height):
        self.window_width = window_width
        self.window_height = window_height
        self.icon_name = "\mandelbrot_icon.ico"
        self.sample_image = "\mandelbrot_set_sample.gif"
        self.x_coord = None
        self.y_coord = None
        self.zoom = None
        self.frames = None
        self.n_iter = None
        self.width_value = None
        self.height_value = None
        self.images = None
        self.img = None
        self.gif = []

    def initialize(self):
        root = Tk()

        default_x = StringVar(root, value = '0')
        default_y = StringVar(root, value = '0')
        default_zoom = StringVar(root, value = '1')
        default_frames = StringVar(root, value = '1')
        default_iterations = StringVar(root, value = '500')
        default_width = StringVar(root, value = '500')
        default_height = StringVar(root, value = '500')

        root.resizable(width=False, height=False)
        root.minsize(width = self.window_width, height = self.window_height)
        root.maxsize(width = self.window_width, height = self.window_height)

        root.title("Mandelbrot set gif generator")
        root.iconbitmap(os.path.abspath(sys.argv[0][:-16]) + self.icon_name)

        main_text = Label(root, text = "Zoom coordinates")
        main_text.config(font = ("DaunPenh", 13, "bold"))
        main_text.place(x = 485, y = 20)

        x_coordinate = Label(root, text = "X:")
        x_coordinate.config(font = ("DaunPenh", 10, "bold"))
        x_coordinate.place(x = 480, y = 70)
        x_entry = Entry(root, textvariable = default_x)
        x_entry.place(x = 505, y = 70)

        y_coordinate = Label(root, text = "Y:")
        y_coordinate.config(font = ("DaunPenh", 10, "bold"))
        y_coordinate.place(x = 480, y = 110)
        y_entry = Entry(root, textvariable = default_y)
        y_entry.place(x = 505, y = 110)

        zoom_text = Label(root, text = "Zoom:")
        zoom_text.config(font = ("DaunPenh", 10, "bold"))
        zoom_text.place(x = 480, y = 150)
        zoom_entry = Entry(root, width = 16, textvariable = default_zoom)
        zoom_entry.place(x = 530, y = 150)

        n_frames = Label(root, text = "N. frames:")
        n_frames.config(font = ("DaunPenh", 10, "bold"))
        n_frames.place(x = 480, y = 190)
        frames_entry = Entry(root, width = 12, textvariable = default_frames)
        frames_entry.place(x = 555, y = 190)

        iterations = Label(root, text = "Iterations:")
        iterations.config(font = ("DaunPenh", 10, "bold"))
        iterations.place(x = 480, y = 230)
        iterations_entry = Entry(root, width = 12, textvariable = default_iterations)
        iterations_entry.place(x = 555, y = 230)

        main_text = Label(root, text = "Image parameters")
        main_text.config(font = ("DaunPenh", 13, "bold"))
        main_text.place(x = 485, y = 285)

        width = Label(root, text = "Width:")
        width.config(font = ("DaunPenh", 10, "bold"))
        width.place(x = 480, y = 325)
        width_entry = Entry(root, width = 12, textvariable = default_width)
        width_entry.place(x = 535, y = 325)

        height = Label(root, text = "Height:")
        height.config(font = ("DaunPenh", 10, "bold"))
        height.place(x = 480, y = 365)
        height_entry = Entry(root, width = 12, textvariable = default_height)
        height_entry.place(x = 535, y = 365)


        def loadValues():
            self.x_coord = float(x_entry.get())
            self.y_coord = float(y_entry.get())
            self.zoom = float(zoom_entry.get())
            self.frames = int(frames_entry.get())
            self.n_iter = int(iterations_entry.get())
            self.width_value = int(width_entry.get())
            self.height_value = int(height_entry.get())


        def generateMandelbrot():
            generate_button['state'] = 'disabled'
            save_button['state'] = 'disabled'
            final_x.configure(text = "X: generating")
            final_y.configure(text = "Y: generating")
            final_zoom.configure(text = "Zoom: generating")
            mand = mandelbrot.Mandelbrot(self.width_value, self.height_value, "")
            self.images = mand.createGif(self.x_coord, self.y_coord, self.frames, self.zoom, 10, "", self.n_iter)
            gif_thread = threading.Thread(target = displayGif)
            gif_thread.start()
            generate_button['state'] = 'normal'
            save_button['state'] = 'normal'

            zoom = self.zoom
            for i in range(self.frames):
                if self.frames > 1:
                    zoom -= 4 * zoom / 10

            final_x.configure(text = "X: " + str(self.x_coord))
            final_y.configure(text = "Y: " + str(self.y_coord))
            final_zoom.configure(text = "Zoom: " + str(zoom))


        def displayGif():

            for frame in self.images:
                self.img = frame
                self.img = self.img.resize((int(self.window_width * 0.70), int(self.window_height * 0.85)), Image.ANTIALIAS)
                self.img = ImageTk.PhotoImage(self.img)
                self.gif.append(self.img)
            
            gif_image = Label(image = self.gif[0], borderwidth = 5, relief = "solid")
            while True:
                for i in self.gif:
                    gif_image.configure(image = i, borderwidth = 5, relief = "solid")
                    gif_image.place(x = 10, y = 25)
                    time.sleep(0.25)


        def run():
            loadValues()
            self.gif = []
            generate_thread = threading.Thread(target = generateMandelbrot)
            generate_thread.start()
            

        def save():
            
            save_path = filedialog.asksaveasfilename(initialdir = "/", title = "Select file", filetypes = (("gif files","*.gif"),("all files","*.*")))
            self.images[0].convert("RGB").save(save_path + ".gif", save_all = True, append_images = [i for i in self.images], loop = 0, duration = 250)


        generate_button = Button(root, text = "Generate image", command = run)
        generate_button.place(x = 480, y = 420)

        save_button = Button(root, text = "  Save  ", command = save)
        save_button.place(x = 590, y = 420)

        img = Image.open(os.path.abspath(sys.argv[0][:-16]) + self.sample_image)
        img = img.resize((int(self.window_width * 0.70), int(self.window_height * 0.85)), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)

        Label(image = img, borderwidth = 5, relief = "solid").place(x = 10, y = 25)

        final_x = Label(root, text = "X:")
        final_x.config(font = ("DaunPenh", 10, "bold"))
        final_x.place(x = 20, y = 470)

        final_y = Label(root, text = "Y:")
        final_y.config(font = ("DaunPenh", 10, "bold"))
        final_y.place(x = 260, y = 470)

        final_zoom = Label(root, text = "Zoom:")
        final_zoom.config(font = ("DaunPenh", 10, "bold"))
        final_zoom.place(x = 500, y = 470)

        root.mainloop()


if __name__ == "__main__":

    gui = Main(650, 500)
    gui.initialize()

