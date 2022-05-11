from re import S
import Main as Main
"""
Stores information about the current game, detects legal moves, logs moves, etc
"""
class GameState():
	def __init__(self) -> None:
		#board: 8x8 2d list of str (2chr)
		#N = Nero, B = Bianco, Torre Alfiere Cavallo Queen King Pedone
		self.board = [
			["BT", "BC", "BA", "BQ", "BK", "BA", "BC", "BT"], #A Bianco 
			["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"], #B
			["--", "--", "--", "--", "--", "--", "--", "--"], #C
			["--", "--", "--", "--", "--", "--", "--", "BK"], #D
			["NK", "--", "--", "--", "NQ", "--", "--", "--"], #E
			["--", "--", "--", "--", "--", "--", "--", "--"], #F
			["NP", "NP", "NP", "NP", "NP", "NP", "NP", "NP"], #G
			["NT", "NC", "NA", "NQ", "NK", "NA", "NC", "NT"], #H Nero 
		]
		self.whiteMoves = True
		self.moveLog = []
		self.moveFunctions = {
			'P': self.getPMoves,
			'T': self.getTMoves,
			'C': self.getCMoves,
			'A': self.getAMoves,
			'Q': self.getQMoves,
			'K': self.getKMoves
		}

	def makeMove(self, move):
		"""
		Makes a move and logs it
		
		:param move: the move to be made
		"""
		#we can assume the move is valid
		self.board[move.startRow][move.startCol] = "--"
		self.board[move.endRow][move.endCol] = move.pieceMoved
		self.moveLog.append(move)
		self.whiteMoves = not self.whiteMoves

	def undoMove(self):
		"""
		Undo last move
		"""
		if (len(self.moveLog) != 0):
			lastMove = self.moveLog.pop()
			self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
			self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
			self.whiteMoves = not self.whiteMoves

	def getValidMoves(self):
		#All moves considering checks (if you move a piece do you expose the K?)
		return self.getAllPossibleMoves() #temp.
		
	def getAllPossibleMoves(self):
		Main.mPrint('FUNC', 'Generating moves:')
		#generating the moves
		moves = []
		for r in range(len(self.board)):  #foreach col
			for c in range(len(self.board[r])): #foreach row (of col)
				pieceColor = self.board[r][c][0]
				if (pieceColor == "B" and self.whiteMoves) or (pieceColor == "N" and not self.whiteMoves):
					piece = self.board[r][c][1]
					self.moveFunctions[piece](r,c,moves) #calls getXMoves
		
		return moves
	
	#oh boy here we go

	def getPMoves(self, r, c, moves):   #FIXME #TODO (maybe join white and blacks ifs since they are similar)
		#FIXME when pawn reaches end of the board it throws IndexOutOfRange, fix adding pawn promotions
		#TODO promotion, castling, en passant
		if self.whiteMoves: #pedoni bianchi
			#is the square in front empty?
			if self.board[r+1][c] == "--":
				moves.append(Move((r, c), (r+1, c), self.board))
				if r == 1 and self.board[r+2][c] == "--": #If it's the first move can go 2 up
					moves.append(Move((r, c), (r+2, c), self.board))

			if c != len(self.board[r])-1: #piece is not on the last column
				if self.board[r+1][c+1] != "--" and self.board[r+1][c+1][0] != "B": #can eat top right if not white (Bianco)
					moves.append(Move((r, c), (r+1, c+1), self.board))

			if c != 0: #piece is not on the first column
				if self.board[r+1][c-1] != "--" and self.board[r+1][c-1][0] != "B": #can eat top left if not white
					moves.append(Move((r, c), (r+1, c-1), self.board))     

		else: #pedoni  neri
			#is the square in front empty?
			if self.board[r-1][c] == "--":
				moves.append(Move((r, c), (r-1, c), self.board))
				if r == 6 and self.board[r-2][c] == "--": #If it's the first move can go 2 up
					moves.append(Move((r, c), (r-2, c), self.board))

			if c != len(self.board[r]) -1: #piece is not on the last column
				if self.board[r-1][c+1] != "--" and self.board[r+1][c+1][0] != "N": #can eat top right if not black (Nero)
					moves.append(Move((r, c), (r-1, c+1), self.board))

			if c != 0: #piece is not on the first column
				if self.board[r-1][c-1] != "--" and self.board[r-1][c-1][0] != "N": #can eat top left if not black
					moves.append(Move((r, c), (r-1, c-1), self.board))

		return moves

	def getTMoves(self, r, c, moves):	
		enemy = 'N' if self.whiteMoves else 'B'

		for up in range(r+1, len(self.board)):
			if self.board[up][c] == "--": #if next up is empty
				moves.append(Move((r, c), (up, c), self.board))
			elif self.board[up][c][0] == enemy: #if next is enemy
				moves.append(Move((r, c), (up, c), self.board))
				break
			else: #if next up is a friend piece
				break
		for down in range(r-1, -1, -1):
			if self.board[down][c] == "--": #if next down is empty
				moves.append(Move((r, c), (down, c), self.board))
			elif self.board[down][c][0] == enemy: #if next is enemy
				moves.append(Move((r, c), (down, c), self.board))
				break
			else: #if next down is a friend piece
				break
		for right in range(c+1, len(self.board[r])):
			if self.board[r][right] == "--": #if next right is empty
				moves.append(Move((r, c), (r, right), self.board))
			elif self.board[r][right][0] == enemy: #if next is enemy
				moves.append(Move((r, c), (r, right), self.board))
				break
			else: #if next right is a friend piece
				break
		for left in range(c-1, -1, -1):
			if self.board[r][left] == "--": #if next left is empty
				moves.append(Move((r, c), (r, left), self.board))
			elif self.board[r][left][0] == enemy: #if next is enemy
				moves.append(Move((r, c), (r, left), self.board))
				break
			else: #if next left is a friend piece
				break

	def getAMoves(self, r, c, moves):
		enemy = 'N' if self.whiteMoves else 'B'
		#for upRight in zip(range(r+1, len(self.board)), range(c+1, len(self.board[c]))):
		#up right
		for (r1,c1) in zip(range(r+1, len(self.board[r])), range(c+1, len(self.board))):
			if self.board[r1][c1] == "--": #if next is empty
				moves.append(Move((r, c), (r1, c1), self.board))
			elif self.board[r1][c1][0] == enemy: #if next is enemy
				moves.append(Move((r, c), (r1, c1), self.board))
				break
			else: #if next up is a friend piece
				break
		#up left
		for (r1,c1) in zip(range(r+1, len(self.board[r])), range(c-1, -1, -1)):
			if self.board[r1][c1] == "--": #if next is empty
				moves.append(Move((r, c), (r1, c1), self.board))
			elif self.board[r1][c1][0] == enemy: #if next is enemy
				moves.append(Move((r, c), (r1, c1), self.board))
				break
			else: #if next up is a friend piece
				break
		#down left
		for (r1,c1) in zip(range(r-1, -1, -1), range(c-1, -1, -1)):
			if self.board[r1][c1] == "--": #if next is empty
				moves.append(Move((r, c), (r1, c1), self.board))
			elif self.board[r1][c1][0] == enemy: #if next is enemy
				moves.append(Move((r, c), (r1, c1), self.board))
				break
			else: #if next up is a friend piece
				break
		#down right
		for (r1,c1) in zip(range(r-1, -1, -1), range(c+1, len(self.board))):
			if self.board[r1][c1] == "--": #if next is empty
				moves.append(Move((r, c), (r1, c1), self.board))
			elif self.board[r1][c1][0] == enemy: #if next is enemy
				moves.append(Move((r, c), (r1, c1), self.board))
				break
			else: #if next up is a friend piece
				break

	def getCMoves(self, r, c, moves):
		enemy = 'N' if self.whiteMoves else 'B'
		if r < 6: 
			if c < 7 and (self.board[r+2][c+1] == "--" or self.board[r+2][c+1][0] == enemy): #top right
				moves.append(Move((r, c), (r+2, c+1), self.board))
			if c > 0 and (self.board[r+2][c-1] == "--" or self.board[r+2][c-1][0] == enemy): #top left
				moves.append(Move((r, c), (r+2, c-1), self.board))
		if r > 1: 
			if c < 7 and (self.board[r-2][c+1] == "--" or self.board[r-2][c+1][0] == enemy): #bottom right
				moves.append(Move((r, c), (r-2, c+1), self.board))
			if c > 0 and (self.board[r-2][c-1] == "--" or self.board[r-2][c-1][0] == enemy): #bottom left
				moves.append(Move((r, c), (r-2, c-1), self.board))
		if c < 6:
			if r < 7 and (self.board[r+1][c+2] == "--" or self.board[r+1][c+2][0] == enemy): #right top
				moves.append(Move((r, c), (r+1, c+2), self.board))
			if r > 0 and (self.board[r-1][c+2] == "--" or self.board[r-1][c+2][0] == enemy): #right bottom
				moves.append(Move((r, c), (r-1, c+2), self.board))
		if c > 1:
			if r < 7 and (self.board[r+1][c-2] == "--" or self.board[r+1][c-2][0] == enemy): #left top
				moves.append(Move((r, c), (r+1, c-2), self.board))
			if r > 0 and (self.board[r-1][c-2] == "--" or self.board[r-1][c-2][0] == enemy): #left bottom
				moves.append(Move((r, c), (r-1, c-2), self.board))

	def getQMoves(self, r, c, moves):
		self.getAMoves(r, c, moves)
		self.getTMoves(r, c, moves)

	def getKMoves(self, r, c, moves):
		enemy = 'N' if self.whiteMoves else 'B'
		#top L
		if c > 0 and r < len(self.board)-1:
			if self.board[r+1][c-1] == '--' or self.board[r+1][c-1][0] == enemy: 
				moves.append(Move((r, c), (r+1, c-1), self.board))
		#top
		if r < len(self.board)-1:
			if self.board[r+1][c] == '--' or self.board[r+1][c][0] == enemy: 
				moves.append(Move((r, c), (r+1, c), self.board))
		#top R
		if c < len(self.board[r])-1 and r < len(self.board)-1:
			if self.board[r+1][c+1] == '--' or self.board[r+1][c+1][0] == enemy: 
				moves.append(Move((r, c), (r+1, c+1), self.board))
		#R
		if c < len(self.board[r])-1 :
			if self.board[r][c+1] == '--' or self.board[r][c+1][0] == enemy:
				moves.append(Move((r, c), (r, c+1), self.board))
		#bottom R
		if r > 0 and c < len(self.board[r])-1: 
			if self.board[r-1][c+1] == '--' or self.board[r-1][c+1][0] == enemy: 
				moves.append(Move((r, c), (r-1, c+1), self.board))
		#bottom
		if r > 0:	
			if self.board[r-1][c] == '--' or self.board[r-1][c][0] == enemy: 
				moves.append(Move((r, c), (r-1, c), self.board))
		#bottom L
		if r > 0 and c > 0:
			if self.board[r-1][c-1] == '--' or self.board[r-1][c-1][0] == enemy: 
				moves.append(Move((r, c), (r-1, c-1), self.board))
		#L
		if c > 0:
			if self.board[r][c-1] == '--' or self.board[r][c-1][0] == enemy: 
				moves.append(Move((r, c), (r, c-1), self.board))

	#just collapse this ^ and forget about it

class Move():
	ranksToRows = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6, "8": 7}
	rowsToRanks = {v: k for k, v in ranksToRows.items()}
	filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
	colsToFiles = {v: k for k, v in filesToCols.items()}

	def __init__(self, startSq, endSq, boardState) -> None:
		"""
		Initializes the Move object
		files: (1->8)   ranks: (A->H)   (1,A)(2,B)
		:param startSq: (file, rank)
		:param endSq: (file, rank)
		:param boardState: a 2D array of the board state
		"""
		self.startRow = startSq[0]       #1
		self.startCol = startSq[1]       #A
		self.endRow = endSq[0]       #2
		self.endCol = endSq[1]       #B
		self.pieceMoved = boardState[self.startRow][self.startCol]
		self.pieceCaptured = boardState[self.endRow][self.endCol]
		self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
		Main.mPrint("ENGINE", f"moveID: {self.moveID} ({self.getChessNotation()})")

	def __eq__(self, other: object) -> bool:
			if isinstance(other, Move):
				return self.moveID == other.moveID
			return False

	def getChessNotation(self) -> str:
		"""Only use of log/printing purposes """
		return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

	def getRankFile(self, r, c) -> str:
		"""
		:param r: the row of the piece
		:param c: column
		:return: The rank and file of the piece. "fr"
		"""
		return self.colsToFiles[c] + self.rowsToRanks[r]

"""
♟️ Chess Pawn

♛ Black Chess Queen
♝ Black Chess Bishop
♜ Black Chess Rook
♞ Black Chess Knight
♚ Black Chess King
♕ White Chess Queen
♙ White Chess Pawn
♔ White Chess King
♗ White Chess Bishop
♘ White Chess Knight
♖ White Chess Rook
"""