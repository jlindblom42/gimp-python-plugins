#! /usr/bin/python

from gimpfu import *
import random


def shuffle_layers(image, drawable):
    # Start undo group
    pdb.gimp_undo_push_group_start(image)

    # Get all layers
    layers = image.layers

    # Generate a random order
    random_order = list(range(len(layers)))
    random.shuffle(random_order)

    # Rearrange layers according to the random order
    for i, layer_index in enumerate(random_order):
        layer = layers[layer_index]
        # Move layer to its new position
        # image.reorder_item(layer, None, i)
        pdb.gimp_image_reorder_item(image, layer, None, i)

    # End undo group
    pdb.gimp_undo_push_group_end(image)

    # Update the image
    gimp.displays_flush()


register(
    "shuffle_layers",
    "",
    "",
    "",
    "",
    "2024",
    "Shuffle Layers",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    shuffle_layers, menu="<Image>/Filters")

main()
