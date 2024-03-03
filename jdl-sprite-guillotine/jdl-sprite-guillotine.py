#! /usr/bin/python

import gimpui
import gtk
from gimpfu import *
import time

HORIZONTAL = 0
VERTICAL = 1
BOTH = 2

TOP = 0
MIDDLE = 1
BOTTOM = 2


# For debugging
def print_args(args):
    output = ''
    for k, v in args:
        output += '%s: %s\n' % (k, v)
    pdb.gimp_message(output)


def set_text(progress_bar_text):
    progress_bar.set_text(progress_bar_text)
    gtk.main_iteration_do(False)


def elapsed_message(message, prev_elapsed_time_sec=0):
    total_time_sec = time.time() - start_time_sec
    elapsed_time_sec = total_time_sec - prev_elapsed_time_sec
    pdb.gimp_message("Completed %s\n[%.2f sec elapsed]\n[%.2f sec total]" % (message, elapsed_time_sec, total_time_sec))
    return total_time_sec


def guide_clear(image):
    while True:
        guide_id = pdb.gimp_image_find_next_guide(image, 0)
        if guide_id == 0:
            break
        pdb.gimp_image_delete_guide(image, guide_id)


has_no_guides_map = {}


def guides_for_transparent(image, layer, loop_index, initial_direction):
    if layer.name in has_no_guides_map:
        return

    has_no_guides = True
    initial_loop = loop_index == 1
    allow_vertical = not initial_loop or initial_direction != HORIZONTAL
    allow_horizontal = not initial_loop or initial_direction != VERTICAL
    guide_clear(image)
    num_cols = layer.width
    num_rows = layer.height

    transparency_memo = {}

    layer_pixel_rgn = layer.get_pixel_rgn(0, 0, layer.width, layer.height)
    layer_pixels = layer_pixel_rgn[:, :]  # Grab all pixels at once for efficiency

    def is_transparent(col_index, row_index):
        key = (col_index, row_index)
        if key not in transparency_memo:
            # Assuming RGBA for each pixel
            idx = (row_index * num_cols + col_index) * 4
            # Check if alpha byte signifies transparency
            transparency_memo[key] = layer_pixels[idx + 3] == '\x00'

        return transparency_memo[key]

    if allow_horizontal:
        first_guide = True
        for curr_row_index in range(num_rows):
            curr_row_transparent = True
            for curr_col_index in range(num_cols):
                if not is_transparent(curr_col_index, curr_row_index):
                    curr_row_transparent = False
                    break

            if curr_row_index == 0 and not curr_row_transparent:
                first_guide = False

            next_row_transparent = True
            next_row_index = curr_row_index + 1
            for curr_col_index in range(num_cols):
                if next_row_index < num_rows and not is_transparent(curr_col_index, next_row_index):
                    next_row_transparent = False
                    break

            if curr_row_transparent and next_row_transparent:
                continue

            if not curr_row_transparent and next_row_transparent:
                continue

            next_row_connected = False
            if not curr_row_transparent and not next_row_transparent:
                for curr_col_index in range(num_cols):
                    if not is_transparent(curr_col_index, curr_row_index):
                        next_col_index = curr_col_index + 1
                        prev_col_index = curr_col_index - 1
                        next_row_connected = (
                                not is_transparent(curr_col_index, next_row_index)
                                or (next_col_index < num_cols
                                    and not is_transparent(next_col_index, next_row_index))
                                or (prev_col_index > 0
                                    and not is_transparent(prev_col_index, next_row_index)))

                        if next_row_connected:
                            break

            if not curr_row_transparent and not next_row_transparent and next_row_connected:
                continue

            if first_guide:
                first_guide = False
                continue

            pdb.gimp_image_add_hguide(image, next_row_index)
            has_no_guides = False

    if allow_vertical:
        first_guide = True
        for curr_col_index in range(num_cols):
            curr_col_transparent = True
            for curr_row_index in range(num_rows):
                if not is_transparent(curr_col_index, curr_row_index):
                    curr_col_transparent = False
                    break

            if curr_col_index == 0 and not curr_col_transparent:
                first_guide = False

            next_col_transparent = True
            next_col_index = curr_col_index + 1
            for curr_row_index in range(num_rows):
                if next_col_index < num_cols and not is_transparent(next_col_index, curr_row_index):
                    next_col_transparent = False
                    break

            if curr_col_transparent and next_col_transparent:
                continue

            if not curr_col_transparent and next_col_transparent:
                continue

            next_col_connected = False
            if not curr_col_transparent and not next_col_transparent:
                for curr_row_index in range(num_rows):
                    if not is_transparent(curr_col_index, curr_row_index):
                        next_row_index = curr_row_index + 1
                        prev_row_index = curr_row_index - 1
                        next_col_connected = (
                                not is_transparent(next_col_index, curr_row_index)
                                or (next_row_index < num_rows
                                    and not is_transparent(next_col_index, next_row_index))
                                or (prev_row_index > 0
                                    and not is_transparent(next_col_index, prev_row_index)))

                        if next_col_connected:
                            break

            if not curr_col_transparent and not next_col_transparent and next_col_connected:
                continue

            if first_guide:
                first_guide = False
                continue

            pdb.gimp_image_add_vguide(image, next_col_index)
            has_no_guides = False

    if has_no_guides:
        has_no_guides_map[layer.name] = True


def get_guides(image):
    guides = [[], []]  # ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1)
    gid = 0
    while True:
        gid = image.find_next_guide(gid)
        if not gid:
            break
        guides[image.get_guide_orientation(gid)].append(image.get_guide_position(gid))
    map(lambda x: x.sort(), guides)
    return guides


# Yield successive start positions and lengths
def iterate_segments(positions):
    for i in range(len(positions) - 1):
        yield positions[i], positions[i + 1] - positions[i]


# Yields successive squares
def iterate_squares(image, guides):
    hguides = [0] + guides[0] + [image.height]
    vguides = [0] + guides[1] + [image.width]
    for y, h in iterate_segments(hguides):
        for x, w in iterate_segments(vguides):
            yield x, y, w, h


# Intersection of two rectangles
def intersect(x1, y1, w1, h1, x2, y2, w2, h2):
    x1l, x1r, y1t, y1b = x1, x1 + w1, y1, y1 + h1
    x2l, x2r, y2t, y2b = x2, x2 + w2, y2, y2 + h2
    il = max(x1l, x2l)  # left side of intersection
    ir = min(x1r, x2r)  # right side
    it = max(y1t, y2t)  # top (Gimp coordinates!)
    ib = min(y1b, y2b)  # bottom
    if ir <= il or ib <= it:  # right must be right of left and bottom should be below top
        return None
    return il, it, ir - il, ib - it


def create_new_layer(image, layer, x, y, w, h):
    lx, ly = layer.offsets[0], layer.offsets[1]
    intersection = intersect(x, y, w, h, lx, ly, layer.width, layer.height)
    if intersection is None:
        return None  # no intersection
    new = layer.copy()
    image.add_layer(new, 0)
    new.name = "%s @ (%d,%d)" % (layer.name, x, y)
    ix, iy, iw, ih = intersection
    new.resize(iw, ih, lx - ix, ly - iy)
    return new


def guillotine_layer(image, layer, loop_text):
    set_text('%s Cutting squares...' % loop_text)
    for x, y, w, h in iterate_squares(image, get_guides(image)):
        new_layer = create_new_layer(image, layer, x, y, w, h)
        if new_layer is not None:
            align_layer_keep_non_empty(image, new_layer)
    guide_clear(image)
    pdb.gimp_image_remove_layer(image, layer)


def center_and_rename_layers(image, remove_bg_color, vertical_align):
    color_to_remove = None
    if remove_bg_color:
        pdb.gimp_context_set_antialias(FALSE)
        pdb.gimp_context_set_sample_threshold_int(0)
        pdb.gimp_context_set_sample_criterion(SELECT_CRITERION_COMPOSITE)
        pdb.gimp_context_set_sample_transparent(TRUE)
        color_to_remove = pdb.gimp_context_get_background()

    index = 1
    for layer in image.layers:
        center_and_rename_layer(image, index, layer, color_to_remove, vertical_align)
        index += 1


def position_layer(image, layer, vertical_align):
    new_x_pos = (image.width - layer.width) / 2
    new_y_pos = {
        'TOP': 0,
        'BOTTOM': image.height - layer.height,
        'CENTER': (image.height - layer.height) / 2,
    }.get(vertical_align, 0)

    layer.set_offsets(int(new_x_pos), int(new_y_pos))


def center_and_rename_layer(image, index, layer, color_to_remove, vertical_align):
    position_layer(image, layer, vertical_align)
    pdb.gimp_layer_resize_to_image_size(layer)
    layer.name = "%d (replace)" % index

    if color_to_remove is not None:
        pdb.gimp_image_select_color(image, CHANNEL_OP_REPLACE, layer, color_to_remove)
        # Check if selection is non-empty
        if pdb.gimp_selection_bounds(image)[0]:
            pdb.gimp_edit_clear(layer)
        pdb.gimp_selection_none(image)


def align_layer_keep_non_empty(image, layer):
    pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE, layer)
    x0, y0 = pdb.gimp_drawable_offsets(layer)
    non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)
    if non_empty:
        pdb.gimp_layer_resize(layer, x2 - x1, y2 - y1, x0 - x1, y0 - y1)
        pdb.gimp_layer_set_offsets(layer, 0, 0)
    else:
        pdb.gimp_image_remove_layer(image, layer)


def sprite_guillotine(image, drawable, initial_direction, vertical_align, remove_bg_color, stop_after_initial):
    image.undo_group_start()
    prev_elapsed_time_sec = 0
    loop_index = 0
    keep_looping = True
    while keep_looping:
        loop_index = loop_index + 1
        loop_text = 'Guillotine Loop #%d: ' % loop_index
        set_text(loop_text)
        layer_index = 0
        num_layers_existing = len(image.layers)
        num_gillotines = 0
        for layer in image.layers:
            layer_index = layer_index + 1
            pdb.gimp_selection_none(image)
            set_text('%s Detecting guides...' % loop_text)
            guides_for_transparent(image, layer, loop_index, initial_direction)
            if stop_after_initial:
                image.undo_group_end()
                return
            guide_id = pdb.gimp_image_find_next_guide(image, 0)
            if guide_id > 0:
                num_gillotines += 1
                guillotine_layer(image, layer, loop_text)
        keep_looping = num_gillotines > 0
        pdb.gimp_displays_flush()
        num_layers_created = len(image.layers) - num_layers_existing
        prev_elapsed_time_sec = elapsed_message(
            '%s\n%d of %d Layers Guillotined\n%d Layers Created' % (
                loop_text, num_gillotines, num_layers_existing, num_layers_created),
            prev_elapsed_time_sec)

    set_text('Finalizing layers...')
    tallest_height = 0
    widest_width = 0
    num_layers_existing = len(image.layers)
    for layer in image.layers:
        tallest_height = max(tallest_height, layer.height)
        widest_width = max(widest_width, layer.width)
    image.resize(widest_width, tallest_height, 0, 0)
    pdb.gimp_displays_flush()
    center_and_rename_layers(image, remove_bg_color, vertical_align)
    pdb.gimp_displays_flush()
    pdb.gimp_selection_none(image)
    image.undo_group_end()
    elapsed_message("Layer Center/Rename\n%d Layers Processed" % num_layers_existing, prev_elapsed_time_sec)


def sprite_guillotine_gui(image, drawable):
    # Initialize GUI window
    dialog = gimpui.Dialog(title="Sprite Guillotine", role=None)
    dialog.set_default_size(400, 300)

    # Create a VBox to hold the GUI elements
    vbox = gtk.VBox(spacing=6)
    dialog.vbox.pack_start(vbox, True, True, 0)
    vbox.show()

    # Option for initial direction
    direction_frame = gtk.Frame("Initial Direction")
    vbox.pack_start(direction_frame, False, False, 0)
    direction_box = gtk.HBox(spacing=6)
    direction_frame.add(direction_box)
    horizontal_radio = gtk.RadioButton(None, "Horizontal")
    vertical_radio = gtk.RadioButton(horizontal_radio, "Vertical")
    direction_box.pack_start(horizontal_radio, False, False, 0)
    direction_box.pack_start(vertical_radio, False, False, 0)
    horizontal_radio.set_active(True)  # Default to horizontal

    # Option for vertical align
    align_frame = gtk.Frame("Vertical Align")
    vbox.pack_start(align_frame, False, False, 0)
    align_box = gtk.HBox(spacing=6)
    align_frame.add(align_box)
    top_radio = gtk.RadioButton(None, "Top")
    middle_radio = gtk.RadioButton(top_radio, "Middle")
    bottom_radio = gtk.RadioButton(middle_radio, "Bottom")
    align_box.pack_start(top_radio, False, False, 0)
    align_box.pack_start(middle_radio, False, False, 0)
    align_box.pack_start(bottom_radio, False, False, 0)
    middle_radio.set_active(True)  # Default to middle

    # Checkbox for removing BG color
    remove_bg_checkbox = gtk.CheckButton("Remove BG Color?")
    vbox.pack_start(remove_bg_checkbox, False, False, 0)
    remove_bg_checkbox.set_active(False)

    # Checkbox for stopping after initial
    stop_after_initial_checkbox = gtk.CheckButton("Stop after initial guide detect?")
    vbox.pack_start(stop_after_initial_checkbox, False, False, 0)
    stop_after_initial_checkbox.set_active(False)

    # Add a progress bar
    global progress_bar
    progress_bar = gtk.ProgressBar()
    vbox.pack_start(progress_bar, False, False, 0)
    set_text("Ready to start.")
    dialog.add_action_widget(gtk.Button("OK"), gtk.RESPONSE_OK)
    dialog.add_action_widget(gtk.Button("Cancel"), gtk.RESPONSE_CANCEL)
    dialog.show_all()
    response = dialog.run()

    if response == gtk.RESPONSE_OK:
        global start_time_sec
        start_time_sec = time.time()

        direction = None if False \
            else HORIZONTAL if horizontal_radio.get_active() \
            else VERTICAL

        align = None if False \
            else TOP if top_radio.get_active() \
            else MIDDLE if middle_radio.get_active() \
            else BOTTOM

        remove_bg = remove_bg_checkbox.get_active()
        stop_after_initial = stop_after_initial_checkbox.get_active()
        sprite_guillotine(image, drawable, direction, align, remove_bg, stop_after_initial)
        pass

    dialog.destroy()


register(
    "sprite_guillotine",
    "",
    "",
    "",
    "",
    "2024",
    "Sprite Guillotine",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    sprite_guillotine_gui, menu="<Image>/Filters")
main()
