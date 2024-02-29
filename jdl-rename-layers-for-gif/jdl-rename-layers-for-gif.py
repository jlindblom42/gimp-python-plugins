#! /usr/bin/python

from gimpfu import *


def rename_layers_for_gif(img, drawable):
    pdb.gimp_progress_init("Starting...", None)
    img.undo_group_start()
    index = 1
    for layer in img.layers:
        if layer.visible:  # Check for layer visibility
            layer.name = str(index) + " (replace)"
            pdb.gimp_progress_set_text('Renamed layer: %s' % layer.name)
            index += 1
    img.undo_group_end()


register(
    "rename_layers_for_gif",
    "",
    "",
    "",
    "",
    "2024",
    "Rename Layers for Gif",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    rename_layers_for_gif, menu="<Image>/Filters")
main()
