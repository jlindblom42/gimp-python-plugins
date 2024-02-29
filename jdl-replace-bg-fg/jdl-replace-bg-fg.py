#! /usr/bin/python

from gimpfu import *


def replace_background_with_foreground(image, drawable):
    pdb.gimp_progress_init("Starting...", None)
    image.undo_group_start()
    layers = image.layers
    pdb.gimp_context_set_antialias(FALSE)
    pdb.gimp_context_set_sample_threshold_int(10)
    pdb.gimp_context_set_sample_criterion(SELECT_CRITERION_COMPOSITE)
    pdb.gimp_context_set_sample_transparent(TRUE)
    color_to_replace = pdb.gimp_context_get_background()
    index = 0
    for layer in layers:
        if layer.visible:
            index += 1
            pdb.gimp_progress_set_text("Replace bg with fg for layer #%d" % index)
            pdb.gimp_image_select_color(image, CHANNEL_OP_REPLACE, layer, color_to_replace)
            non_empty_selection = pdb.gimp_selection_bounds(image)[0]
            if non_empty_selection:
                pdb.gimp_edit_bucket_fill(layer, FG_BUCKET_FILL, NORMAL_MODE, 100., 0., FALSE, 0., 0.)
    image.undo_group_end()


register(
    "replace_background_with_foreground",
    "",
    "",
    "",
    "",
    "2024",
    "Replace BG With FG",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    replace_background_with_foreground, menu="<Image>/Filters")
main()
