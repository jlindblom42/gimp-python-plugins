#!/usr/bin/env python

from gimpfu import *


def gif_background_merge(image, drawable, num_scenes=3, num_frames=5):
    pdb.gimp_undo_push_group_start(image)

    # Start with all layers hidden
    for layer in image.layers:
        layer.visible = False

    unmerged_layers = image.layers

    for frame_index in range(num_frames):
        for scene_index in range(num_scenes):
            scene_frame_index = (scene_index * num_frames + frame_index)
            pdb.gimp_message('%s * %s + %s = %s' % (scene_index, num_frames, frame_index, scene_frame_index))
            frame = unmerged_layers[scene_frame_index]
            frame.visible = True

        merged_layer = pdb.gimp_image_merge_visible_layers(image, CLIP_TO_IMAGE)
        merged_layer.visible = False
        merged_layer.name = 'Frame %d' % frame_index

    # Reveal all layers again
    for layer in image.layers:
        layer.visible = True

    # Get the bottom layer
    bottom_layer = image.layers[-1]

    # Get the list of layers excluding the bottom one
    layers_excluding_bottom = image.layers[:-1]

    # Reverse the list to start from the top
    for layer in reversed(layers_excluding_bottom):
        duplicate_layer = pdb.gimp_layer_copy(bottom_layer, True)
        image.add_layer(duplicate_layer, len(image.layers))

        # Move the duplicate below the current layer
        pdb.gimp_image_reorder_item(image, duplicate_layer, None, image.layers.index(layer) + 1)

        # Merge down the current layer into the duplicate
        pdb.gimp_image_merge_down(image, layer, EXPAND_AS_NECESSARY)

    # Remove bottom layer
    image.remove_layer(bottom_layer)

    pdb.gimp_undo_push_group_end(image)


register(
    "gif_background_merge",
    "",
    "",
    "",
    "",
    "2024",
    "Gif Background Merge",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_INT, "number", "Number of scenes", 3),
        (PF_INT, "number", "Number of frames", 5),
    ],
    [],
    gif_background_merge, menu="<Image>/Filters")
main()
