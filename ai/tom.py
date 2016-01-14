import random

import sys
sys.path.append( "../" )
from tile import TileType

turn_number = 0

def perform_move( board ):

	if not board.has_performed_move():
		perform_random_move( board )

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