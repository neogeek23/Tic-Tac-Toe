import sys
import math
import random
import itertools
from enum import Enum


class PlacementResult(Enum):
	success = 0
	non_numeric_input = 1
	dimension_size_error = 2
	unavailable_placement = 3


class Player:
	# Player is separate from Board in case I ever want to make a bot, at which point players will need to have boards
	# and because I need a mystery player to steal center sometimes
	def __init__(self, index):
		self.__index = index
		self.__move_list = list()

		if index < 0:
			self.__token = "-"
		elif index == 0:
			self.__token = "X"
		else:
			self.__token = "O"

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
				if i > 9:  # lets be honest this will destroy memory; already dies at dim 8, 7 is struggle
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
		elif d < 4:
			header = "\n"
			for i in range(self.__dimensions + 1):
				if i != 0:
					header += "\t"
				header += " {:2s}".format(str(i)[:1])
				for j in range(self.__dimensions + 1):
					header += "| {:2s}".format(str(j)[:1])
			print(header)
			for i in range(self.__dimensions + 1):
				row_string = ""
				for j in range(self.__dimensions + 1):
					if j != 0:
						row_string += "\t"
					row_string += " {:2s}".format(str(i)[:1])
					for k in range(self.__dimensions + 1):
						# One of these days I'll think about why it is j-i-k not i-j-k #madness
						row_string += "| " + list_of_list[j][i][k].get_owner() + " "
				print(row_string)
		else:
			for i in range(self.__dimensions + 1):
				if i < 10:
					print("\n-------" + str(i) + "-------\tDimension:\t" + str(d))
				else:
					print("\n-------" + str(i) + "------\tDimension:\t" + str(d))
				self.__display_recur(list_of_list[i], d - 1)

	def __get_space(self, index_list):
		if len(index_list) != self.__dimensions:  # this is safety that is helpful only in the building process
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
				return PlacementResult.non_numeric_input

		if len(indexes) != self.__dimensions:
			return PlacementResult.dimension_size_error

		if self.__get_space(indexes).place_token(player.get_token()):
			self.__round += 1
			self.__winner = self.__is_winning_move(coordinate, player)
			player.save_move(coordinate)
			return PlacementResult.success
		else:
			return PlacementResult.unavailable_placement

	def __get_random_coordinate(self, start, stop):
		result = ""
		for i in range(self.__dimensions):
			result += str(random.randrange(start, stop))
			if i < self.__dimensions - 1:
				result += "."
		return result

	def get_center_coordinates(self):
		# this will only be called for odd dimensions, it should probably have some more safety on it
		center = self.__dimensions / 2
		return self.__get_random_coordinate(center, center + 1)

	def place_random(self, token):
		return self.place_token(self.__get_random_coordinate(0, self.__dimensions + 1), token)

	def __is_winning_move(self, coordinate, player):
		coord_list = list()
		for s in coordinate.split("."):
			coord_list.append(int(s))

		freedom_set = self.__get_dimension_locks()
		intersecting_pathsets = self.__get_winning_paths(coord_list, freedom_set)

		# we want to look through all of the found possible paths a placed token in a space could finish a continuous
		# streak and see if it did
		for paths in intersecting_pathsets:
			for path in paths:
				solution_in_path = True
				for space in path:
					solution_in_path = solution_in_path and self.__get_space(space).get_owner() == player.get_token()
				if solution_in_path:
					self.__winning_path = path
					return player.get_id()
		return None

	def __get_dimension_locks(self):
		# This gets all unique permutations of True-False for each dimension so 2^n elements
		# This is used to create a matrix of all the possible cross sections of a n-space
		# This is also used to pattern all the ways to manipulate a 1-dimensional element, increase/decrease it
		final = list()
		initial = list()

		for i in range(self.__dimensions):
			initial.append(True)

		for i in range(len(initial)):  # Don't do +1 b/c +1 item will get all False, which will mean the 0th dimension
			if i > 0:
				initial[i - 1] = False
			for j in list(itertools.permutations(initial)):
				temp = list()
				for k in list(j):
					temp.append(k)
				if temp not in final:
					final.append(temp)
		return final

	def __get_winning_paths(self, coord_list, freedoms):
		path_set = list()
		# This will get all possible paths that are n+1 long from the starting point
		for freedom in freedoms:  # Each freedom is a permutation of whether each dimension should change
			result = list()
			for edit_pattern in freedoms:  # Each edit_pattern is a permutation of how to change each dimension
				patterned_edit = list()
				for i in range(self.__dimensions + 1):  # dim + 1 i is number of spaces for a continuous streak
					temp = coord_list.copy()  # we want a new memory location to edit our coord for a new coord
					for j in range(len(temp)):  # j is which dimension in our new coord we are manipulating
						if freedom[j]:
							if edit_pattern[j]:
								# We want to increase or decrease such that we are always between 0 and the dimension.
								# Doing this will create a wraparound problem though e.g. (1,0),(0,1),(2,2). We will
								# abstain from including these soon. We also want to only shift in a dimension by a
								# single space.
								temp[j] = (temp[j] + i + (self.__dimensions + 1)) % (self.__dimensions + 1)
							else:
								temp[j] = (temp[j] - i - (self.__dimensions + 1)) % (self.__dimensions + 1)
					patterned_edit.append(temp)
				# we only want unique coordinate sets and we do not want wraparounds or other non-continuous paths
				if patterned_edit not in result and self.__is_path_continuous(patterned_edit, freedom):
					result.append(patterned_edit)
			# we only want unique coordinate groups
			if result not in path_set:
				path_set.append(result)
		return path_set

	def __is_path_continuous(self, path, freedoms):
		# This will prune out impossible paths (paths that wrap around the space)
		# Though this could be static, it doesn't make sense as static, so I haven't made it so.
		slope_is_legit = True
		# We want to look at each element in a list against every other element in that list, except itself so it is a
		# for i for j where i != j kind of thing - this is more detail that necessary in a comment, the so it is a part
		for i in range(len(path)):
			found_a_slope_buddy = False
			for j in range(len(path)):
				if i != j:
					point_has_good_slope = True
					for k in range(len(path[i])):
						if freedoms[k]:  # we include freedom because a dimension may be "locked", which means we
							# may be looking at a victory path in some dimension r (such that r < n) cross section, when
							# this is the case we don't want to check if there is a change of 1 in those dimensions that
							# are locked because there will be a change of 0 and the test will give us a false negative
							point_has_good_slope = point_has_good_slope and abs(path[i][k] - path[j][k]) == 1
					found_a_slope_buddy = found_a_slope_buddy or point_has_good_slope
			slope_is_legit = slope_is_legit and found_a_slope_buddy
		return slope_is_legit

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


def main():
	board = create_board_from_inputs()
	play_tic_tac_toe(board)


def create_board_from_inputs():
	print(
		"\nWelcome to multidimensional Tic-Tac-Toe!\n\nThe board will contain (n+1)^n spaces for n dimensions.\nFor "
		"even dimensions starting with the 4th dimension, the center space can be setup to be unplayable.\nClaim n+1 "
		"spaces in a continuous streak to win!\n")
	difficulty_attempts = 1
	max_attempts = 3
	difficulty = input("How many dimensions of Tic Tac Toe would you like to attempt? ")

	while not difficulty.isnumeric() and difficulty_attempts < max_attempts:
		difficulty_attempts += 1
		print("Remaining attempts: " + str(max_attempts - difficulty_attempts) + ", failure will result in termination.")
		difficulty = input(
			"We require more integers for dimension count.  How many dimensions of tic tac toe would you "
			"like to attempt? ")

	if difficulty_attempts >= max_attempts and not difficulty.isnumeric():
		print("Let me know when you find your number pad.  Please come again.")
		sys.exit()

	dimension = int(difficulty)
	if dimension < 2:
		print(
			"Tic Tac Toe requires at least 2 dimensions and you chose " + difficulty + ", so we will use 2 dimensions.")
		dimension = 2
	else:
		print("You have requested a board of " + str(int(math.pow(dimension + 1, dimension))) + " spaces.")
		if dimension > 5:
			print("This is a very large board.  It may take some time to create.")

	board = Board(dimension)
	if dimension > 2 and dimension % 2 == 0:
		middle_attempts = 1
		center_selectable = input("Do you want the center most space selectable (Y/N)? ")

		while not (center_selectable == "Y" or center_selectable == "N") and middle_attempts < max_attempts:
			middle_attempts += 1
			print("Remaining attempts: " + str(max_attempts - middle_attempts) + ", failure will result in termination.")
			center_selectable = input(
				"Y/N type input is required. Do you want the center most space selectable (Y/N)? ")

		if not (center_selectable == "Y" or center_selectable == "N") and middle_attempts >= max_attempts:
			print("Let me know when you find your 'Y' and 'N' keys.  Please come again.")
			sys.exit()

		if center_selectable == "N":
			# Player(-1) is a player for the board to claim the center location
			board.place_token(board.get_center_coordinates(), Player(-1))  # This is half why Player is not a subclass
	return board


def play_tic_tac_toe(board):
	turn = 0
	while not board.is_full() and not board.has_winner():
		board.display()
		player_to_play = turn % 2
		move_attempts = 1
		max_attempts = 3
		coordinate_move = input(
			"\nPlayer " + str(player_to_play + 1) +
			" please input coordinates (<nth index>.<nth - 1 index>. ... .<3rd index>.<rows>.<cols>) to place your '" +
			board.players[player_to_play].get_token() + "' token: ")
		move_result = board.place_token(coordinate_move, board.players[player_to_play])

		while move_result != PlacementResult.success and move_attempts < max_attempts:
			if move_result == PlacementResult.non_numeric_input:
				print("Input Error on Coordinate.  There is a non-integer type between the '.' separators.")
			if move_result == PlacementResult.dimension_size_error:
				s = "Input Error on Coordinate.  The number of indexes in your coordinate does not match the dimension."
				print(s)
			if move_result == PlacementResult.unavailable_placement:
				print("Input Error on Coordinate.  That space is already claimed.")
			s = "Remaining attempts: " + str(max_attempts - move_attempts)
			s += ", failure will result in random placement."
			print(s)
			s = "\nPlayer " + str(player_to_play + 1)
			s += " please input coordinates (<nth index>.<nth - 1 index>. ... .<3rd index>.<rows>.<cols>) to place "
			s += "your '" + board.players[player_to_play].get_token() + "' token: "
			coordinate_move = input(s)
			move_attempts += 1
			move_result = board.place_token(coordinate_move, board.players[player_to_play])

		if move_result != PlacementResult.success and move_attempts >= max_attempts:
			while move_result != PlacementResult.success:
				move_result = board.place_random(board.players[player_to_play])
		turn += 1

	# Reporting on End of Game
	board.display()
	if board.is_full():
		print("Board has filled and no victor has been found.  Game Over.  Thanks for playing, try again.")

	if board.has_winner():
		s = "\nVictory to Player " + str(board.players[board.get_winner()].get_id() + 1)
		s += " - respect.  The " + board.players[board.get_winner()].get_token()
		s += "'s win!\nThe winning path contains:\n" + board.get_winning_path()
		s += "\nGame Over.  Thanks for playing, play again."
		print(s)

main()
