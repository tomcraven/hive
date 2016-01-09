import pygame
from enum import Enum
import texture_manager
from player import PlayerNumber
from position import Position
from draw import Draw

class Tile( object ):
	@staticmethod
	def create( tile_type, player ):
		return tile_type_object[ tile_type ]( player )

	def __init__( self, tile_type, player ):
		self.__position = Position()
		self.__render_position = [ 0, 0 ]
		self.image = texture_manager.load( tile_image_path[ tile_type ] )
		self.player = player
		self.type = tile_type
		self.beetle_ontop = None

		# Set the tile type colour
		self.image.fill( tile_type_colours[ tile_type ], special_flags = pygame.BLEND_ADD )

		# Set the player colour, i can't think of a better way to do this atm...
		for y in range( self.image.get_height() ):
			for x in range( self.image.get_width() ):
				colour = self.image.get_at( ( x, y ) )
				if colour[ 0 ] == 255 and colour[ 1 ] == 255 and colour[ 2 ] == 255:
					self.image.set_at( ( x, y ), player.get_colour() )

	def get_position( self ):
		return self.__position

	def set_position( self, position, board ):
		self.__position.set( position )
		self.__render_position = Draw.get_render_position( self.__position )

	def render( self, surface ):
		Draw.image( surface, self.image, self.__position )

	def adjacent_position_movement_is_wide_enough( self, board, begin, end ):
		# distance between begin and end should be 1
		# firstly find adjacent positions that are shared by begin and end
		begin_adjacent_positions = list( begin.get_adjacent_positions() )
		end_adjacent_positions = list( end.get_adjacent_positions() )
		shared_adjacent_positions = [ x for x in begin_adjacent_positions if x in end_adjacent_positions ]
		assert len( shared_adjacent_positions ) == 2

		# if both shared positions are occupied then we cannot move between them
		# i.e. if either position is free, then we can pass
		if len( board.get_tiles_with_position( shared_adjacent_positions[0] ) ) == 0 or \
			len( board.get_tiles_with_position( shared_adjacent_positions[1] ) ) == 0:
			return True

		return False

	def position_is_reachable( self, board, target_position, free_positions ):
		# we need to walk from get_position() to target_position
		# whilst checking that the pieces either side of each position on the route...
		#...are large enough for us to fit through
		# it's a stupid recurrsive search but does the job (i think)

		def can_create_path_between( begin, end, visited_nodes ):
			adjacent_positions_to_begin = begin.get_adjacent_positions()
			adjacent_free_positions_to_begin = [ x for x in adjacent_positions_to_begin if x in free_positions ]

			# calculate if we can move to adjacent position
			valid_positions = [ x for x in adjacent_free_positions_to_begin \
				if self.adjacent_position_movement_is_wide_enough( board, begin, x ) \
				and x not in visited_nodes ]
			visited_nodes.extend( valid_positions )

			if end in valid_positions:
				return True

			for position in valid_positions:
				if can_create_path_between( position, end, visited_nodes ):
					return True

			return False

		return can_create_path_between( self.get_position(), target_position, [] )


class Ant( Tile ):
	def __init__( self, player ):
		super( Ant, self ).__init__( TileType.ant, player )

	def get_valid_positions( self, board ):
		# can be placed anywhere that's free and touching another piece
		# ant needs to be able to 'walk' into the space...
		#...sometimes a gap might be too small for it to enter into (lol)

		def get_free_positions_on_board():
			free_positions = []
			for tile in board.tiles:
				if tile == self:
					continue

				adjacent_positions = tile.get_position().get_adjacent_positions()

				for position in adjacent_positions:
					if len( board.get_tiles_with_position( position ) ) == 0:
						if position not in free_positions:
							free_positions.append( position )

			return free_positions

		free_positions = get_free_positions_on_board()
		reachable_positions = [ x for x in free_positions if self.position_is_reachable( board, x, free_positions ) ]

		return reachable_positions

class Bee( Tile ):
	def __init__( self, player ):
		super( Bee, self ).__init__( TileType.bee, player )

	def get_valid_positions( self, board ):
		# valid positions for bee are:
		# * 1 tile away
		# * not already occupied
		# * touching another tile (if we 'remove' the current bee tile)
		# * 'reachable' - i.e. wide enough to be walked into
		# there also needs to be a tile that is adjacently shared by both the start and end position...
		#...this is so we dont 'jump' over a cave-like gap

		adjacent_positions = self.get_position().get_adjacent_positions()
		free_adjacent_positions = [ x for x in adjacent_positions if len( board.get_tiles_with_position( x ) ) == 0 ]
		reachable_free_adjacent_positions = \
			[ x for x in free_adjacent_positions if self.adjacent_position_movement_is_wide_enough( board, self.get_position(), x ) ]

		def has_occupied_shared_tile( begin, end ):
			begin_adjacent_positions = list( begin.get_adjacent_positions() )
			end_adjacent_positions = list( end.get_adjacent_positions() )
			shared_adjacent_positions = [ x for x in begin_adjacent_positions if x in end_adjacent_positions ]
			assert len( shared_adjacent_positions ) == 2

			shared_adjacent_tiles = [
				len( board.get_tiles_with_position( shared_adjacent_positions[0] ) ),
				len( board.get_tiles_with_position( shared_adjacent_positions[1] ) )
			]

			return shared_adjacent_tiles.count( 0 ) == 1

		reachable_free_adjacent_positions = [ x for x in reachable_free_adjacent_positions if has_occupied_shared_tile( self.get_position(), x ) ]

		def movement_creates_an_island( end ):
			tiles = list( board.tiles )
			start_position = self.get_position()
			self.set_position( end, board )
			connected_hive = board.hive_is_connected( tiles )
			self.set_position( start_position, board )
			return not connected_hive

		return [ x for x in reachable_free_adjacent_positions if not movement_creates_an_island( x ) ]

class Beetle( Tile ):
	def __init__( self, player ):
		self.tile_underneith = None
		super( Beetle, self ).__init__( TileType.beetle, player )

	def get_valid_positions( self, board ):
		# valid positions for beetle are:
		# * 1 tile away
		# * can be already occupied (we just jump on top)
		# * touching another tile (if we 'remove' the current bee tile)
		# * 'reachable' - i.e. wide enough to be walked into
		# there also needs to be a tile that is adjacently shared by both the start and end position...
		#...this is so we dont 'jump' over a cave-like gap

		adjacent_positions = self.get_position().get_adjacent_positions()

		# For tiles that are already taken, we can move there no problem...
		# For target positions that have no tile attached, we need to check that moving here doesn't create an island

		def movement_creates_an_island( end ):
			tiles = list( board.tiles )
			start_position = self.get_position()
			self.set_position( end, board )
			connected_hive = board.hive_is_connected( tiles )
			self.set_position( start_position, board )
			return not connected_hive

		valid_positions = [ x for x in adjacent_positions if not movement_creates_an_island( x ) ]

		return valid_positions

	def set_position( self, position, board ):
		# Remove the beetle reference from the tile that we're moving from (if there is one)
		if self.tile_underneith is not None:
			self.tile_underneith.beetle_ontop = None

		# Find the tiles we're ontop of, then find the highest one
		tiles_ontop_of = board.get_tiles_with_position( position )
		self.tile_underneith = next( ( x for x in tiles_ontop_of if x.beetle_ontop == None ), None )

		# If we're not ontop of a tile, update the reference to this beetle
		if self.tile_underneith is not None:
			self.tile_underneith.beetle_ontop = self

		super( Beetle, self ).set_position( position, board )

		self.create_scaled_image()

	def create_scaled_image( self ):
		scale_factor = 1
		tile_underneith = self.tile_underneith
		while tile_underneith is not None:
			scale_factor *= 0.75

			if tile_underneith.type == TileType.beetle:
				tile_underneith = tile_underneith.tile_underneith
			else:
				tile_underneith = None

		self.__scaled_image = pygame.transform.scale( self.image, 
			[ int( self.image.get_width() * scale_factor ), int( self.image.get_height() * scale_factor ) ] )

		self.__render_position = Draw.get_render_position( self.get_position() )
		self.__render_position[ 0 ] += ( self.image.get_width() - self.__scaled_image.get_width() ) / 2
		self.__render_position[ 1 ] += ( self.image.get_height() - self.__scaled_image.get_height() ) / 2

	def render( self, surface ):
		Draw.image_explicit( surface, self.__scaled_image, *self.__render_position )

class GrassHopper( Tile ):
	def __init__( self, player ):
		super( GrassHopper, self ).__init__( TileType.grass_hopper, player )

	def get_valid_positions( self, board ):
		# Grass hopper moves along edges until it reaches the first blank square
		# If there is a blank square right next to it, then it can't jump in that direction

		def find_first_blank_square( position, callback ):
			if len( board.get_tiles_with_position( position ) ) == 0:
				return position

			return find_first_blank_square( callback( position ), callback )

		jumpable_positions = [
			find_first_blank_square( self.get_position(), lambda position : position.east() ),
			find_first_blank_square( self.get_position(), lambda position : position.west() ),
			find_first_blank_square( self.get_position(), lambda position : position.north_west() ),
			find_first_blank_square( self.get_position(), lambda position : position.north_east() ),
			find_first_blank_square( self.get_position(), lambda position : position.south_west() ),
			find_first_blank_square( self.get_position(), lambda position : position.south_east() ),
		]

		# If one of the jumpable positions is directly adjacent then ignore it
		non_adjacent_jumpable_positions = [ x for x in jumpable_positions \
			if x not in self.get_position().get_adjacent_positions() ]

		return non_adjacent_jumpable_positions

class Spider( Tile ):
	def __init__( self, player ):
		super( Spider, self ).__init__( TileType.spider, player )

	def get_valid_positions( self, board ):
		# Spider movement is three tiles away from self
		# Tiles must be free
		# Can 'jump' gaps (might be tricky to create a test case for this)
		# Must not double back on itself (i think)
		return []

class TileType( Enum ):
	ant = 0
	bee = 1
	beetle = 2
	grass_hopper = 3
	spider = 4

tile_image_path = {
	TileType.ant : "images/ant.png",
	TileType.bee : "images/bee.png",
	TileType.beetle : "images/beetle.png",
	TileType.grass_hopper : "images/grass_hopper.png",
	TileType.spider : "images/spider.png",
}

tile_type_object = {
	TileType.ant : Ant,
	TileType.bee : Bee,
	TileType.beetle : Beetle,
	TileType.grass_hopper : GrassHopper,
	TileType.spider : Spider,
}

tile_type_colours = {
	TileType.ant : ( 0, 148, 255 ),
	TileType.bee : ( 255, 185, 0 ),
	TileType.beetle : ( 224, 0, 255 ),
	TileType.grass_hopper : ( 40, 220, 40 ),
	TileType.spider : ( 144, 0, 7 ),
}