import random

def perform_move( board ):

	has_tiles_to_place = len( board.get_my_unplayed_tiles() ) > 0

	must_place_tile = \
		( has_tiles_to_place ) and \
		(( len( board.get_my_played_tiles() ) == 0 ) or \
		( no_available_moves( board ) ))

	if must_place_tile:
		perform_placement( board )
	else:
		if has_tiles_to_place and random.choice( [ True, False ] ):
			perform_placement( board )
		else:
			perform_movement( board )

def perform_placement( board ):
	random_unplayed_tile = random.choice( board.get_my_unplayed_tiles() )
	valid_positions_for_tile = board.get_valid_placements_for_tile( random_unplayed_tile.type )

	while len( valid_positions_for_tile ) == 0:
		random_unplayed_tile = random.choice( board.get_my_unplayed_tiles() )
		valid_positions_for_tile = board.get_valid_placements_for_tile( random_unplayed_tile.type )

	board.place_tile( random_unplayed_tile.type, random.choice( valid_positions_for_tile ) )

def perform_movement( board ):
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