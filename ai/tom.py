import random

import sys
sys.path.append( "../" )
from tile import TileType, Tile
from position import Position

class Placement:
	def __init__( self, tile_type = None, position = None, score = 0 ):
		self.tile_type = tile_type
		self.position = position
		self.score = score

		self.next = None

	def go( self, board ):
		board.place_tile( self.tile_type, self.position )

class Movement:
	def __init__( self, tile = None, new_position = None, score = 0 ):
		self.tile = tile
		self.new_position = new_position
		self.score = score

		self.next = None

	def go( self, board ):
		board.move_tile( self.tile, self.new_position )

class FakeBoard:
	def __init__( self, tiles ):
		self.tiles = tiles

	def get_tiles_with_position( self, position ):
		return [ x for x in self.tiles if x.get_position() == position ]

class Graph:
	def __init__( self, x_points, y_points ):
		assert len( x_points ) == len( y_points )
		self.x_points = x_points
		self.y_points = y_points

	def get_for_x( self, in_x ):
		left = 0
		right = 0

		for i, x in enumerate( self.x_points ):
			if x < in_x:
				left = i
			else:
				break

		for x in list( enumerate( self.x_points ) )[::-1]:
			if x > in_x:
				right = i
			else:
				break

		diff = ( self.x_points[ right ] - self.x_points[ left ] )

		x_delta = 0
		if diff != 0:
			x_delta = float( in_x - self.x_points[ left ] ) / diff

		return self.y_points[ left ] + ( x_delta * float( self.y_points[ right ] - self.y_points[ left ] ) )

__tile_scores = {
	TileType.bee : Graph( [ 0 ], [ 50 ] ),
	TileType.ant : Graph( [ 0, 4, 5 ], [ 10, 10, 30 ] ),
	TileType.grass_hopper : Graph( [ 0, 4, 5 ], [ 15, 15, 20 ] ),
	TileType.beetle : Graph( [ 0 ], [ 20 ] ),
	TileType.spider : Graph( [ 0 ], [ 20 ] )
}

__free_space_around_my_bee_score = 100
__beetle_ontop_of_opponent_bee_score = 30

__graph_place_tiles_multiplier = Graph( [ 0, 5, 20 ], [ 1.5, 0.25, 0.1 ] )
__graph_filled_space_around_opponent_bee_score = Graph( [ 0, 5, 20 ], [ 20, 20, 150 ] )

__turn_number = 0

def shuffle( in_iterable ):
	random.shuffle( in_iterable )
	return in_iterable
 
# todo - work out my score, work out opponents score, maximise mine and minimise opponents

def perform_move( board ):

	tiles_in_play = board.get_my_played_tiles() + board.get_opponent_played_tiles()
	best_action = get_best_action_for_board_state( board, tiles_in_play )
	if best_action is not None:
		best_action.go( board )
	else:
		perform_random_move( board )

	global __turn_number
	__turn_number += 1

def get_best_action_for_board_state( board, tiles_in_play ):

	best_placement = Placement()
	for tile_type in shuffle( get_my_unplayed_tile_types( board ) ):
		valid_placement_positions = shuffle( board.get_valid_placements_for_tile( tile_type ) )

		for placement_position in valid_placement_positions:
			new_tile = Tile.create( tile_type, board.get_me() )
			new_tile.set_position( placement_position, FakeBoard( tiles_in_play ) )

			potential_new_tiles = tiles_in_play + [ new_tile ]
			potential_new_tiles_score = score_tile_state( potential_new_tiles, board )

			placement = Placement( tile_type, placement_position, potential_new_tiles_score )
			if placement.score > best_placement.score:
				best_placement = placement

	best_movement = Movement()
	for tile in shuffle( board.get_my_played_tiles() ):
		valid_movement_positions = shuffle( board.get_valid_movements_for_tile( tile ) )
		
		for movement_position in valid_movement_positions:
			tiles_in_play.remove( tile )

			new_tile = Tile.create( tile.type, board.get_me() )
			new_tile.set_position( movement_position, FakeBoard( tiles_in_play ) )

			potential_new_tiles = tiles_in_play + [ new_tile ]
			potential_new_tiles_score = score_tile_state( potential_new_tiles, board )

			movement = Movement( tile, movement_position, potential_new_tiles_score )
			if movement.score > best_movement.score:
				best_movement = movement

			# Little bit of a hack - move any potential beetles off other tiles
			new_tile.set_position( Position( [ 1000, 1000 ] ), FakeBoard( tiles_in_play ) )
			tiles_in_play.append( tile )

	if best_placement.score > 0 and best_placement.score > best_movement.score:
		return best_placement
	elif best_movement.score > 0:
		return best_movement

	return None

def score_tile_state( tiles, board ):

	# good things:
	#	- pinning opponents pieces
	#	- spaces around bee
	#	- filled positions around opponents bee
	#	- pieces that aren't pinned
	#	- beetle ontop of opponent bee

	score = 0
	# score += score_tiles( get_pinned_opponent_pieces( tiles, board ) )
	# score += score_tiles( get_my_free_pieces( tiles, board ) )
	score += score_tiles( get_my_tiles( tiles, board ), __graph_place_tiles_multiplier.get_for_x( __turn_number ) )
	score += __free_space_around_my_bee_score * count_spaces_around_my_bee( tiles, board )
	score += __graph_filled_space_around_opponent_bee_score.get_for_x( __turn_number ) * \
		count_filled_spaces_around_opponent_bee( tiles, board )

	if beetle_ontop_of_opponent_bee( tiles, board ):
		score += __beetle_ontop_of_opponent_bee_score

	return score

def get_my_tiles( tiles, board ):
	return [ x for x in tiles if x.player == board.get_me() ]

def get_my_unplayed_tile_types( board ):
	unplayed_tile_types = [ x.type for x in board.get_my_unplayed_tiles() ]
	return list( set( unplayed_tile_types ) )

def beetle_ontop_of_opponent_bee( tiles, board ):
	opponent_bee = next( ( x for x in tiles if x.type == TileType.bee and x.player == board.get_opponent() ), None )
	if opponent_bee is not None:
		my_beetles = [ x for x in tiles if x.player == board.get_me() and x.type == TileType.beetle ]

		return opponent_bee.get_position() in ( x.get_position() for x in my_beetles )

	return False

def count_filled_spaces_around_opponent_bee( tiles, board ):
	opponent_bee = next( ( x for x in tiles if x.type == TileType.bee and x.player == board.get_opponent() ), None )
	if opponent_bee is not None:
		filled_spaces = len( [ True for x in opponent_bee.get_position().get_adjacent_positions() \
			if len( get_tiles_with_position( tiles, x ) ) > 0 ] )
		return filled_spaces

	return 0

def count_spaces_around_my_bee( tiles, board ):
	my_bee = next( ( x for x in tiles if x.type == TileType.bee and x.player == board.get_me() ), None )
	if my_bee is not None:
		free_spaces = len( [ True for x in my_bee.get_position().get_adjacent_positions() \
			if len( get_tiles_with_position( tiles, x ) ) == 0 ] )
		return free_spaces

	return 0

def get_tiles_with_position( tiles, position ):
	return [ x for x in tiles if x.get_position() == position ]

def score_tiles( tiles, multiplier = 1 ):
	return sum( __tile_scores[ x.type ].get_for_x( __turn_number ) * multiplier for x in tiles )

def get_pinned_opponent_pieces( tiles, board ):
	opponent_tiles = [ x for x in tiles if x.player == board.get_opponent() ]
	pinned_opponent_tiles = [ x for x in opponent_tiles if tile_is_pinned( x, tiles ) ]
	return pinned_opponent_tiles

def get_my_free_pieces( tiles, board ):
	my_tiles = [ x for x in tiles if x.player == board.get_me() ]
	my_free_tiles = [ x for x in my_tiles if not tile_is_pinned( x, tiles ) ]
	return my_free_tiles

def tile_is_pinned( tile, tiles ):
	# Check that removing the tile doesn't create any islands
	tiles.remove( tile )
	connected_hive = hive_is_connected( tiles )
	tiles.append( tile )

	return not connected_hive

def hive_is_connected( tiles ):
	visited_tiles = []

	if len( tiles ) == 0:
		return True

	def count_island_size( tile ):
		visited_tiles.append( tile )
		adjacent_tiles = get_adjacent_tiles( tile.get_position(), tiles )
		unvisted_adjacent_tiles = [ x for x in adjacent_tiles if x not in visited_tiles ]
		visited_tiles.extend( unvisted_adjacent_tiles )

		size = 1
		for unvisted_adjacent_tile in unvisted_adjacent_tiles:
			size += count_island_size( unvisted_adjacent_tile )

		return size

	return count_island_size( tiles[ 0 ] ) == len( tiles )

def get_adjacent_tiles( position, tiles ):
	return [ x for x in tiles if x.get_position() in position.get_adjacent_positions() ]

def perform_random_move( board ):

	has_tiles_to_place = len( board.get_my_unplayed_tiles() ) > 0

	has_positions_to_place_for_any_tile = any(
			board.get_valid_placements_for_tile( x.type ) for x in board.get_my_unplayed_tiles()
		)

	must_place_tile = \
		( has_tiles_to_place ) and \
		(( len( board.get_my_played_tiles() ) == 0 ) or \
		( no_available_moves( board ) ))

	if must_place_tile:
		perform_random_placement( board )
	else:
		if has_positions_to_place_for_any_tile and has_tiles_to_place and random.choice( [ True, False ] ):
			perform_random_placement( board )
		else:
			perform_random_movement( board )

def perform_random_placement( board ):
	random_unplayed_tile = random.choice( board.get_my_unplayed_tiles() )
	valid_positions_for_tile = board.get_valid_placements_for_tile( random_unplayed_tile.type )

	while len( valid_positions_for_tile ) == 0:
		random_unplayed_tile = random.choice( board.get_my_unplayed_tiles() )
		valid_positions_for_tile = board.get_valid_placements_for_tile( random_unplayed_tile.type )

	board.place_tile( random_unplayed_tile.type, random.choice( valid_positions_for_tile ) )

def perform_random_movement( board ):
	random_tile_in_play = random.choice( board.get_my_played_tiles() )
	valid_positions_for_tile = board.get_valid_movements_for_tile( random_tile_in_play )

	while len( valid_positions_for_tile ) == 0:
		random_tile_in_play = random.choice( board.get_my_played_tiles() )
		valid_positions_for_tile = board.get_valid_movements_for_tile( random_tile_in_play )

	board.move_tile( random_tile_in_play, random.choice( valid_positions_for_tile ) )

def no_available_moves( board ):
	tiles_in_play = board.get_my_played_tiles()
	for tile in tiles_in_play:
		if len( board.get_valid_movements_for_tile( tile ) ) > 0:
			return False

	return True