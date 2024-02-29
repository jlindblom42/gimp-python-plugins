#! /usr/bin/python

from gimpfu import *


def guide_clear(image, drawable):
    image.undo_group_start()
    guides = []

    # read guide ids
    guide_id = pdb.gimp_image_find_next_guide(image, 0)
    while guide_id > 0:
        guides.append(guide_id)
        guide_id = pdb.gimp_image_find_next_guide(image, guide_id)

    # remove it in reverse order
    guides = guides[::-1]  # reverse the list
    for guide_id in guides:
        pdb.gimp_image_delete_guide(image, guide_id)

    image.undo_group_end()


register(
    "guide_clear",
    "",
    "",
    "",
    "",
    "2024",
    "Guide Clear",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    guide_clear, menu="<Image>/Filters")
main()
