from os import walk
import pygame

def import_folder(path):
	surface_list = []

	for _, __, img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list

#from os import walk
#import pygame
#import os
#
#def import_folder(path):
#    surface_list = []
#
#    if os.path.exists(path):
#        print(f"Path {path} exists.")
#        for _, __, img_files in walk(path):
#            for image in img_files:
#                full_path = os.path.join(path, image)
#                print(f"Loading image: {full_path}")
#                image_surf = pygame.image.load(full_path).convert_alpha()
#                surface_list.append(image_surf)
#    else:
#        print(f"Path {path} does not exist.")
#
#    return surface_list
#