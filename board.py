from tile import Tile, TileType
from player import PlayerNumber
import config, pygame, itertools
from position import Position
from draw import Draw

class Board:
	def __init__( self ):
		self.tiles = []

	def update( self ):
		# get moves for each player? (maybe do this outside of this class)
		# check for win/lose condition
		# make sure we can see the whole board on the screen
		pass

	def render( self, surface ):
		for tile in self.tiles:
			tile.render( surface )

		# Render the coordinates of all tiles and their adjacent pieces
		# We're rendering each coordinate multiple times here, but it shouldn't matter too much
		for tile in self.tiles:
			for position in tile.get_position().get_adjacent_positions():
				Draw.coordinate( surface, position )

	def touching( self, tile_position, position ):
		return position in tile_position.get_adjacent_positions()

	def position_already_occupied( self, position ):
		return any( [ tile.get_position() == position for tile in self.tiles ] )

	def touching_any( self, position ):
		return any( [ self.touching( tile.get_position(), position ) for tile in self.tiles ] )

	def get_adjacent_tiles( self, position ):
		return [ tile for tile in self.tiles if self.touching( tile.get_position(), position ) ]

	def get_tiles_for_player( self, player ):
		return [ tile for tile in self.tiles if tile.player == player ]

	def touching_any_opponent_piece( self, position, player ):
		return any( [ tile for tile in self.get_adjacent_tiles( position ) if tile.player != player ] )

	def touching_same_player_piece( self, position, player ):
		return any( [ tile for tile in self.get_adjacent_tiles( position ) if tile.player == player ] )

	def players_first_tile( self, player ):
		return len( [ tile for tile in self.tiles if tile.player == player ] ) == 0

	def player_needs_to_play_bee( self, player ):
		players_tiles = self.get_tiles_for_player( player )
		if len( players_tiles ) <= config.maximum_moves_before_bee:
			return False

		has_played_bee = ( [ tile.type for tile in players_tiles ].count( TileType.bee ) > 0 )

		return not has_played_bee

	def validate_tile_placement( self, position, player ):

		# If the board is empty, the first piece can be played anywhere
		if len( self.tiles ) == 0:
			return

		# If player is trying to play ontop of an existing piece, that's a no-no
		if self.position_already_occupied( position ):
			raise ValueError( "There is already a piece at this position", position, player )

		# If there are tiles on the board and it is the player's first piece...
		#...this piece needs to be touching *any* another piece to be played
		if self.players_first_tile( player ):
			if not self.touching_any( position ):
				raise ValueError( "First tile is not touching another piece on the board", position, player)
			return

		# Both players already have pieces in play, the placed piece cannot touch any...
		#...pieces from opponent
		if self.touching_any_opponent_piece( position, player ):
			raise ValueError( "Tile is touching an opponents piece", position, player )

		# The piece must be touching at least one piece from same player
		if not self.touching_same_player_piece( position, player ):
			# Not sure we can even get here...
			raise ValueError( "Tile is not touching one of the same player's pieces", position, player )

		# Finally - check that we need to force the player to play bee
		if self.player_needs_to_play_bee( player ):
			raise ValueError( "Player needs to play their bee", player )

	def place_tile( self, tile_type, position, player ):
		self.validate_tile_placement( position, player )

		new_tile = Tile.create( tile_type, player )
		new_tile.set_position( position, self )
		self.tiles.append( new_tile )

		return new_tile

	def get_tiles_with_position( self, position ):
		return [ x for x in self.tiles if x.get_position() == position ]

	def hive_is_connected( self, tiles = None ):
		visited_tiles = []

		if tiles is None:
			tiles = self.tiles

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

	def valid_movement_for_tile_type( self, tile, position ):
		return position in tile.get_valid_positions( self )

	def validate_tile_movement( self, tile, position ):
		if self.tile_is_pinned( tile ):
			raise ValueError( "Tile is currently pinned", tile, position )

		if tile.beetle_ontop is not None:
			raise ValueError( "Tile is currently under a beetle", tile, position )

		if not self.valid_movement_for_tile_type( tile, position ):
			raise ValueError( "This is not a valid movement for this tile", tile, position )

	def move_tile( self, tile, position ):
		self.validate_tile_movement( tile, position )

		tile.set_position( position, self )