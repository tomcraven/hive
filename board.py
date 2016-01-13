from tile import Tile, TileType
from player import PlayerNumber
import config, pygame, itertools
from position import Position
from draw import Draw
import texture_manager as texture_manager

class PlayerBoardProxy:
	def __init__( self, board, current_player, opponent_player ):
		self.__board = board
		self.__player = current_player
		self.__opponent_player = opponent_player

		self.__has_performed_move = False

	def get_valid_placements_for_tile( self, tile_type ):
		return self.__board.get_valid_tile_placements( tile_type, self.__player )

	def get_valid_movements_for_tile( self, tile ):
		return self.__board.get_valid_movements_for_tile( tile, self.__player )

	def get_my_played_tiles( self ):
		return [ x for x in self.__player.tiles if x in self.__board.tiles ]

	def get_my_unplayed_tiles( self ):
		return [ x for x in self.__player.tiles if x not in self.__board.tiles ]

	def get_opponent_played_tiles( self ):
		return [ x for x in self.__opponent_player.tiles if x in self.__board.tiles ]

	def get_opponent_unplayed_tiles( self ):
		return [ x for x in self.__opponent_player.tiles if x not in self.__board.tiles ]

	def get_tiles_with_position( self, position ):
		return self.__board.get_tiles_with_position( position )

	def place_tile( self, tile_type, position ):
		assert self.__has_performed_move == False

		self.__has_performed_move = True
		placed_tile = self.__board.place_tile( tile_type, position, self.__player )
		print self.__player, "placed", placed_tile, "at", position
		return placed_tile

	def move_tile( self, tile, position ):
		assert self.__has_performed_move == False

		print self.__player, "moved", tile, "from", tile.get_position(), "to", position
		self.__has_performed_move = True
		self.__board.move_tile( self.__player, tile, position )

	def has_performed_move( self ):
		return self.__has_performed_move

class Board:
	def __init__( self, player_one, player_two ):
		self.tiles = []

		self.__player_one = player_one
		self.__player_two = player_two

		self.__next_player = self.__player_one

		self.__cached_tile_movements = {}

		self.update_board_render_bounds()

	def get_winner( self ):

		def players_bee_is_surrounded( player ):
			player_bee = next( ( x for x in self.get_tiles_for_player( player ) if x.type == TileType.bee ), None )

			if player_bee is not None:
				bee_position = player_bee.get_position()
				return \
					( len( self.get_tiles_with_position( bee_position.west() ) ) > 0 ) and \
					( len( self.get_tiles_with_position( bee_position.east() ) ) > 0 ) and \
					( len( self.get_tiles_with_position( bee_position.north_west() ) ) > 0 ) and \
					( len( self.get_tiles_with_position( bee_position.north_east() ) ) > 0 ) and \
					( len( self.get_tiles_with_position( bee_position.south_west() ) ) > 0 ) and \
					( len( self.get_tiles_with_position( bee_position.south_east() ) ) > 0 )

			return False


		def player_can_place( player ):
			player_unplayed_tiles = [ x for x in player.tiles if x not in self.tiles ]
			for tile in player_unplayed_tiles:
				possible_placements = self.get_valid_tile_placements( tile.type, player )
				if len( possible_placements ) > 0:
					return True
			return False

		def player_can_move( player ):
			player_played_tiles = self.get_tiles_for_player( player )
			for tile in player_played_tiles:
				if len( self.get_valid_movements_for_tile( tile, player ) ) > 0:
					return True
			return False

		if ( not player_can_place( self.__next_player ) ) and ( not player_can_move( self.__next_player ) ):
			return self.__player_two if self.__next_player is self.__player_one else self.__player_one

		if players_bee_is_surrounded( self.__player_one ):
			return self.__player_two

		if players_bee_is_surrounded( self.__player_two ):
			return self.__player_one

		return None

	def update( self ):
		# todo - check for conditions in which both AIs are doing the same thing each time, in these cases it's a draw
		board_proxy = PlayerBoardProxy( self, self.__next_player, self.__player_two if self.__next_player is self.__player_one else self.__player_one )
		self.__next_player.perform_move( board_proxy )
		self.__next_player = self.__player_two if self.__next_player is self.__player_one else self.__player_one

		if not board_proxy.has_performed_move():
			has_tiles_to_place = len( board_proxy.get_unplayed_tiles() ) > 0
			has_tiles_to_move = False
			for tile in board_proxy.get_played_tiles():
				if len( board_proxy.get_valid_movements_for_tile( tile ) ) > 0:
					has_tiles_to_move = True

			if has_tiles_to_place or has_tiles_to_move:
				raise ValueError( "Player must either play a tile or move a piece each turn (if able)",
					"has_tiles_to_place:", has_tiles_to_place,
					"has_tiles_to_move:", has_tiles_to_move )

		assert self.hive_is_connected()

		# Make sure we can see the whole board on the screen
		self.update_board_render_bounds()

		self.__cached_tile_movements = {}

	def update_board_render_bounds( self ):
		position_rect = [ 0, 0, 1, 1 ]
		left, top, right, bottom = 0, 1, 2, 3
		x, y = 0, 1

		for tile in self.tiles:
			position = tile.get_position().get()

			position_rect[ left ] = min( position[ x ], position_rect[ left ] )
			position_rect[ right ] = max( position[ x ], position_rect[ right ] )

			position_rect[ top ] = min( position[ y ], position_rect[ top ] )
			position_rect[ bottom ] = max( position[ y ], position_rect[ bottom ] )

		self.__render_bounds = [
			Draw.get_render_position( Position( [ position_rect[ left ], position_rect[ top ] ] ) ),
			Draw.get_render_position( Position( [ position_rect[ right ], position_rect[ bottom ] ] ) )
		]

		top_left, bottom_right = 0, 1
		self.__render_bounds[ top_left ][ x ] -= 1.5 * texture_manager.average_width()
		self.__render_bounds[ bottom_right ][ x ] += 2.5 * texture_manager.average_width()

		self.__render_bounds[ top_left ][ y ] -= 0.5 * texture_manager.average_height()
		self.__render_bounds[ bottom_right ][ y ] += 1.5 * texture_manager.average_height()

		Draw.set_render_bounds( self.__render_bounds )

	def render( self, surface ):

		width = int( self.__render_bounds[ 1 ][ 0 ] - self.__render_bounds[ 0 ][ 0 ] )
		height = int( self.__render_bounds[ 1 ][ 1 ] - self.__render_bounds[ 0 ][ 1 ] )
		render_surface = pygame.Surface( ( width, height ) )

		# Make sure we render the tiles under beetles first
		rendered_tiles = []
		for tile in self.tiles:
			def render_tile( tile ):
				if tile.type == TileType.beetle and tile.tile_underneith is not None:
					render_tile( tile.tile_underneith )

				tile.render( render_surface )
				rendered_tiles.append( tile )

			if tile not in rendered_tiles:
				render_tile( tile )

		# Render the coordinates of all tiles and their adjacent pieces
		# We're rendering each coordinate multiple times here, but it shouldn't matter too much
		for tile in self.tiles:
			for position in tile.get_position().get_adjacent_positions():
				Draw.coordinate( render_surface, position )

		# Scale and blit our render surface to the screen surface
		scaled_render_surface = pygame.transform.scale( render_surface, [ width, height ] )
		surface.blit( scaled_render_surface, [ 0, 0 ] )

	def touching( self, tile_position, position ):
		return position in tile_position.get_adjacent_positions()

	def position_already_occupied( self, position ):
		return any( [ tile.get_position() == position for tile in self.tiles ] )

	def touching_any( self, position, apart_from_tiles = [] ):
		return any( [ self.touching( tile.get_position(), position ) for tile in self.tiles if tile not in apart_from_tiles ] )

	def get_adjacent_tiles( self, position ):
		return [ tile for tile in self.tiles if self.touching( tile.get_position(), position ) ]

	def get_tiles_for_player( self, player ):
		return [ tile for tile in self.tiles if tile.player == player ]

	def touching_any_opponent_piece( self, position, player ):
		return any( [ tile for tile in self.get_adjacent_tiles( position ) if tile.player != player ] )

	def touching_same_player_piece( self, position, player ):
		return any( [ tile for tile in self.get_adjacent_tiles( position ) if tile.player == player ] )

	def player_has_played_bee( self, player ):
		return ( [ tile.type for tile in self.get_tiles_for_player( player ) ].count( TileType.bee ) > 0 )

	def player_needs_to_play_bee( self, player ):
		players_tiles = self.get_tiles_for_player( player )
		if len( players_tiles ) <= config.maximum_moves_before_bee:
			return False

		return not self.player_has_played_bee( player )

	# Returns all positions on the board that are 'unoccupied'
	# These are not positions that are 'valid' tile placements or movements
	def get_unoccupied_positions( self ):
		if len( self.tiles ) == 0:
			return [ Position( [ 0, 0 ] ) ]

		free_positions = []
		for tile in self.tiles:
			if tile == self:
				continue

			adjacent_positions = tile.get_position().get_adjacent_positions()

			for position in adjacent_positions:
				if len( self.get_tiles_with_position( position ) ) == 0:
					if position not in free_positions:
						free_positions.append( position )

		return free_positions

	def get_valid_tile_placements( self, tile_type, player ):
		unoccupied_positions = self.get_unoccupied_positions()

		# Player can place their first tile anywhere
		if len( self.get_tiles_for_player( player ) ) == 0:
			return unoccupied_positions

		# Position must not have any adjacent positions that have tiles occupied by the opponent
		valid_positions = [ x for x in unoccupied_positions if not self.touching_any_opponent_piece( x, player ) ]

		# If player needs to play their bee, then force this tile to be played
		if ( self.player_needs_to_play_bee( player ) ) and ( tile_type != TileType.bee ):
			valid_positions = []

		return valid_positions

	def tile_in_play( self, tile ):
		return tile in self.tiles

	def place_tile( self, tile_type, position, player ):
		valid_tile_placements = self.get_valid_tile_placements( tile_type, player )
		if position not in valid_tile_placements:
			raise ValueError( str( position ), "is not a valid placement for tile", tile_type,
				"Valid placements are: ", ",".join( [ str( x ) for x in valid_tile_placements ] ) )

		tile = player.get_new_tile( tile_type, self )
		if not tile:
			raise ValueError( "Unable to play tile", tile_type, "Does", str( player ), "have this tile available to play?" )

		tile.set_position( position, self )
		self.tiles.append( tile )

		return tile

	def get_tiles_with_position( self, position ):
		return [ x for x in self.tiles if x.get_position() == position ]

	def hive_is_connected( self, tiles = None ):
		visited_tiles = []

		if tiles is None:
			tiles = self.tiles

		if len( tiles ) == 0:
			return True

		def count_island_size( tile ):
			visited_tiles.append( tile )
			adjacent_tiles = self.get_adjacent_tiles( tile.get_position() )
			unvisted_adjacent_tiles = [ x for x in adjacent_tiles if x not in visited_tiles ]
			visited_tiles.extend( unvisted_adjacent_tiles )

			size = 1
			for unvisted_adjacent_tile in unvisted_adjacent_tiles:
				size += count_island_size( unvisted_adjacent_tile )

			return size

		return count_island_size( tiles[ 0 ] ) == len( tiles )

	def tile_is_pinned( self, tile ):
		# Check that removing the tile doesn't create any islands
		self.tiles.remove( tile )
		connected_hive = self.hive_is_connected()
		self.tiles.append( tile )

		return not connected_hive

	def get_valid_movements_for_tile( self, tile, player ):

		if self.__cached_tile_movements.has_key( tile ):
			return self.__cached_tile_movements[ tile ]

		valid_tile_movements = []

		if ( not self.tile_is_pinned( tile ) ) and ( tile.beetle_ontop is None ) and ( self.player_has_played_bee( player ) ):
			valid_tile_movements = tile.get_valid_positions( self )

		self.__cached_tile_movements[ tile ] = valid_tile_movements
		return valid_tile_movements

	def move_tile( self, player, tile, position ):

		if tile not in self.tiles:
			raise ValueError( tile, "is not currently in play" )

		valid_tile_movements = self.get_valid_movements_for_tile( tile, player )

		if not position in valid_tile_movements:
			raise ValueError( str( position ), "is not a valid movement for tile", tile,
				"Valid movements are: ", ",".join( [ str( x ) for x in valid_tile_movements ] ) )

		tile.set_position( position, self )