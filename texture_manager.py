import pygame

__loaded_textures = {}
def load( path ):
	# if __loaded_textures.has_key( path ):
	# 	return __loaded_textures[ path ]

	# __loaded_textures[ path ] = pygame.image.load( path )
	# return __loaded_textures[ path ]

	return pygame.image.load( path )