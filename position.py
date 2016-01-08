class Position( object ):
	def __init__( self, coordinate = None ):
		self.__coordinate = coordinate

	def __eq__( self, other ):
		return \
			self.__coordinate[ 0 ] == other.__coordinate[ 0 ] and \
			self.__coordinate[ 1 ] == other.__coordinate[ 1 ]

	def __str__( self ):
		return str( self.__coordinate )

	def set( self, new_position ):
		self.__coordinate = new_position.__coordinate

	def get( self ):
		return self.__coordinate[ : ]

	def is_even_row( self ):
		return ( self.__coordinate[ 1 ] % 2 ) == 0

	def east( self ):
		return Position( [ self.__coordinate[ 0 ] + 1, self.__coordinate[ 1 ] ] )

	def west( self ):
		return Position( [ self.__coordinate[ 0 ] - 1, self.__coordinate[ 1 ] ] )

	def north_west( self ):
		if self.is_even_row():
			return Position( [ self.__coordinate[ 0 ] - 1, self.__coordinate[ 1 ] - 1 ] )
		return Position( [ self.__coordinate[ 0 ], self.__coordinate[ 1 ] - 1 ] )

	def north_east( self ):
		if self.is_even_row():
			return Position( [ self.__coordinate[ 0 ], self.__coordinate[ 1 ] - 1 ] )
		return Position( [ self.__coordinate[ 0 ] + 1, self.__coordinate[ 1 ] - 1 ] )

	def south_west( self ):
		if self.is_even_row():
			return Position( [ self.__coordinate[ 0 ] - 1, self.__coordinate[ 1 ] + 1 ] )
		return Position( [ self.__coordinate[ 0 ], self.__coordinate[ 1 ] + 1 ] )

	def south_east( self ):
		if self.is_even_row():
			return Position( [ self.__coordinate[ 0 ], self.__coordinate[ 1 ] + 1 ] )
		return Position( [ self.__coordinate[ 0 ] + 1, self.__coordinate[ 1 ] + 1 ] )

	def get_adjacent_positions( self ):
		return [
			self.east(),
			self.west(),
			self.north_west(),
			self.north_east(),
			self.south_west(),
			self.south_east()
		]