#! /usr/bin/python

from gimpfu import *


def group_visible_layers(image, drawable):
    # Start undo group
    pdb.gimp_undo_push_group_start(image)

    # Get all layers
    layers = image.layers

    # Find the index of the topmost visible layer
    top_visible_layer_index = None
    for i, layer in enumerate(layers):
        if layer.visible:
            top_visible_layer_index = i
            break  # Stop at the first visible layer found from the top

    # Check if a visible layer was found; otherwise, set default to 0
    if top_visible_layer_index is None:
        top_visible_layer_index = 0

    # Create a new layer group
    layer_group = pdb.gimp_layer_group_new(image)
    # Insert the layer group just above the topmost visible layer
    image.add_layer(layer_group, top_visible_layer_index)

    # Iterate over all layers, check if visible, and move to the group
    for layer in layers:
        if layer.visible and not pdb.gimp_item_is_group(layer):
            # Reparent the layer to the group
            pdb.gimp_image_reorder_item(image, layer, layer_group, 0)

    # End undo group
    pdb.gimp_undo_push_group_end(image)


register(
    "group_visible_layers",
    "",
    "",
    "",
    "",
    "2024",
    "Group Visible Layers",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    group_visible_layers, menu="<Image>/Filters")
main()
