#! /usr/bin/python

from gimpfu import *


def align_layer_keep_non_empty(image, layer):
    pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE, layer)
    x0, y0 = pdb.gimp_drawable_offsets(layer)
    non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)
    if non_empty:
        pdb.gimp_layer_resize(layer, x2 - x1, y2 - y1, x0 - x1, y0 - y1)
        pdb.gimp_layer_set_offsets(layer, 0, 0)
    else:
        pdb.gimp_image_remove_layer(image, layer)


def crop_and_align_layers_to_content(image, drawable):
    pdb.gimp_image_undo_group_start(image)
    try:
        for layer in image.layers:
            align_layer_keep_non_empty(image, layer)
    finally:
        pdb.gimp_image_undo_group_end(image)


register(
    "crop_and_align_layers_to_content",
    "",
    "",
    "",
    "",
    "2024",
    "Layers Align and Crop to Content",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    crop_and_align_layers_to_content, menu="<Image>/Filters")
main()
