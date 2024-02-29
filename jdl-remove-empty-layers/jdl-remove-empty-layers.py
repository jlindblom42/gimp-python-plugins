#! /usr/bin/python

from gimpfu import *


def remove_empty_layers(image, drawable):
    pdb.gimp_progress_init("Starting...", None)
    # Align layers to top left
    image.undo_group_start()
    result_text = ''
    for layer in image.layers:
        if layer.visible:  # Check for layer visibility
            pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE, layer)
            non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)
            if not non_empty:
                progress = 'Removed empty layer: %s' % layer.name
                pdb.gimp_image_remove_layer(image, layer)
                pdb.gimp_progress_set_text(progress)
                result_text += '%s\n' % progress
    pdb.gimp_selection_none(image)
    if result_text == '':
        result_text = 'No empty layers to be removed.'
    pdb.gimp_message(result_text)
    image.undo_group_end()


register(
    "remove_empty_layers",
    "",
    "",
    "",
    "",
    "2024",
    "Remove Empty Layers",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    remove_empty_layers, menu="<Image>/Filters")
main()
