#! /usr/bin/python

from gimpfu import *


def ungroup_layer(image, layer, parent):
    if pdb.gimp_item_is_group(layer):
        for child in reversed(layer.children):
            ungroup_layer(image, child, layer)
    elif parent is not None:
        pdb.gimp_image_reorder_item(image, layer, None, 0)


def ungroup_all_layers(image, drawable):
    pdb.gimp_image_undo_group_start(image)
    try:
        for layer in list(image.layers):
            ungroup_layer(image, layer, None)
    finally:
        pdb.gimp_image_undo_group_end(image)
    gimp.displays_flush()


register(
    "ungroup_all_layers",
    "",
    "",
    "",
    "",
    "2024",
    "Ungroup Visible Layers",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    ungroup_all_layers, menu="<Image>/Filters")
main()
