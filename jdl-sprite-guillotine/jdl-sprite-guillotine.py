#! /usr/bin/python

from gimpfu import *
import gtk
import gimpui

HORIZONTAL = 0
VERTICAL = 1
BOTH = 2

TOP = 0
MIDDLE = 1
BOTTOM = 2


def set_text(progress_bar_text):
    progress_bar.set_text(progress_bar_text)
    gtk.main_iteration_do(False)


def print_args(args):
    output = ''
    for k, v in args:
        output += '%s: %s\n' % (k, v)
    pdb.gimp_message(output)


def guide_clear(image):
    # Directly removing guides without reversing the list or individually fetching them
    while True:
        guide_id = pdb.gimp_image_find_next_guide(image, 0)
        if guide_id == 0:
            break
        pdb.gimp_image_delete_guide(image, guide_id)


def get_pixel_at_coordinates(image, layer, x, y):
    # Get a pixel region representing the entire layer
    region = layer.get_pixel_rgn(0, 0, layer.width, layer.height)
    # Extract the pixel value. Format is (R, G, B, A) with values 0-255
    pixel = region[x, y]
    return pixel


has_no_guides_map = {}


def guides_for_transparent(image, layer, loop_index, initial_direction):
    if layer.name in has_no_guides_map:
        return

    has_no_guides = True
    initial_loop = loop_index == 1
    allow_vertical = True
    allow_horizontal = True
    if initial_loop:
        allow_vertical = initial_direction != HORIZONTAL
        allow_horizontal = initial_direction != VERTICAL
    guide_clear(image)
    width = layer.width
    height = layer.height

    transparency_memo = {}

    layer_pixel_rgn = layer.get_pixel_rgn(0, 0, layer.width, layer.height)
    layer_pixels = layer_pixel_rgn[:, :]  # Grab all pixels at once for efficiency

    def is_transparent(x_, y_):
        key = (x_, y_)
        if key not in transparency_memo:
            # Assuming RGBA, where loop_index 3 is alpha:
            # transparency_memo[key] = layer.get_pixel(x_, y_)[3] == 0
            # pixel_data = layer_pixel_rgn[x_, y_]
            # rgba = [ord(c) for c in pixel_data]
            idx = (y_ * width + x_) * 4  # Assuming RGBA for each pixel
            transparency_memo[key] = layer_pixels[idx + 3] == '\x00'  # Check if alpha byte signifies transparency

        return transparency_memo[key]

    if allow_horizontal:
        first_guide = True
        for y in range(height):
            current_row_transparent = True
            for x in range(width):
                if not is_transparent(x, y):
                    current_row_transparent = False
                    break

            if y == 0 and not current_row_transparent:
                first_guide = False

            next_row_transparent = True
            for x in range(width):
                if y + 1 < height and not is_transparent(x, y + 1):
                    next_row_transparent = False
                    break

            if current_row_transparent and next_row_transparent:
                continue

            if not current_row_transparent and next_row_transparent:
                continue

            next_row_is_connected = False
            if not current_row_transparent and not next_row_transparent:
                for x in range(width):
                    if not is_transparent(x, y):
                        next_row_is_connected = (not is_transparent(x, y + 1)
                                                 or (x + 1 < width and not is_transparent(x + 1, y + 1))
                                                 or (x - 1 > 0 and not is_transparent(x - 1, y + 1)))
                        if next_row_is_connected:
                            break

            if not current_row_transparent and not next_row_transparent and next_row_is_connected:
                continue

            if first_guide:
                first_guide = False
                continue

            pdb.gimp_image_add_hguide(image, y + 1)
            has_no_guides = False

    if allow_vertical:
        first_guide = True
        for x in range(width):
            current_col_transparent = True
            for y in range(height):
                if not is_transparent(x, y):
                    current_col_transparent = False
                    break

            if x == 0 and not current_col_transparent:
                first_guide = False

            next_col_transparent = True
            for y in range(height):
                if x + 1 < width and not is_transparent(x + 1, y):
                    next_col_transparent = False
                    break

            if current_col_transparent and next_col_transparent:
                continue

            if not current_col_transparent and next_col_transparent:
                continue

            next_col_is_connected = False
            if not current_col_transparent and not next_col_transparent:
                for y in range(height):
                    if not is_transparent(x, y):
                        next_col_is_connected = (not is_transparent(x + 1, y)
                                                 or (y + 1 < height and not is_transparent(x + 1, y + 1))
                                                 or (y - 1 > 0 and not is_transparent(x + 1, y - 1)))
                        if next_col_is_connected:
                            break

            if not current_col_transparent and not next_col_transparent and next_col_is_connected:
                continue

            if first_guide:
                first_guide = False
                continue

            pdb.gimp_image_add_vguide(image, x + 1)
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

    if vertical_align == TOP:
        new_y_pos = 0
    elif vertical_align == BOTTOM:
        new_y_pos = image.height - layer.height
    else:
        new_y_pos = (image.height - layer.height) / 2

    layer.set_offsets(int(new_x_pos), int(new_y_pos))


def center_and_rename_layer(image, index, layer, color_to_remove, vertical_align):
    position_layer(image, layer, vertical_align)

    # Resize layer to image
    pdb.gimp_layer_resize_to_image_size(layer)
    # Rename layer to index
    layer.name = str(index) + " (replace)"

    if color_to_remove is not None:
        pdb.gimp_image_select_color(image, CHANNEL_OP_REPLACE, layer, color_to_remove)
        non_empty_selection = pdb.gimp_selection_bounds(image)[0]
        if non_empty_selection:
            pdb.gimp_edit_clear(layer)  # Delete the selected area
        pdb.gimp_selection_none(image)  # Deselect after deleting


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
    loop_index = 0
    keep_looping = True
    while keep_looping:
        loop_index = loop_index + 1
        loop_text = 'Loop #%d: ' % loop_index
        set_text(loop_text)
        layer_index = 0
        guillotine_performed = False
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
                guillotine_performed = True
                guillotine_layer(image, layer, loop_text)
        keep_looping = guillotine_performed
        pdb.gimp_displays_flush()

    set_text('Finalizing layers...')
    tallest_height = 0
    widest_width = 0
    for layer in image.layers:
        tallest_height = max(tallest_height, layer.height)
        widest_width = max(widest_width, layer.width)
    image.resize(widest_width, tallest_height, 0, 0)
    pdb.gimp_displays_flush()
    center_and_rename_layers(image, remove_bg_color, vertical_align)
    pdb.gimp_displays_flush()
    pdb.gimp_selection_none(image)
    image.undo_group_end()


def sprite_guillotine_gui(image, drawable):
    # settings = gtk.Settings.get_default()
    # settings.set_property("gtk-application-prefer-dark-theme",
    #                       True)  # if you want use dark theme, set second arg to True

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
    direction_box = gtk.VBox(spacing=6)
    direction_frame.add(direction_box)
    horizontal_radio = gtk.RadioButton(None, "Horizontal")
    vertical_radio = gtk.RadioButton(horizontal_radio, "Vertical")
    direction_box.pack_start(horizontal_radio, False, False, 0)
    direction_box.pack_start(vertical_radio, False, False, 0)
    horizontal_radio.set_active(True)  # Default to horizontal

    # Option for vertical align
    align_frame = gtk.Frame("Vertical Align")
    vbox.pack_start(align_frame, False, False, 0)
    align_box = gtk.VBox(spacing=6)
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
    set_text("Starting...")

    # Add action buttons
    dialog.add_action_widget(gtk.Button("OK"), gtk.RESPONSE_OK)
    dialog.add_action_widget(gtk.Button("Cancel"), gtk.RESPONSE_CANCEL)

    # Show the dialog
    dialog.show_all()

    # Run the dialog and wait for user response
    response = dialog.run()

    if response == gtk.RESPONSE_OK:
        direction = HORIZONTAL if horizontal_radio.get_active() else VERTICAL
        if top_radio.get_active():
            align = TOP
        elif middle_radio.get_active():
            align = MIDDLE
        else:
            align = BOTTOM
        remove_bg = remove_bg_checkbox.get_active()
        stop_after_initial = stop_after_initial_checkbox.get_active()
        sprite_guillotine(image, drawable, direction, align, remove_bg, stop_after_initial)
        pass

    dialog.destroy()


# sprite_guillotine(gimp.image_list()[0], gimp.image_list()[0].active_layer, HORIZONTAL)
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
        # (PF_RADIO, "option", "Initial direction?", HORIZONTAL,
        #  (("Horizontal", HORIZONTAL),
        #   ("Vertical", VERTICAL))),
        # (PF_RADIO, "option", "Vertical align?", MIDDLE,
        #  (("Middle", MIDDLE),
        #   ("Bottom", BOTTOM))),
        # # (PF_BOOL, "stop_after_initial", "Stop after initial guide detect?", 0),
        # (PF_BOOL, "remove_bg_color", "Remove BG Color?", 0),
    ],
    [],
    sprite_guillotine_gui, menu="<Image>/Filters")
main()
