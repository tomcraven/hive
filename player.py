from tile import Tile, TileType
import imp

class Player:
	def __init__( self, player_number, ai_file ):
		self.__player_number = player_number

		self.__ai_perform_move = imp.load_source( "", ai_file ).perform_move
		self.__ai_file = ai_file
		assert self.__ai_perform_move is not None

		self.tiles = [
			Tile.create( TileType.bee, self ),

			Tile.create( TileType.beetle, self ),
			Tile.create( TileType.beetle, self ),

			Tile.create( TileType.spider, self ),
			Tile.create( TileType.spider, self ),

			Tile.create( TileType.ant, self ),
			Tile.create( TileType.ant, self ),
			Tile.create( TileType.ant, self ),

			Tile.create( TileType.grass_hopper, self ),
			Tile.create( TileType.grass_hopper, self ),
			Tile.create( TileType.grass_hopper, self ),
		]

	def __eq__( self, other ):
		return self.__player_number == other.get_player_number()

	def __ne__( self, other ):
		return not self.__eq__( other )

	def __str__( self ):
		return "Player " + str( self.__player_number ) + " [" + self.__ai_file + "]"

	def get_player_number( self ):
		return self.__player_number

	def get_colour( self ):
		return player_colour[ self.__player_number ]

	def perform_move( self, board ):
		self.__ai_perform_move( board )

	def get_new_tile( self, tile_type, board ):
		unplayed_tile_with_type = next( ( x for x in self.tiles \
			if x.type == tile_type and \
			not board.tile_in_play( x ) ), None )

		return unplayed_tile_with_type

class PlayerNumber:
	one = 1
	two = 2

player_colour = {
	PlayerNumber.one : ( 238, 255, 198, 255 ),
	PlayerNumber.two : ( 50, 50, 50, 255 ),
}