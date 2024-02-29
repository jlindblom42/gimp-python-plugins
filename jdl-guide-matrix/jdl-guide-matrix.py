#! /usr/bin/python

from gimpfu import *

def guide_clear(image):
	guides = []
	#read guide ids
	guide_id = pdb.gimp_image_find_next_guide(image,0)
	while guide_id > 0:
		guides.append(guide_id)
		guide_id = pdb.gimp_image_find_next_guide(image,guide_id)
	#remove it in reverse order
	guides = guides[::-1] #reverse the list
	for guide_id in guides:
		pdb.gimp_image_delete_guide(image,guide_id)
        
def guide_matrix(image, drawable):
    image.undo_group_start()
    guide_clear(image)
    width = image.width
    height = image.height
    # Horizontal guides
    pdb.gimp_image_add_hguide(image, height * 0.25)
    pdb.gimp_image_add_hguide(image, height * 0.5)
    pdb.gimp_image_add_hguide(image, height * 0.75)
    # Vertical guides
    pdb.gimp_image_add_vguide(image, width * 0.25)
    pdb.gimp_image_add_vguide(image, width * 0.5)
    pdb.gimp_image_add_vguide(image, width * 0.75)
    image.undo_group_end()

register(
          "guide_matrix",
          "",
          "",
          "",
          "",
          "2024",
          "Guide Matrix",
          "*",
          [
              (PF_IMAGE, "image", "Input image", None),
              (PF_DRAWABLE, "drawable", "Input drawable", None),
          ],
          [],
          guide_matrix, menu="<Image>/Filters")
main()