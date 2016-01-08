import pygame

__loaded_textures = []
def load( path ):
	__loaded_textures.append( pygame.image.load( path ) )
	return __loaded_textures[ len( __loaded_textures ) - 1 ]

def average_width():
	return sum( [ x.get_width() for x in __loaded_textures ] ) / len( __loaded_textures )

def average_height():
	return sum( [ x.get_height() for x in __loaded_textures ] ) / len( __loaded_textures )