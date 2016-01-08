from enum import Enum

class Player:
	def __init__( self, player_number ):
		self.__player_number = player_number

	def __eq__( self, other ):
		return self.__player_number == other.get_player_number()

	def __ne__( self, other ):
		return not self.__eq__( other )

	def get_player_number( self ):
		return self.__player_number

	def get_colour( self ):
		return player_colour[ self.__player_number ]

class PlayerNumber( Enum ):
	one = 1
	two = 2

player_colour = {
	PlayerNumber.one : ( 238, 255, 198, 255 ),
	PlayerNumber.two : ( 50, 50, 50, 255 ),
}