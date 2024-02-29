#! /usr/bin/python

from gimpfu import *
import gtk
import gimpui
import gobject

def layers_to_image_size(image, drawable):
    image.undo_group_start()
    layers = image.layers
    for layer in layers:
        pdb.gimp_layer_resize_to_image_size(layer)
    image.undo_group_end()

register(
          "layers_to_image_size",
          "",
          "",
          "",
          "",
          "2024",
          "Layers to Image Size",
          "*",
          [
              (PF_IMAGE, "image", "Input image", None),
              (PF_DRAWABLE, "drawable", "Input drawable", None),
          ],
          [],
          layers_to_image_size, menu="<Image>/Filters")
main()