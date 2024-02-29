#! /usr/bin/python

from gimpfu import *


def remove_invisible_layers(image, drawable):
    image.undo_group_start()
    pdb.gimp_progress_init("Starting...", None)
    result_text = ''
    for layer in image.layers:
        if not layer.visible:  # Check for layer visibility
            progress = 'Removed invisible layer: %s' % layer.name
            pdb.gimp_image_remove_layer(image, layer)
            pdb.gimp_progress_set_text(progress)
            result_text += '%s\n' % progress

    if result_text == '':
        result_text = 'No invisible layers to be removed.'
    pdb.gimp_message(result_text)
    image.undo_group_end()


register(
    "remove_invisible_layers",
    "",
    "",
    "",
    "",
    "2024",
    "Remove Invisible Layers",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    remove_invisible_layers, menu="<Image>/Filters")
main()
