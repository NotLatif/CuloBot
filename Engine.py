import Main as Main

class GameState():
	"""
	Stores information about the current game, detects legal moves, logs moves, etc
	"""
	def __init__(self, gameID, cg) -> None:
		self.cg = cg
		#board: 8x8 2d list of str (2chr)
		#N = Nero, B = Bianco, Torre Alfiere Cavallo Queen King Pedone
		self.board = [ #TODO (maybe) use english notation
			["BT", "BC", "BA", "BQ", "BK", "BA", "BC", "BT"], #A Bianco 
			["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"], #B
			["--", "--", "--", "--", "--", "--", "--", "--"], #C
			["--", "--", "--", "--", "--", "--", "--", "--"], #D
			["--", "--", "--", "--", "--", "--", "--", "--"], #E
			["--", "--", "--", "--", "--", "--", "--", "--"], #F
			["NP", "NP", "NP", "NP", "NP", "NP", "NP", "NP"], #G
			["NT", "NC", "NA", "NQ", "NK", "NA", "NC", "NT"], #H Nero 
		]
		self.whiteKpos = (0, 4)
		self.blackKpos = (7, 4)
		self.whiteMoves = True
		self.checkMate = False
		self.staleMate = False
		self.moveLog = []
		self.moveFunctions = {
			'P': self.getPMoves,
			'T': self.getTMoves,
			'C': self.getCMoves,
			'A': self.getAMoves,
			'Q': self.getQMoves,
			'K': self.getKMoves
		}
		self.turnCount = 0
		self.gameID = gameID

		self.inCheck = False
		self.pins = [] #pieces that are protecting the king
		self.checks = [] #pieces that are checking the king

	def mPrint(self, prefix, value):
		self.cg.mPrint(prefix, value, 'ENGINE')

	def getWinner(self):
		if self.checkMate or self.staleMate:
			return 'N' if self.whiteMoves else 'B'
		return None

	def getMoveHistory(self):
		pass
	
	def makeMove(self, move) -> None:
		"""
		Makes a move and logs it
		
		:param move: the move to be made
		"""
		#we can assume the move is valid
		self.board[move.startRow][move.startCol] = "--"
		self.board[move.endRow][move.endCol] = move.pieceMoved
		self.moveLog.append(move)
		self.turnCount += 1
		self.whiteMoves = not self.whiteMoves
		if move.pieceMoved == 'BK':
			self.whiteKpos = (move.endRow, move.endCol)
		if move.pieceMoved == 'NK':
			self.blackKpos = (move.endRow, move.endCol)

	def undoMove(self) -> None:
		"""
		Undo last move
		"""
		if (len(self.moveLog) != 0):
			lastMove = self.moveLog.pop()
			self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
			self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
			self.turnCount -= 1
			self.whiteMoves = not self.whiteMoves
			if lastMove.pieceMoved == 'BK':
				self.whiteKpos = (lastMove.startRow, lastMove.startCol)
			if lastMove.pieceMoved == 'NK':
				self.blackKpos = (lastMove.startRow, lastMove.startCol)

	def getValidMoves(self) -> list:
		self.mPrint('VARS', f"Turn: {'White' if self.whiteMoves else 'Black'}")
		#return self.getValidMovesNaive() #not very good but should work
		moves =  self.getValidMovesComplicated() #better but has bugs currently 
		for m in moves:
			self.mPrint("DEBUG", f"moveID: {m.moveID} ({m.getChessNotation()})")
		return moves

	def getValidMovesComplicated(self) -> list: #more efficient but complicated algorithm
		self.mPrint('INFO', 'using the complicate algorithm to generate moves')
		moves = []
		self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
		self.mPrint('VARS', f'inCheck: {self.inCheck}')
		for p in self.pins: self.mPrint('VARS', f'pin[x]: {p}')
		for c in self.checks: self.mPrint('VARS', f'check[x]: {c}')

		if self.whiteMoves:
			kingRow = self.whiteKpos[0]
			kingCol = self.whiteKpos[1]
		else:
			kingRow = self.blackKpos[0]
			kingCol = self.blackKpos[1]

		if self.inCheck: #remove moves that expose the king
			if len(self.checks) == 1: #only 1 check, block the check or move the king
				moves = self.getAllPossibleMoves()
				#to block a check put a piece in between king and enemy
				check = self.checks[0]
				checkRow = check[0]
				checkCol = check[1]
				pieceChecking = self.board[checkRow][checkCol]
				validSquares = [] #pieces can move here
				if pieceChecking[1] == 'C': #Cavallo
					validSquares = [(checkRow, checkCol)] #piece can only move where the knight is
				else:
					for i in range(1, len(self.board)): #generates where piece can move to and block the check
						oneValidSquare = (kingRow + check[2] * i, kingCol + check[3] * i) #check2 and check3 are the check directions
						validSquares.append(oneValidSquare)
						if oneValidSquare[0] == checkRow and oneValidSquare[1] == checkCol:
							break
				#get rid of any moves that don't block check or move the king
				for i in range(len(moves)-1, -1, -1): #will delete stuff from list so go backwards
					if moves[i].pieceMoved[1] != 'K': #move does not move king so it is check or capture
						if not (moves[i].endRow, moves[i].endCol) in validSquares: #move dsen't block check or capture piece
							moves.remove(moves[i])

			else: #'double check' king has to move
				self.getKMoves(kingRow, kingCol, moves)
		else: #not in check so all moves are ok
			moves = self.getAllPossibleMoves()

		if len(moves) == 0:
			if self.isInCheck():
				self.checkMate = True
			else:
				self.staleMate = True
		else:
			self.checkMate = False #in case of undo
			self.staleMate = False

		return moves

	def checkForPinsAndChecks(self) -> tuple[bool, list, list]:
		pins = []
		checks = []
		inCheck = False
		if self.whiteMoves:
			enemyColor = 'N'
			allyColor = 'B'
			startRow = self.whiteKpos[0]
			startCol = self.whiteKpos[1]
		else:
			enemyColor = 'B'
			allyColor = 'N'
			startRow = self.blackKpos[0]
			startCol = self.blackKpos[1]
		
		#'raycast' from king and find pins, checks
		directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
		for j in range(len(directions)):
			d = directions[j]
			possiblePin = () #reset var
			for i in range(1, len(self.board)):
				endRow = startRow + d[0] * i
				endCol = startCol + d[1] * i
				if 0 <= endRow < len(self.board[i]) and 0 <= endCol < len(self.board):
					endPiece = self.board[endRow][endCol]
					if endPiece[0] == allyColor and endPiece[1] != 'K':
						if possiblePin == (): #piece could be pinned
							possiblePin = (endRow, endCol, d[0], d[1])
						else: #second allied piece in a row (no pins)
							break
					elif endPiece[0] == enemyColor:
						type = endPiece[1]
						#big if statement with 5 conditions
						#1.) orthogonally away from king and piece is rook (T torre)
						#2.) diagonally away from king and piece is bishop (A alfiere)
						#3.) 1 square away diagonally from king and piece is pawn
						#4.) any direction and piece is Queen
						#5.) any direction 1 sq. away and piece is king
						if (0 <= j <= 3 and type == 'T') or \
								(4 <=j <= 7 and type == 'A') or \
								(i == 1 and type == 'P' and((enemyColor == 'B' and 6 <= j <= 7) or (enemyColor == 'N' and 4 <= j <= 5))) or \
								(type == 'Q') or\
								(i == 1 and type == 'K'):
							if possiblePin == (): #no piece defending king
								inCheck = True
								checks.append((endRow, endCol, d[0], d[1]))
								break
							else: #piece blocking check
								pins.append(possiblePin)
								break
						else: #enemy not aplying check
							break
				else: #off board
					break 
		#knight checks
		knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
		for m in knightMoves:
			endRow = startRow + m[0]
			endCol = startCol + m[1]	#   V<- we can assume that all the rows are the same lenght
			if 0 <= endRow < len(self.board[0]) and 0 <= endCol < len(self.board):
				endPiece = self.board[endRow][endCol]
				if endPiece[0] == enemyColor and endPiece[1] == 'C': #Cavallo
					inCheck = True
					checks.append((endRow, endCol, m[0], m[1]))

		return inCheck, pins, checks

	def getValidMovesNaive(self) -> list:
		self.mPrint('INFO', 'using the naive algorithm to generate moves')

		#All moves considering checks (if you move a piece do you expose the K?)
		#1. generate all the moves
		moves = self.getAllPossibleMoves() #temp.
		#2. foreach move make it
		for i in range(len(moves)-1, -1, -1): #go backwards because we will delete things from a list
			self.makeMove(moves[i]) #WARN: this function switches turn
			#3. generate all opponent's moves
			#4. foreach opponent move, see if they attack the king
			self.whiteMoves = not self.whiteMoves
			if self.isInCheck():
				#5. if they do, it's not a valid move
				moves.remove(moves[i])
			self.whiteMoves = not self.whiteMoves
			self.undoMove() #WARN this function switches turn

		if len(moves) == 0:
			if self.isInCheck():
				self.checkMate = True
			else:
				self.staleMate = True
		else:
			self.checkMate = False #in case of undo
			self.staleMate = False
		return moves

	def isInCheck(self) -> bool:
		"""Determines if player is in check"""
		if self.whiteMoves:
			return self.squareUnderAttack(self.whiteKpos[0], self.whiteKpos[1])
		else:
			return self.squareUnderAttack(self.blackKpos[0], self.blackKpos[1])

	def squareUnderAttack(self, r, c) -> bool:
		"""Determines if enemy can attack (r, c)"""
		self.mPrint('DEBUG', f'generating opponent moves')
		self.whiteMoves = not self.whiteMoves #I want opponent moves
		opponentMoves = self.getAllPossibleMoves()
		self.whiteMoves = not self.whiteMoves #reset turn
		for move in opponentMoves:
			if move.endRow == r and move.endCol == c: #square under attack
				return True #square under attack
		return False #square not under attack
		
	def getAllPossibleMoves(self) -> list:
		self.mPrint('FUNC', 'getAllPossibleMoves()')
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

	def getPMoves(self, r, c, moves) -> list:
		#FIXME when pawn reaches end of the board it throws IndexOutOfRange, fix adding pawn promotions
		#TODO promotion, castling, en passant
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				self.pins.remove(self.pins[i])
				break

		if self.whiteMoves: #pedoni bianchi
			#is the square in front empty?
			if self.board[r+1][c] == "--":
				if not piecePinned or pinDirection == (1, 0):
					moves.append(Move((r, c), (r+1, c), self.board))
					if r == 1 and self.board[r+2][c] == "--": #If it's the first move can go 2 up
						moves.append(Move((r, c), (r+2, c), self.board))
			#captures
			if c != len(self.board[r])-1: #piece is not on the last column
				if not piecePinned or pinDirection == (1, 1):
					if self.board[r+1][c+1] != "--" and self.board[r+1][c+1][0] != "B": #can eat top right if not white (Bianco)
						moves.append(Move((r, c), (r+1, c+1), self.board))

			if c != 0: #piece is not on the first column
				if not piecePinned or pinDirection == (1, -1):
					if self.board[r+1][c-1] != "--" and self.board[r+1][c-1][0] != "B": #can eat top left if not white
						moves.append(Move((r, c), (r+1, c-1), self.board))     

		else: #pedoni  neri
			#is the square in front empty?
			if self.board[r-1][c] == "--":
				if not piecePinned or pinDirection == (-1, 0):
					moves.append(Move((r, c), (r-1, c), self.board))
					if r == 6 and self.board[r-2][c] == "--": #If it's the first move can go 2 up
						moves.append(Move((r, c), (r-2, c), self.board))

			if c != len(self.board[r]) -1: #piece is not on the last column
				if not piecePinned or pinDirection == (-1, 1):
					if self.board[r-1][c+1] != "--" and self.board[r-1][c+1][0] != "N": #can eat top right if not black (Nero)
						moves.append(Move((r, c), (r-1, c+1), self.board))

			if c != 0: #piece is not on the first column
				if not piecePinned or pinDirection == (-1, -1):
					if self.board[r-1][c-1] != "--" and self.board[r-1][c-1][0] != "N": #can eat top left if not black
						moves.append(Move((r, c), (r-1, c-1), self.board))

		return moves

	def getTMoves(self, r, c, moves) -> list:
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				if self.board[r][c][1] != 'Q': #can't remove queen from pin on rook moves, only remove it on bishop moves
					self.pins.remove(self.pins[i])
				break

		enemy = 'N' if self.whiteMoves else 'B'

		directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
		for d in directions:
			for i in range(1, 8):
				endRow = r + d[0] * i
				endCol = c + d[1] * i
				if 0 <= endRow < 8 and 0 <= endCol < 8:
					if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
						endPiece = self.board[endRow][endCol]
						if endPiece == "--": #empty space valid
							moves.append(Move((r, c), (endRow, endCol), self.board))
						elif endPiece[0] == enemy: #eats enemy
							moves.append(Move((r, c), (endRow, endCol), self.board))
							break
						else: #friendly piece (invalid move)
							break
				else: #off board
					break

	def getAMoves(self, r, c, moves) -> list:
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				self.pins.remove(self.pins[i])
				break

		enemy = 'N' if self.whiteMoves else 'B'

		directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
		for d in directions:
			for i in range(1, 8):
				endRow = r + d[0] * i
				endCol = c + d[1] * i
				if 0 <= endRow < 8 and 0 <= endCol < 8:
					if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
						endPiece = self.board[endRow][endCol]
						if endPiece == "--": #empty space valid
							moves.append(Move((r, c), (endRow, endCol), self.board))
						elif endPiece[0] == enemy: #eats enemy
							moves.append(Move((r, c), (endRow, endCol), self.board))
							break
						else: #friendly piece (invalid move)
							break
				else: #off board
					break

	def getCMoves(self, r, c, moves) -> list:
		piecePinned = False
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				self.pins.remove(self.pins[i])
				break
		
		ally = 'B' if self.whiteMoves else 'N'
		knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
		for m in knightMoves:
			endRow = r + m[0]
			endCol = c + m[1]
			if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board):
				if not piecePinned:
					endPiece = self.board[endRow][endCol]
					if endPiece[0] != ally: #not ally, so enemy or blank
						moves.append(Move((r, c), (endRow, endCol), self.board))

	def getQMoves(self, r, c, moves) -> list:
		self.getAMoves(r, c, moves)
		self.getTMoves(r, c, moves)

	def getKMoves(self, r, c, moves) -> list:
		allyColor = 'B' if self.whiteMoves else 'N'
		rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
		colMoves = (-1,  0,  1,-1, 1,-1, 0, 1)
		for i in range(8):
			endRow = r + rowMoves[i]
			endCol = c + colMoves[i]
			if 0 <= endRow < 8 and 0 <= endCol < 8:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] != allyColor: #it's blank or enemy
					if allyColor == 'B':
						self.whiteKpos = (endRow, endCol)
					else:
						self.blackKpos = (endRow, endCol)
					inCheck, pins, checks = self.checkForPinsAndChecks()
					if not inCheck:
						moves.append(Move((r, c), (endRow, endCol), self.board))
					#place king back on original location
					if allyColor == 'B':
						self.whiteKpos = (r, c)
					else:
						self.blackKpos = (r, c)


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
		#self.mPrint("ENGINE", f"moveID: {self.moveID} ({self.getChessNotation()})")

	def __eq__(self, other: object) -> bool:
			if isinstance(other, Move):
				return self.moveID == other.moveID
			return False

	def getAlgebraicNotation(self) -> str:
		notation = ''
		pass #TODO implement (use emojis maybe)

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
K: King
Q: Queen
R: Rook		(T torre)
B: Bishop	(A alfiere)
N: Knight	(C cavallo)
P: Pawn (although, by convention, P is usually omitted from notation)"""
"""
♟️♟ Chess Pawn

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