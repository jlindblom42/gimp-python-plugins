#! /usr/bin/python

from gimpfu import *


def duplicate_visible_layers(image, drawable, mirrored, num_iterations):
    pdb.gimp_undo_push_group_start(image)

    # Reverse the layer list to keep the original order when inserting
    layers = list(image.layers)

    sequence_start = None
    sequence_end = None

    for layer_index in range(len(layers)):
        prev_layer = None
        curr_layer = layers[layer_index]
        next_layer = None

        if layer_index > 0:
            prev_layer = layers[layer_index - 1]

        if layer_index < (len(layers) - 1):
            next_layer = layers[layer_index + 1]

        if curr_layer.visible:
            if prev_layer is None or not prev_layer.visible:
                sequence_start = layer_index

            if next_layer is None or not next_layer.visible:
                sequence_end = layer_index + 1

        if sequence_start is not None and sequence_end is not None:
            for iteration in range(num_iterations):
                sequence_layers = []
                for sequence_index in range(sequence_start, sequence_end):
                    # For each sequence index, extract the corresponding layer.
                    sequence_layers.append(layers[sequence_index])

                # If mirrored is True, reverse the order for every other iteration.
                # Number of iterations being odd or even influences the starting point.
                if mirrored and iteration % 2 == num_iterations % 2:
                    sequence_layers.reverse()

                for sequence_layer in sequence_layers:
                    # Duplicate the layer and add it just below the end of the sequence.
                    dup_layer = pdb.gimp_layer_copy(sequence_layer, True)
                    image.add_layer(dup_layer, image.layers.index(sequence_layer))

                    if next_layer is not None:
                        new_index = image.layers.index(next_layer) - 1
                    else:
                        new_index = image.layers.index(curr_layer)

                    pdb.gimp_image_reorder_item(image, dup_layer, None, new_index)

            sequence_start = None
            sequence_end = None

    pdb.gimp_undo_push_group_end(image)
    gimp.displays_flush()


register(
    "duplicate_visible_layers",
    "",
    "",
    "",
    "",
    "2024",
    "Duplicate Visible Layers",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_BOOL, "mirrored", "Mirrored?", False),
        (PF_INT, "num_iterations", "# Iterations?", 1),
    ],
    [],
    duplicate_visible_layers, menu="<Image>/Filters")

main()
