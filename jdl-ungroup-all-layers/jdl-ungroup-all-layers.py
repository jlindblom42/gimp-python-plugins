#! /usr/bin/python

from gimpfu import *


def ungroup_layer(image, layer, parent, insert_after):
    """Ungroups layers directly below their parent group while maintaining order."""
    if pdb.gimp_item_is_group(layer):
        # Start from the last child to keep the order correct after moving them out of the group
        children = reversed(layer.children)
        # Track the insert position based on the last moved child
        insert_after = layer
        for child in children:
            # Recursively ungroup children, adjusting insert_after each time
            insert_after = ungroup_layer(image, child, layer, insert_after)
        # Delete the now-empty group if it's not the top level
        if parent is not None:
            pdb.gimp_image_remove_layer(image, layer)
            return insert_after  # Return the last layer inserted after for the parent's context
    elif parent is not None:
        # Move the layer directly below the insert_after layer
        target_index = pdb.gimp_image_get_item_position(image, insert_after) + 1
        pdb.gimp_image_reorder_item(image, layer, None, target_index)
        return layer  # Return this layer as the new insert_after for subsequent siblings
    return insert_after  # For top-level or non-group items, propagate the insert position unchanged


def ungroup_all_layers(image, drawable):
    """Ungroups all layers in the image, maintaining their order below their parent groups."""
    pdb.gimp_image_undo_group_start(image)
    try:
        # Use None for parent and insert_after initially
        for layer in list(image.layers):
            ungroup_layer(image, layer, None, None)
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
    "Ungroup All Layers",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    ungroup_all_layers, menu="<Image>/Filters")

main()
