import pygame
import texture_manager

class Draw:
	__render_bounds = [ [ 0, 0 ], [ 0, 0 ] ]

	@staticmethod
	def rect( surface, x, y, width, height, colour ):
		surface.fill( colour, [ x - Draw.__render_bounds[ 0 ][ 0 ], y - Draw.__render_bounds[ 0 ][ 1 ], width, height ] )

	@staticmethod
	def get_render_position( position ):
		x_position_modifier = 0
		if not position.is_even_row():
			half_width = texture_manager.average_width() / 2
			x_position_modifier += half_width

		return [ 
			( position.get()[0] * texture_manager.average_width() ) + x_position_modifier, 
			  position.get()[1] * ( texture_manager.average_height() * 0.75 )
		]

	@staticmethod
	def coordinate( surface, position ):
		font = pygame.font.SysFont( "monospace", 10 )
		coordinate_label = font.render( str( position ), 1, ( 0, 0, 255 ) )
		
		render_position = Draw.get_render_position( position )
		coordinate_label_position = [ render_position[ 0 ] + ( texture_manager.average_width() / 2 ) - ( coordinate_label.get_width() / 2 ), 
			render_position[ 1 ] + ( texture_manager.average_height() / 2 ) - ( coordinate_label.get_height() / 2 ) ]
		
		Draw.rect( surface, 
			coordinate_label_position[ 0 ],
			coordinate_label_position[ 1 ],
			coordinate_label.get_width(),
			coordinate_label.get_height(), 
			( 255, 255, 255 ) )

		Draw.image_explicit( surface, coordinate_label, *coordinate_label_position )

	@staticmethod
	def image( surface, image, position ):
		Draw.image_explicit( surface, image, *Draw.get_render_position( position ) )

	@staticmethod
	def image_explicit( surface, image, x, y ):
		surface.blit( image, [ x - Draw.__render_bounds[ 0 ][ 0 ], y - Draw.__render_bounds[ 0 ][ 1 ] ] )

	@staticmethod
	def set_render_bounds( bounds ):
		Draw.__render_bounds = bounds