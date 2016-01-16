import random

import sys
sys.path.append( "../" )
from tile import TileType

turn_number = 0

def perform_move( board ):
	global turn_number
	turn_number += 1
	if turn_number == 2:
		board.place_tile( TileType.bee, 
			board.get_valid_placements_for_tile( TileType.bee )[ 0 ] )
		return

	opponent_bee = get_opponent_bee( board )
	if opponent_bee is not None:
		opponent_bee_adjacent_positions = opponent_bee.get_position().get_adjacent_positions()
		tiles = get_tiles_with_possible_move_positions( board, opponent_bee_adjacent_positions )

		# remove tiles that are already adjacent to the opponents bee and tiles that are our bee
		tiles = [ t for t in tiles if \
			t.get_position() not in opponent_bee_adjacent_positions and \
			t.type != TileType.bee ]

		if len( tiles ) > 0:
			tile_to_move = tiles[ 0 ]
			possible_target_positions = [ x for x in board.get_valid_movements_for_tile( tile_to_move ) if x in opponent_bee_adjacent_positions ]
			board.move_tile( tile_to_move, possible_target_positions[ 0 ] )
			return

		tiles_adjacent_to_opponent_bee = []
		for position in opponent_bee_adjacent_positions:
			tiles_adjacent_to_opponent_bee.extend( board.get_tiles_with_position( position ) )

		# remove tiles that aren't ours
		tiles_adjacent_to_opponent_bee = [ x for x in tiles_adjacent_to_opponent_bee if x in board.get_my_played_tiles() ]

		# find tiles in play that aren't next to the opponents bee and that aren't my bee
		tiles_not_adjacent_to_opponent_bee = [ x for x in board.get_my_played_tiles() if \
			x not in tiles_adjacent_to_opponent_bee and \
			x.type != TileType.bee ]

		if len( tiles_not_adjacent_to_opponent_bee ) > 0:
			if len( board.get_my_unplayed_tiles() ) > 0:
				perform_random_placement( board )
			else:
				move_any_tile( board, tiles_not_adjacent_to_opponent_bee )
	else:
		perform_random_placement( board )

	if not board.has_performed_move():
		perform_random_move( board )
		return

def move_any_tile( board, tiles ):
	random.shuffle( tiles )
	for tile in tiles:
		potential_movements = board.get_valid_movements_for_tile( tile )
		if len( potential_movements ) > 0:
			random_move = random.choice( potential_movements )
			board.move_tile( tile, random_move )
			return

def get_tiles_with_possible_move_positions( board, target_positions ):
	ret = []
	for tile in board.get_my_played_tiles():
		positions = board.get_valid_movements_for_tile( tile )

		if any( x in target_positions for x in positions ):
			ret.append( tile )
	return ret

def get_opponent_bee( board ):
	opponent_played_tiles = board.get_opponent_played_tiles()
	for tile in opponent_played_tiles:
		if tile.type == TileType.bee:
			return tile
	return None

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