#! /usr/bin/python

from gimpfu import *


def remove_background(image, drawable):
    pdb.gimp_undo_push_group_start(image)

    try:
        # Get the current background color from GIMP's context
        background_color = pdb.gimp_context_get_background()

        # Iterate over all layers
        for layer in [l for l in image.layers if pdb.gimp_item_get_visible(l)]:
            # Temporarily add an alpha channel to ensure transparency is possible
            if not pdb.gimp_drawable_has_alpha(layer):
                pdb.gimp_layer_add_alpha(layer)

            # Select the background color
            pdb.gimp_by_color_select(layer, background_color, 0, CHANNEL_OP_REPLACE, False, False, 0, False)

            # Check if any pixels were selected
            non_empty_selection = pdb.gimp_selection_bounds(image)[0]

            if non_empty_selection:
                # Clear the selection, making it transparent
                pdb.gimp_edit_clear(layer)

            # Remove any selection
            pdb.gimp_selection_none(image)

    finally:
        pdb.gimp_undo_push_group_end(image)

    # Update the display
    gimp.displays_flush()


register(
    "remove_background",
    "",
    "",
    "",
    "",
    "2024",
    "Remove BG",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    remove_background, menu="<Image>/Filters")
main()
