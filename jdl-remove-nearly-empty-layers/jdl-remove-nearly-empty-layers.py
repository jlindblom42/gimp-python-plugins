#! /usr/bin/python

from gimpfu import *


def count_non_transparent_pixels(layer):
    # Get the pixel region for the entire layer
    pixel_rgn = layer.get_pixel_rgn(0, 0, layer.width, layer.height, False, False)
    pixels = pixel_rgn[:, :]  # Access all pixels at once for efficiency

    # Count non-transparent pixels (assuming RGBA)
    non_transparent_count = sum(pixels[i + 3] != '\x00' for i in range(0, len(pixels), 4))

    return non_transparent_count


def remove_nearly_empty_layers(image, threshold_percentage, output_only):
    pdb.gimp_image_undo_group_start(image)
    pdb.gimp_progress_init("Starting...", None)
    result_text = ''
    for layer in image.layers:
        non_transparent_pixels = count_non_transparent_pixels(layer)
        total_pixels = layer.width * layer.height
        non_transparent_percentage = (float(non_transparent_pixels) / total_pixels) * 100

        if non_transparent_percentage < threshold_percentage:
            progress = 'X (%d%% < %d%%) Removed layer: %s' % (
                non_transparent_percentage, threshold_percentage, layer.name)
            if not output_only:
                pdb.gimp_image_remove_layer(image, layer)
            result_text += '%s\n' % progress
        else:
            progress = '   (%d%% > %d%%) Ignored layer: %s' % (
                non_transparent_percentage, threshold_percentage, layer.name)
            result_text += '%s\n' % progress

    if result_text == '':
        result_text = 'No layers empty enough to be removed.'
    pdb.gimp_message(result_text)
    pdb.gimp_image_undo_group_end(image)
    pdb.gimp_displays_flush()


register(
    "remove_nearly_empty_layers",
    "",
    "",
    "",
    "",
    "2024",
    "Remove Nearly Empty Layers",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_SLIDER, "threshold_percentage", "Non-transparent pixel percentage threshold", 10, (0, 100, 1)),
        (PF_BOOL, "output_only", "Output only?", 0),
    ],
    [],
    remove_nearly_empty_layers, menu="<Image>/Filters")
main()
