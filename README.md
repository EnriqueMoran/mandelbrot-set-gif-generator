# mandelbrot-gif-generator
Creates a gif of Mandelbrot set being zoomed to a specific given point. _PIL_ and _ctypes_ libraries needed.


## Usage 

Generate Mandelbrot set and save it in a new image.
To set image width and heigth, modify first and second arguments of mandelbrot instance.
To change the number of iterations, edit third argument of mandelbrot instance (700).


## How it works

As python libraries doesnt allow create a canvas and edit its pixels one by one, the program creates an image and edit each pixel based on scape time algorithm.
Afther generating the Mandelbrot set, the program saves it on the selected image.


## Version

**Version 0.1:** Mandelbrot set is generated on a png image. There are some errors at the bottom of image.

**Version 0.2:** Input image no longer needed.


## Output

![alt tag](mandelbrot_background_9300x9300.png)
