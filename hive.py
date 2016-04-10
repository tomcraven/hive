import pygame, time
import config
from tile import TileType
from board import Board, BoardState
from player import PlayerNumber, Player
from position import Position
import sys, random

display_surface = None

def init():
	pygame.init()
	global display_surface
	display_surface = pygame.display.set_mode( config.screen_dimensions, pygame.DOUBLEBUF, 32 )
	pygame.display.set_caption( config.title )

def main():
	random_seed = 1460297195956#int( time.time() * 1000 )
	print "seeding random with", random_seed
	random.seed( random_seed )

	player_one = Player( PlayerNumber.one, sys.argv[ 1 ] )
	player_two = Player( PlayerNumber.two, sys.argv[ 2 ] )

	board = Board( player_one, player_two )

	board_state = board.get_state()
	while board_state != BoardState.game_finished:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

		pygame.display.update()
		board.update()
		board_state = board.get_state()

		display_surface.fill( ( 10, 10, 10 ) )
		board.render( display_surface )

		time.sleep( 0.01 )

	winning_player = board.get_winner()
	if winning_player is None:
		print "Game is a tie"
	else:
		print winning_player, "has won"


	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

		pygame.display.update()
		display_surface.fill( ( 10, 10, 10 ) )
		board.render( display_surface )

		time.sleep( 0.1 )

if __name__ == '__main__':

	if len( sys.argv ) != 3:
		raise ValueError( "Pass in the AI files like this - python hive.py ai_1.py ai_2.py" )

	init()
	main()
