import pygame, time
import config
from tile import TileType
from board import Board
from player import PlayerNumber, Player
from position import Position

display_surface = None

def init():
	pygame.init()
	global display_surface
	display_surface = pygame.display.set_mode( config.screen_dimensions, pygame.DOUBLEBUF, 32 )
	pygame.display.set_caption( config.title )

def main():
	board = Board()

	player_one = Player( PlayerNumber.one )
	player_two = Player( PlayerNumber.two )

	board.place_tile( TileType.ant, Position( [ 1, 0 ] ), player_one )
	board.place_tile( TileType.beetle, Position( [ 0, 1 ] ), player_one )
	board.place_tile( TileType.bee, Position( [ 0, 2 ] ), player_one )
	board.place_tile( TileType.beetle, Position( [ 0, 3 ] ), player_one )
	board.place_tile( TileType.beetle, Position( [ 1, 3 ] ), player_one )
	board.place_tile( TileType.beetle, Position( [ 2 ,3 ] ), player_one )
	board.place_tile( TileType.beetle, Position( [ 3, 2 ] ), player_one )
	board.place_tile( TileType.beetle, Position( [ 3, 1 ] ), player_one )
	board.place_tile( TileType.beetle, Position( [ 3, 0 ] ), player_one )
	board.place_tile( TileType.beetle, Position( [ 2, 0 ] ), player_one )
	gh = board.place_tile( TileType.grass_hopper, Position( [ 1, 4 ] ), player_one )

	board.move_tile( gh, Position( [ -1, 1 ] ) )
	board.move_tile( gh, Position( [ 1, 1 ] ) )
	board.move_tile( gh, Position( [ 2, -1 ] ) )
	board.move_tile( gh, Position( [ 4, 2 ] ) )
	board.move_tile( gh, Position( [ 2, 2 ] ) )
	board.move_tile( gh, Position( [ 1, 4 ] ) )
	board.move_tile( gh, Position( [ -1, 1 ] ) )

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

		pygame.display.update()
		board.update()

		display_surface.fill( ( 10, 10, 10 ) )
		board.render( display_surface )

		time.sleep( 0.1 )

if __name__ == '__main__':
	init()
	main()