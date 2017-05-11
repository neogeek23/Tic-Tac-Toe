import sys
import math
import random


class Player:
	def __init__(self, index):
		self.__index = index
		self.__move_list = list()

		if index < 0:
			self.__token = "-"
		elif index == 0:
			self.__token = "O"
		else:
			self.__token = "X"

	def get_id(self):
		return self.__index

	def get_token(self):
		return self.__token

	def save_move(self, move):
		self.__move_list.append(move)

	def get_move_history(self):
		return self.__move_list

	def get_last_move(self):
		return self.__move_list[len(self.__move_list)]


class Board:
	class Space:
		def __init__(self):
			self.__owner = " "  # This means unclaimed

		def place_token(self, owner):
			if self.__owner == " ":	 # If unclaimed
				self.__owner = owner
				return True
			else:
				return False

		def get_owner(self):
			return self.__owner

	def __init__(self, dimensions):
		self.__dimensions = dimensions
		self.players = [Player(0), Player(1)]
		self.__spaces = self.__board_creator(dimensions)
		self.__round = 0
		self.__winner = None
		self.__winning_path = list()

	def __board_creator(self, dimensions):
		result = list()
		for i in range(self.__dimensions + 1):
			if dimensions == 1:
				result.append(self.Space())
			if dimensions > 1:
				result.append(self.__board_creator(dimensions - 1))
		return result

	def is_full(self):
		return self.__round == math.pow(self.__dimensions + 1, self.__dimensions)

	def has_winner(self):
		return self.__winner is not None

	def get_winner(self):
		return self.__winner

	def display(self):
		self.__display_recur(self.__spaces, self.__dimensions)

	def __display_recur(self, list_of_list, d):
		if d < 3:
			header = "\n   "
			for i in range(self.__dimensions + 1):
				if i > 9:  # lets be honest 100^99 will destroy memory
					header += "| " + str(i)
				else:
					header += "| " + str(i) + " "
			print(header)
			for i in list_of_list:
				row_string = " " + str(list_of_list.index(i))
				if list_of_list.index(i) < 10:
					row_string += " "
				for j in i:
					row_string += "| " + j.get_owner() + " "
				print(row_string)
		else:
			for i in range(self.__dimensions + 1):
				if i < 10:
					print("\n-------" + str(i) + "-------\tDimension:\t" + str(d))
				else:
					print("\n-------" + str(i) + "------\tDimension:\t" + str(d))
				self.__display_recur(list_of_list[i], d - 1)

	def __get_space(self, index_list):
		if len(index_list) != self.__dimensions:
			print("\nCoordinates for a space were impossible.")
			return None
		else:
			int_indexes = list()
			for i in index_list:
				int_indexes.append(int(i))
			return self.__get_space_recur(self.__spaces, int_indexes)

	def __get_space_recur(self, list_of_lists, index_list):
		if len(index_list) == 1:
			return list_of_lists[int(index_list[0])]
		else:
			return self.__get_space_recur(list_of_lists[index_list[0]], index_list[1:])

	def place_token(self, coordinate, player):
		indexes = coordinate.split(".")

		for index in indexes:
			if not index.isnumeric():
				return 1  # This will be a key value to denote a failure of type

		if len(indexes) != self.__dimensions:
			return 2  # This will be a key value to denote a failure of quantity

		if self.__get_space(indexes).place_token(player.get_token()):
			self.__round += 1
			self.__winner = self.__is_winning_move(coordinate, player)
			player.save_move(coordinate)
			return 0  # This will be a key value to denote ultimate success
		else:
			return 3  # This will be a key value to denote a occupancy of space

	def __get_random_coordinate(self, start, stop):
		result = ""
		for i in range(self.__dimensions):
			result += str(random.randrange(start, stop))
			if i < self.__dimensions:
				result += "."
		return result

	def get_center_coordinates(self):
		center = self.__dimensions / 2
		return self.__get_random_coordinate(center, center + 1)

	def place_random(self, token):
		return self.place_token(self.__get_random_coordinate(0, self.__dimensions + 2), token)

	def __is_winning_move(self, coordinate, player):
		intersecting_paths = list()
		indexes = list()

		for i in coordinate.split("."):
			indexes.append(int(i))

		# Get all of the coordinate for straight (single dimension change) paths that intersect our coordinate
		for i in range(self.__dimensions):
			temp_list = list()
			for j in range(self.__dimensions + 1):
				temp_coord = indexes.copy()
				temp_coord[i] = j
				temp_list.append(temp_coord)
			intersecting_paths.append(temp_list)

		# Attempt to build all possible diagonal (multiple dimension change) paths that intersect our coordinate
		# I feel like this might be over kill but with no limits on dimensions it gets confusing, better safe
		intersecting_paths += self.__get_diagonals(indexes, -1, 1)
		intersecting_paths += self.__get_diagonals(indexes, 1, -1)
		intersecting_paths += self.__get_diagonals(indexes, -1, -1)
		intersecting_paths += self.__get_diagonals(indexes, 1, 1)

		for path in intersecting_paths:
			solution_in_path = True
			for space in path:
				solution_in_path = solution_in_path and self.__get_space(space).get_owner() == player.get_token()
			if solution_in_path:
				self.__winning_path = path
				return player.get_id()
		return None

	# This will produce a list of all possible diagonals of a given coordinate set
	def __get_diagonals(self, indexes, up, dn):
		intersecting_paths = list()
		for i in range(self.__dimensions - 1):  # For each dimension less the first, no one cares about that
			temp_list = list()
			for j in range(self.__dimensions + 1):  # For each coordinate in a path, since 1 extra we do + 1
				if j == 0:
					temp_coord = indexes.copy()
				else:
					temp_coord = temp_list[j - 1].copy()
				if j > 0:  # by skipping the first item, ensure our coordinate is included
					for k in range(self.__dimensions - i):  # For each point in a coordinate
						if indexes[k + i] >= self.__dimensions / 2:  # Below ensures any coordinate in range
							temp_coord[k + i] += up + (self.__dimensions + 1 if temp_coord[k + i] + up < 0 else 0) \
										- (self.__dimensions + 1 if temp_coord[k + i] + up > self.__dimensions else 0)
						else:
							temp_coord[k + i] += dn + (self.__dimensions + 1 if temp_coord[k + i] + dn < 0 else 0) \
										- (self.__dimensions + 1 if temp_coord[k + i] + dn > self.__dimensions else 0)
				if 0 < i:
					dim_locked_coord = indexes[:i] + temp_coord[i:]	 # Should be allowing dimensional cross sections
				else:
					dim_locked_coord = temp_coord
				temp_list.append(dim_locked_coord)
			include_in_temp_list = self.__is_slope_correct(temp_list, i)  # Skip indexes below i for cross section
			if include_in_temp_list:
				intersecting_paths.append(temp_list)
		return intersecting_paths

	# This will determine if the change in between all coordinate sets in a coordinate group is equal by ensuring that
	# for each coordinate set in a coordinate group there is another coordinate set in which the difference between them
	# is a net of 1 for each coordinate in of the coordinate sets
	@staticmethod
	def __is_slope_correct(coord_list, index_start):
		slope_is_correct = True
		for i in range(len(coord_list)):
			found_a_slope_match = False
			for j in range(len(coord_list)):
				if i != j:
					this_point_in_slope = True
					for k in range(len(coord_list[i])):
						if k >= index_start:
							this_point_in_slope = this_point_in_slope and abs(coord_list[i][k] - coord_list[j][k]) == 1
					found_a_slope_match = found_a_slope_match or this_point_in_slope
			slope_is_correct = slope_is_correct and found_a_slope_match
		return slope_is_correct

	def get_winning_path(self):
		result = ""
		for coord in self.__winning_path:
			result += "("
			index = 0
			for p in coord:
				index += 1
				result += str(p)
				if index != len(coord):
					result += " "
			result += ")\n"
		return result

# Setup Inputs
print("\nWelcome to multidimensional Tic-Tac-Toe!\n\nThe board will contain (n+1)^n for n dimensions.\nFor even "
	  "dimensions starting with the 4th dimension, the center space can be setup to be unplayable.\nClaim n+1 "
	  "spaces in a row to win!\n")
difficulty_attempts = 1
difficulty = input("How many dimensions of Tic Tac Toe would you like to attempt? ")

while not difficulty.isnumeric() and difficulty_attempts < 3:
	difficulty_attempts += 1
	print("Remaining attempts:  " + str(3 - difficulty_attempts) + " failure will result in termination.")
	difficulty = input("We require more integers for dimension count.  How many dimensions of tic tac toe would you "
					   "like to attempt? ")

if difficulty_attempts >= 3 and not difficulty.isnumeric():
	print("Let me know when you find your number pad.  Please come again.")
	sys.exit()

dimension = int(difficulty)
if dimension < 2:
	print("Tic Tac Toe requires at least 2 dimensions and you chose " + difficulty + ", so we will use 2 dimensions.")
	dimension = 2

board = Board(dimension)
if dimension > 2 and dimension % 2 == 0:
	middle_attempts = 1
	center_selectable = input("Do you want the center most space selectable (Y/N)? ")

	while not (center_selectable == "Y" or center_selectable == "N") and middle_attempts < 3:
		middle_attempts += 1
		print("Remaining attempts:  " + str(3 - middle_attempts) + " failure will result in termination.")
		center_selectable = input("Y/N type input is required. Do you want the center most space selectable (Y/N)? ")

	if not (center_selectable == "Y" or center_selectable == "N") and middle_attempts >= 3:
		print("Let me know when you find your 'Y' and 'N' keys.  Please come again.")
		sys.exit()

	if center_selectable == "N":
		# Player(-1) is a player for the board to claim the center location
		board.place_token(board.get_center_coordinates(), Player(-1))  # This will always work #usefulcomments

# Actually Playing the game
turn = 0
while not board.is_full() and not board.has_winner():
	board.display()
	player_to_play = turn % 2
	move_attempts = 1
	coordinate_move = input("\nPlayer " + str(player_to_play + 1) + " please input coordinates (<nth index>.<nth - 1 "
																  "index>. ... .<3rd index>.<rows>.<cols>) of move: ")
	move_result = board.place_token(coordinate_move, board.players[player_to_play])
	while move_result > 0 and move_attempts < 3:
		if move_result == 1:
			print("Input Error on Coordinate.  There is a non-integer type between the '.' separators.")
		if move_result == 2:
			print("Input Error on Coordinate.  There are not enough indexes for each dimension.")
		if move_result == 3:
			print("Input Error on Coordinate.  There space described by coordinate is already claimed.")
		print("Remaining attempts:  " + str(3 - move_attempts) + " failure will result in random placement.")
		coordinate_move = input("Player " + str(player_to_play + 1) + " please input coordinates (<nth index>.<nth - 1 "
																	"index>. ... .<3rd index>.<rows>.<cols>) of move: ")
		move_result = board.place_token(coordinate_move, board.players[player_to_play])

	if move_result > 0 and move_attempts >= 3:
		move_result = board.place_random(board.players[player_to_play])
		while move_result > 0:
			move_result = board.place_random(board.players[player_to_play])

	turn += 1

# Reporting on End of Game
board.display()
if board.is_full():
	print("Board has filled a no victor has been found.  Game Over.  Thanks for playing, try again.")

if board.has_winner():
	print("\nVictory to Player " + str(board.players[board.get_winner()].get_id() + 1) + " - respect.  The "
		+ board.players[board.get_winner()].get_token() + "'s win!\nThe winning path is:\n" + board.get_winning_path()
		+ "\nGame Over.  Thanks for playing, play again.")
