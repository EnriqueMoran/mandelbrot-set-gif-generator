# mandelbrot-gif-generator
Creates a gif of Mandelbrot set being zoomed to a specific given point. _PIL_ and _ctypes_ libraries needed.

![alt tag](/readme_images/gui_example.gif)


## GUI Usage 

All you have to set is _x_ and _y_ coordinates, the initial _zoom_ (if value is 1, the first frame will be the whole mMndelbrot set) and the _number of frames_.

If you want larger images, just change _Width_ and _Height_ values (setting the same value for both is highly recommended), for higher definitions at deep zooms, change _Iterarions_ value.

Once all parametes has been set, press *Generate image* and after the image (or gif) is shown, you can *Save* it. 
For single image set _N.Frames_ to 1.

For using the GUI version, run either _exe_ version or _.py_


## Library Usage 

First step is creating a _mandelbrot object_ instance. The basic arguments are: _image_width_, _image_heigth_ and _image_path_. With these arguments the mandelbrot set generated will be centered at (0, 0) with no zoom; the default value of escape time algorithm iterations is 100 (for larger images this value
must be higher).

Once the object is instanciated, call _createGif_ method. Necessary arguments are: _x coordinate_, _y coordinate_, _number of frames_, _initial zoom_, _zoom per frame_, _path_ and _iterations_.

There is an extra argument that let the algorithm save every frame of the gif (True or False).

x and y coordinates is the coordinate where the algorithm will zoom into, _number of frames_ is how many frames will the gif have.
_initial zoom_ is where will we start zooming (zoom will be lowered by 4 times zoom / zoom per frame on each iteration).

```
image_path = "mandelbrot_test.gif"   # Remember to use absolute path, otherwise the image will be create in the same directory as the script is at (image must be .gif)
iterations = 1000
image_width = 2500
image_heigth = 2500
n_frames = 25
frames_per_zoom = 10
zoom = 1
x_coordinate = 0
y_coordinate = 0    # We will zoom into (0, 0)

mandelbrot = Mandelbrot(image_width, image_heigth, image_path)
mandelbrot.createGif(x0, y0, n_frames, image_zoom, frames_per_zoom, image_path, iterations)    # This will save a 2500x2500 gif image with 25 frames

```

If we want to generate just a single image, change number of frames argument to 1:

```
n_frames = 1
mandelbrot.createGif(x0, y0, n_frames, image_zoom, frames_per_zoom, image_path, iterations)
```

If we want to save every single frame generated, add True argument to _createGif_ method:

```
mandelbrot.createGif(x0, y0, n_frames, image_zoom, frames_per_zoom, image_path, iterations, True)
```

## How it works

As python libraries doesnt allow create a canvas and edit its pixels one by one, the program creates an image and edit each pixel based on escape time algorithm.
Mandelbrot set will be zoomed on each iteration, the final result will be saved as a gif image.


## Version

**Version 0.1:** Mandelbrot set is generated on a png image. There are some errors at the bottom of image.

**Version 0.2:** Input image no longer needed.

**Version 0.3:** Can create gif, zoom and coordinate bugs fixed.

**Version 0.35:** Gif creation improved, methods usage now is easier.

**Version 0.36:** Mandelbrot set generation fixed.

**Version 1.0:** GUI and EXE version added!


## Output

![alt tag](readme_images/mandelbrot9300x9300.png)


![alt tag](readme_images/example_gif.gif)
