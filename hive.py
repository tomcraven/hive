import pygame, time
import config
from tile import TileType
from board import Board
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
	random_seed = int( time.time() * 1000 )
	print "seeding random with", random_seed
	random.seed( random_seed )

	player_one = Player( PlayerNumber.one, sys.argv[ 1 ] )
	player_two = Player( PlayerNumber.two, sys.argv[ 2 ] )

	board = Board( player_one, player_two )

	winning_player = None
	while winning_player is None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

		pygame.display.update()
		board.update()
		winning_player = board.get_winner()

		display_surface.fill( ( 10, 10, 10 ) )
		board.render( display_surface )

		time.sleep( 0.01 )

	print winning_player, "has won"

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

		pygame.display.update()
		display_surface.fill( ( 10, 10, 10 ) )
		board.render( display_surface )

		time.sleep( 0.01 )

if __name__ == '__main__':

	if len( sys.argv ) != 3:
		raise ValueError( "Pass in the AI files like this - python hive.py ai_1.py ai_2.py" )

	init()
	main()