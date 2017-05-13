import sys
import math
import random
import itertools


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
				if i > 9:  # lets be honest 100^99 will destroy memory; already dies a dim 8, 7 is struggle
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
			if i < self.__dimensions - 1:
				result += "."
		return result

	def get_center_coordinates(self):
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

		for i in range(len(initial)):
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
		# This will get all possible paths that are 5 long from the starting point
		for freedom in freedoms:
			result = list()
			for edit_pattern in freedoms:
				patterned_edit = list()
				for i in range(self.__dimensions + 1):
					temp = coord_list.copy()
					for j in range(len(temp)):
						if freedom[j]:
							if edit_pattern[j]:
								temp[j] = (temp[j] + i + (self.__dimensions + 1)) % (self.__dimensions + 1)
							else:
								temp[j] = (temp[j] - i - (self.__dimensions + 1)) % (self.__dimensions + 1)
					patterned_edit.append(temp)
				if patterned_edit not in result and self.__is_path_continuous(patterned_edit, freedom):
					result.append(patterned_edit)
			if result not in path_set:
				path_set.append(result)
		return path_set

	def __is_path_continuous(self, path, freedoms):
		# This will prune out impossible paths (paths that wrap around the space)
		# Though this could be static, it doesn't feel right as static, so I haven't made it so.
		slope_is_legit = True
		for i in range(len(path)):
			found_a_slope_buddy = False
			for j in range(len(path)):
				if i != j:
					point_has_good_slope = True
					for k in range(len(path[i])):
						if freedoms[k]:
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

# Setup Inputs
print("\nWelcome to multidimensional Tic-Tac-Toe!\n\nThe board will contain (n+1)^n spaces for n dimensions.\nFor even "
	  "dimensions starting with the 4th dimension, the center space can be setup to be unplayable.\nClaim n+1 "
	  "spaces in a continuous streak to win!\n")
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
							"index>. ... .<3rd index>.<rows>.<cols>) to place your '"
							+ board.players[player_to_play].get_token() + "' token: ")
	move_result = board.place_token(coordinate_move, board.players[player_to_play])
	while move_result > 0 and move_attempts < 3:
		if move_result == 1:
			print("Input Error on Coordinate.  There is a non-integer type between the '.' separators.")
		if move_result == 2:
			print("Input Error on Coordinate.  There are not enough indexes for each dimension.")
		if move_result == 3:
			print("Input Error on Coordinate.  There space described by coordinate is already claimed.")
		print("Remaining attempts:  " + str(3 - move_attempts) + " failure will result in random placement.")
		coordinate_move = input("\nPlayer " + str(player_to_play + 1) + " please input coordinates (<nth index>.<nth "
								"- 1 index>. ... .<3rd index>.<rows>.<cols>) to place your '"
								+ board.players[player_to_play].get_token() + "' token: ")
		move_attempts += 1
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
