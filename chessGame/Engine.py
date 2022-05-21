#TODO ask choice for pawn promotion
class GameState():
	"""
	Stores information about the current game, detects legal moves, logs moves, etc
	"""
	def __init__(self, cg) -> None:
		self.cg = cg
		self.board = [] #list[8][8] it will be generated from FEN
		self.whiteKpos = ()
		self.blackKpos = ()
		self.whiteMoves = True
		self.halfMoveClock = 0 #https://www.chessprogramming.org/Halfmove_Clock
		self.fullMoves = 0 #incremented every time black makes a move
		self.enpassantPossible = () #coords of enpassant capture
		self.lastMoveStart = ()
		self.lastMoveEnd = ()
		self.castleRights = CastleRights(True, True, True, True)
		self.castleRightsLog = [CastleRights(self.castleRights.K, self.castleRights.Q, 
											self.castleRights.k, self.castleRights.q)]

		self.inCheck = False
		self.checkMate = False
		self.staleMate = False
		self.pins = [] #pieces that are protecting the king
		self.checks = [] #pieces that are checking the king
		self.draw = False

		self.moveLog = []
		self.moveFunctions = {
			'P': self.getPMoves,
			'R': self.getRMoves,
			'N': self.getNMoves,
			'B': self.getBMoves,
			'Q': self.getQMoves,
			'K': self.getKMoves
		}
		self.turnCount = 0
		self.whiteCaptured = [] #pieces the white player had captured
		self.blackCaptured = [] #pieces the black player had captured

	def boardFromFEN(self, FEN : str) -> None:
		self.mPrint('DEBUG', f'requested board FEN: {FEN}')
		
		board = []
		row = []
		boardFEN = FEN.split()[0]
		if('k' not in boardFEN or 'K' not in boardFEN):
			self.mPrint('ERROR', f'king is missing from FEN | missing king: {"black" if "k" not in boardFEN else ""} {"white" if "K" not in boardFEN else ""} ')
			return -1
		
		#very hard to read, will probably rewrite at some point
		for r, line in enumerate(boardFEN.split('/')[::-1]): #Read it backwards
			for c, char in enumerate(line):
				if char.isnumeric():
					for i in range(int(char)):
						row.append('--')
						
				elif char.isupper(): #white
					row.append(f'W{char}')
					if char == 'K':
						self.whiteKpos = (r, c)
						self.mPrint('DEBUG', f'Found white king @ ({r}, {c})')
				else:
					row.append(f'B{char.upper()}')
					if char == 'k':
						self.blackKpos = (r, c)
						self.mPrint('DEBUG', f'Found black king @ ({r}, {c})')
			board.append(row)
			row = []
	
		FENdata = FEN.split()
		if len(FENdata) >= 1: #the board was descrbed (this should always be True)
			self.board = board
		else:																#random letters for searching in the code
			self.mPrint('ERROR', 'Unexpected condition result (False) (expected:True) jiaejriajifea')
			return
		if len(FENdata) >= 2: #the turn is described
			self.whiteMoves = True if FENdata[1].lower() == 'w' else False
		
		if len(FENdata) >= 3: #the castling rights were described
			if (FENdata[3] != '-'): #check if it was not blank
				if ('Q' in FENdata[3]):
					self.castleRights.Q = True
				if ('K' in FENdata[3]):
					self.castleRights.K = True
				if ('q' in FENdata[3]):
					self.castleRights.q = True
				if ('k' in FENdata[3]):
					self.castleRights.k = True

		if len(FENdata) >= 4: #enPassant was described
			if (FENdata[3] != '-'): #check if it was not blank
				self.enpassantPossible = (Move.filesToCols[FENdata[3][0]], Move.ranksToRows[FENdata[3][1]])
		
		if len(FENdata) >= 5: #the half Clock was described
			if (FENdata[4].isnumeric()):
				self.halfMoveClock = int(FENdata[4])
			else:
				self.mPrint('WARN', 'FEN halfclock was provived but it\'s not an integer.')
		
		if len(FENdata) >= 6: #the full Clock was described
			if (FENdata[5].isnumeric()):
				self.fullMoves = int(FENdata[5])
			else:
				self.mPrint('WARN', 'FEN fullclock was provived but it\'s not an integer.')

	def getFEN(self) -> str:
		fen = ''
		consecutiveBlanks = 0
		whiteKingPresent = False
		blackKingPresent = False
		for row in range(len(self.board)-1, -1, -1): #FEN is written from row 8 to 1
			for col, colPiece in enumerate(self.board[row]):
				if colPiece == '--':
					consecutiveBlanks += 1

				elif colPiece[0] == 'W':
					if consecutiveBlanks: #0 acts like False
						fen += str(consecutiveBlanks)
						consecutiveBlanks = 0
					if colPiece[1] == 'K': whiteKingPresent=True
					fen += colPiece[1]

				elif colPiece[0] == 'B':
					if consecutiveBlanks: #0 acts like False
						fen += str(consecutiveBlanks)
						consecutiveBlanks = 0
					if colPiece[1] == 'K': blackKingPresent=True
					fen += colPiece[1].lower()
				else:
					self.mPrint('ERROR', f'<ERROR generating FEN @ tile({row},{col}); piece="{colPiece}">')
					return None
			#at the end of each row
			if consecutiveBlanks: #0 acts like False
				fen += str(consecutiveBlanks)
				consecutiveBlanks = 0
			fen += '/'
		fen = fen[:-1] #remove the last '/'
		if(not whiteKingPresent or not blackKingPresent):
			#sorry for the long string, it's just an "UI" thing
			self.mPrint('ERROR', f'<ERROR generating FEN: {"white King" if not whiteKingPresent else ""}{" and " if not whiteKingPresent and not blackKingPresent else ""}{"black King" if not blackKingPresent else ""} is not present on the board>')
			return None
		
		fen += ' '
		if self.whiteMoves: fen += 'w '
		else: fen += 'b '

		#castling rights (QK)(qk) eg: QKqk: all castling right available; QK only white can castle; k black can only castle kingside
		if self.castleRights == (False, False, False, False):
			fen += '- '
		else:
			if self.castleRights.Q == True:
				fen += 'Q'
			if self.castleRights.K == True:
				fen += 'K'
			if self.castleRights.q == True:
				fen += 'q'
			if self.castleRights.k == True:
				fen += 'k'
		
		#enpassant
		if self.enpassantPossible != ():
			fen += f'{Move.colsToFiles[self.enpassantPossible[1]]}{Move.rowsToRanks[self.enpassantPossible[0]]}'
		else: fen += '- '

		fen += f'{self.halfMoveClock} {self.fullMoves}'

		return fen 

	def getStats(self):
		return (f'wK:{self.whiteKpos}', f'bK:{self.blackKpos}', f'checkmate: {self.checkMate}',
				f'stalemate: {self.staleMate}', f'turn: {self.turnCount}', f'inCheck: {self.inCheck}', 
				f'pins: {self.pins}', f'checks: {self.checks}', f'whiteMoves: {self.whiteMoves}')

	def mPrint(self, prefix, value):
		self.cg.mPrint(prefix, value, 'ENGINE')

	def getWinner(self):
		if self.checkMate or self.staleMate:
			return 'B' if self.whiteMoves else 'W'
		return None

	def getPGN(self): #FIXME ADD ROUND
		pgn = f"""
[Event "Discord chess"]
[Site "{self.cg.serverName}"]
[Date "{self.cg.date}"]
[Round "{self.cg.round}"]
[White "{self.cg.players[0]}"]
[Black "{self.cg.players[1]}"]
[Result "{self.cg.result}"]
[FEN {self.cg.FEN}]

"""
		for i, j in zip(range(0, len(self.moveLog), 2), range(len(self.moveLog))):
			pgn += f"{j+1}. {self.moveLog[i].algebraicNotation} " #turn. whitemove
			if (i+1 < len(self.moveLog)):
				pgn += f"{self.moveLog[i+1].algebraicNotation} " #blackmove
		
		return pgn
	
	def makeMove(self, move) -> None:
		"""
		Makes a move and logs it
		:param move: the move to be made
		"""
		self.mPrint('DEBUG', f'piece moved: {move.pieceMoved}')
		#we can assume the move is valid
		self.board[move.startRow][move.startCol] = "--"
		self.board[move.endRow][move.endCol] = move.pieceMoved
		self.moveLog.append(move)
		self.lastMoveStart = (move.startRow, move.startCol)
		self.lastMoveEnd = (move.endRow, move.endCol)
		self.turnCount += 1
		self.whiteMoves = not self.whiteMoves
		if move.pieceMoved == 'WK':
			self.mPrint('DEBUG', 'moved white king')
			self.whiteKpos = (move.endRow, move.endCol)
		if move.pieceMoved == 'BK':
			self.mPrint('DEBUG', 'moved black king')
			self.blackKpos = (move.endRow, move.endCol)
		if move.pieceMoved[0] == 'B':
			self.fullMoves += 1
		#updating enpassant variable (pawn moves twice)
		if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
			self.enpassantPossible = ((move.endRow + move.startRow) // 2, move.endCol) #the enPassant square is the average
		else:
			self.enpassantPossible = ()
		#enpassant capture
		if move.enPassant:
			self.board[move.startRow][move.endCol] = '--' #the capture is one row behind
		#pawn promotion
		if move.pawnPromotion:
			promotedPiece = input('Promote the piece Q, K, B, R, N: ')
			self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q' #Promote to a queen for now, will figure out later a way
		#castlemove
		if move.isCastle:
			self.mPrint('DEBUG', f'found castle move {move.endCol} {move.startCol}')
			if move.endCol - move.startCol == 2: #kingside
				self.mPrint('DEBUG', f'- kingside')
				#move the rook
				self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
				#cancel the rook
				self.board[move.endRow][move.endCol+1] = "--"

			else: #queenside
				self.mPrint('DEBUG', f'- queenside')
				#move the rook
				self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
				#cancel the rook
				self.board[move.endRow][move.endCol-2] = "--"
		
		#update castling
		self.updateCastleRight(move)
		self.castleRightsLog.append(CastleRights(self.castleRights.K, self.castleRights.Q, 
									self.castleRights.k, self.castleRights.q))

	def undoMove(self) -> None:
		"""
		Undo last move
		"""
		if (len(self.moveLog) != 0):
			lastMove = self.moveLog.pop()
			self.lastMove = lastMove
			self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
			self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
			self.turnCount -= 1
			self.whiteMoves = not self.whiteMoves
			if lastMove.pieceMoved == 'WK':
				self.whiteKpos = (lastMove.startRow, lastMove.startCol)
			if lastMove.pieceMoved == 'BK':
				self.blackKpos = (lastMove.startRow, lastMove.startCol)
			if lastMove.pieceMoved[0] == 'B':
				self.fullMoves -= 1
			#undo enpassant
			if lastMove.enPassant:
				self.board[lastMove.endRow][lastMove.endCol] = '--' #leave landing square
				self.board[lastMove.startRow][lastMove.endCol] = lastMove.pieceCaptured #BUG?
				self.enpassantPossible = (lastMove.endRow, lastMove.endCol)
			#undo 2 square pawn advance
			if lastMove.pieceMoved[1] == 'P' and abs(lastMove.startRow - lastMove.endRow) == 2:
				self.enpassantPossible = ()
			#undo castling rights
			self.castleRightsLog.pop()
			self.castleRights = self.castleRightsLog[-1]
			#undo castle
			if lastMove.isCastle:
				if lastMove.endCol - lastMove.startCol == 2: #kingside
					#move the rook back
					self.board[lastMove.endRow][lastMove.endCol+1] = self.board[lastMove.endRow][lastMove.endCol-1]
					#remove the rook
					self.board[lastMove.endRow][lastMove.endCol-1] = "--"
				else: #queenside
					#move the rook back
					self.board[lastMove.endRow][lastMove.endCol-2] = self.board[lastMove.endRow][lastMove.endCol+1]
					#remove the rook
					self.board[lastMove.endRow][lastMove.endCol+1] = "--"
				
	def updateCastleRight(self, move):	
		if move.pieceMoved == 'WK':
			self.castleRights.K = False
			self.castleRights.Q = False
		elif move.pieceMoved == 'BK':
			self.castleRights.k = False
			self.castleRights.q = False
		elif move.pieceMoved == 'WR': #white rook
			if move.startRow == 0:
				if move.startCol == 0:
					self.castleRights.Q = False
				elif move.startCol == 7:
					self.castleRights.K = False
		elif move.pieceMoved == 'BR': #white rook
			if move.startRow == 7:
				if move.startCol == 0:
					self.castleRights.q = False
				elif move.startCol == 7:
					self.castleRights.k = False

	def getValidMoves(self) -> list:
		self.mPrint('VARS', f"Turn: {'White' if self.whiteMoves else 'Black'}")
		#return self.getValidMovesNaive() #not very good but should work
		moves =  self.getValidMovesComplicated()#better method
		
		Move.setAlgebraicNotation(moves) #pass every move so it can set the notation
		for m in moves:
			self.mPrint("MOVE", f"legalMove {m.moveID}: ({m.getChessNotation()}) ({m.algebraicNotation}{m.algebraicNotationSuffixes})")
		return moves

	def getValidMovesComplicated(self) -> list: #more efficient but complicated algorithm
		self.mPrint('INFO', 'Generating moves')
		moves = []
		self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
		self.mPrint('VARS', f'inCheck: {self.inCheck}')
		self.mPrint('VARS', f'checks: {self.checks}')
		self.mPrint('VARS', f'pins: {self.pins}')
		self.mPrint('VARS', f'enPassant: {self.enpassantPossible}')
		self.mPrint('VARS', f'whiteK: {self.whiteKpos}')
		self.mPrint('VARS', f'blackK: {self.blackKpos}')
		self.mPrint('VARS', f'halfMoves: {self.halfMoveClock}')
		self.mPrint('VARS', f'fullMoves: {self.fullMoves}')
		self.mPrint('VARS', f'checkmate: {self.checkMate}')
		self.mPrint('VARS', f'stalemate: {self.staleMate}')
		self.mPrint('VARS', f'castleRigts: {self.castleRights.getRights()}')
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
				if pieceChecking[1] == 'N': #Cavallo
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

		self.mPrint('WARN', f'whiteK: {self.whiteKpos}')
		self.mPrint('WARN', f'blackK: {self.blackKpos}')

		self.getCastleMoves(kingRow, kingCol, moves)

		if len(moves) == 0:
			if self.inCheck:
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
			enemyColor = 'B'
			allyColor = 'W'
			startRow = self.whiteKpos[0]
			startCol = self.whiteKpos[1]
		else:
			enemyColor = 'W'
			allyColor = 'B'
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
					if endPiece[0] == allyColor and endPiece[1] != 'K': #king?
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
						if (0 <= j <= 3 and type == 'R') or \
								(4 <=j <= 7 and type == 'B') or \
								(i == 1 and type == 'P' and((enemyColor == 'W' and 6 <= j <= 7) or (enemyColor == 'B' and 4 <= j <= 5))) or \
								(type == 'Q') or\
								(i == 1 and type == 'K'): #king
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
				if endPiece[0] == enemyColor and endPiece[1] == 'N': #Cavallo
					inCheck = True
					checks.append((endRow, endCol, m[0], m[1]))

		return inCheck, pins, checks

	def squareUnderAttack(self, r, c) -> bool:
		"""Determines if enemy can attack (r, c)"""
		self.mPrint('FUNC', f'generating opponent moves to check if ({r}, {c}) is under attack')
		self.whiteMoves = not self.whiteMoves #I want opponent moves
		opponentMoves = self.getAllPossibleMoves()
		self.whiteMoves = not self.whiteMoves #reset turn
		for move in opponentMoves:
			if move.endRow == r and move.endCol == c: #square under attack
				self.mPrint('DEBUG', f'FOUND ATTACK FOR SQUARE ({r} {c}) "{move.pieceMoved}"')
				return True #square under attack
		self.mPrint('DEBUG', f'No one attacking that square')
		return False #square not under attack

	def getCheckSquare(self) -> bool:
		if self.whiteMoves:
			return self.blackKpos
		else:
			return self.whiteKpos
		
	def getAllPossibleMoves(self) -> list:
		self.mPrint('FUNC', f'Generating all possible moves for {"white" if self.whiteMoves else "black"}')
		#generating the moves
		moves = []
		for r in range(len(self.board)):  #foreach col
			for c in range(len(self.board[r])): #foreach row (of col)
				pieceColor = self.board[r][c][0]
				if (pieceColor == "W" and self.whiteMoves) or (pieceColor == 'B' and not self.whiteMoves):
					piece = self.board[r][c][1]
					self.moveFunctions[piece](r,c,moves) #calls getXMoves
		return moves
	
	#oh boy here we go

	def getPMoves(self, r, c, moves) -> list:
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				self.pins.remove(self.pins[i])
				break

		if self.whiteMoves:
			moveAmount = 1
			startRow = 1
			lastRow = 7
			enemyColor = 'B'
		else:
			moveAmount = -1
			startRow = 6
			lastRow = 0
			enemyColor = 'W'
		pawnPromotion = False

		if self.board[r+moveAmount][c] == "--": #1 square move
			if not piecePinned or pinDirection == (moveAmount, 0):
				if r + moveAmount == lastRow:
					pawnPromotion = True
				moves.append(Move((r, c), (r+moveAmount, c), self.board, pawnPromotion=pawnPromotion))
				if r == startRow and self.board[r+(2*moveAmount)][c] == "--": #2 square move
					moves.append(Move((r, c), (r+ 2*moveAmount, c), self.board))
		
		if c-1 >= 0: #capture to the left
			if not piecePinned or pinDirection == (moveAmount, -1):
				if self.board[r + moveAmount][c - 1][0] == enemyColor:
					if r + moveAmount == lastRow:
						pawnPromotion = True
					moves.append(Move((r, c), (r+moveAmount, c-1), self.board, pawnPromotion=pawnPromotion))
				if (r + moveAmount, c - 1) == self.enpassantPossible:
					moves.append(Move((r, c), (r+moveAmount, c-1), self.board, enPassant=True))
		
		if c+1 < len(self.board): #capture to right
			if not piecePinned or pinDirection == (moveAmount, 1):
				if self.board[r + moveAmount][c + 1][0] == enemyColor:
					if r + moveAmount == lastRow:
						pawnPromotion = True
					moves.append(Move((r, c), (r+moveAmount, c+1), self.board, pawnPromotion=pawnPromotion))
				if (r + moveAmount, c + 1) == self.enpassantPossible:
					moves.append(Move((r, c), (r+moveAmount, c+1), self.board, enPassant=True))

		return moves

	def getRMoves(self, r, c, moves) -> list:
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				if self.board[r][c][1] != 'Q': #can't remove queen from pin on rook moves, only remove it on bishop moves
					self.pins.remove(self.pins[i])
				break

		enemy = 'B' if self.whiteMoves else 'W'

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

	def getBMoves(self, r, c, moves) -> list:
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				self.pins.remove(self.pins[i])
				break

		enemy = 'B' if self.whiteMoves else 'W'

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

	def getNMoves(self, r, c, moves) -> list:
		piecePinned = False
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				self.pins.remove(self.pins[i])
				break
		
		ally = 'W' if self.whiteMoves else 'B'
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
		self.getBMoves(r, c, moves)
		self.getRMoves(r, c, moves)

	def getKMoves(self, r, c, moves) -> list:
		allyColor = 'W' if self.whiteMoves else 'B'
		rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
		colMoves = (-1,  0,  1,-1, 1,-1, 0, 1)
		for i in range(8):
			endRow = r + rowMoves[i]
			endCol = c + colMoves[i]
			if 0 <= endRow < 8 and 0 <= endCol < 8:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] != allyColor: #it's blank or enemy
					if allyColor == 'W':
						self.whiteKpos = (endRow, endCol)
					else:
						self.blackKpos = (endRow, endCol)
					inCheck, pins, checks = self.checkForPinsAndChecks()
					if not inCheck:
						moves.append(Move((r, c), (endRow, endCol), self.board))
					#place king back on original location
					if allyColor == 'W':
						self.whiteKpos = (r, c)
					else:
						self.blackKpos = (r, c)
		
	def getCastleMoves(self, r, c, moves):
		self.mPrint('INFO', 'finding castle moves')
		if self.inCheck:
			self.mPrint('DEBUG', f'inCheck, castle not possible')
			return
		if (self.whiteMoves and self.castleRights.K) or (not self.whiteMoves and self.castleRights.k):
			self.mPrint('DEBUG', 'getKingSide')
			self.getKingSideCastleMove(r, c, moves)
		if (self.whiteMoves and self.castleRights.Q) or (not self.whiteMoves and self.castleRights.q):
			self.mPrint('DEBUG', 'getQueenSide')
			self.getQueenSideCastleMove(r, c, moves)
		self.mPrint('WARN', f'End of getCastleMoves: {r} {c}')
		#FIXME change WARN tag (was used only to highlight while debugging)

	def getKingSideCastleMove(self, r, c, moves):
		self.mPrint('DEBUG', f'kingside {r}, {c}')
		self.mPrint('DEBUG', f'pieces: {self.board[r][c+1]}, {self.board[r][c+2]}')
		if self.board[r][c+1] == '--'and self.board[r][c+2] == '--':
			self.mPrint('DEBUG', 'kingside squares are free')
			if not self.squareUnderAttack(r, c+2):
				self.mPrint('DEBUG', f'moves.append(Move(({r}, {c}), ({r}, {c+2}), ...))')
				moves.append(Move((r, c), (r, c+2), self.board, castle=True, kingCastle=True))
			else:
				self.mPrint('DEBUG', f'({r}, {c+2}) is under attack, castling not possible')

	def getQueenSideCastleMove(self, r, c, moves):
		self.mPrint('DEBUG', f'queenside {r}, {c}')
		self.mPrint('DEBUG', f'pieces: {self.board[r][c-1]}, {self.board[r][c-2]}, {self.board[r][c-3]}')
		if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
			self.mPrint('DEBUG', 'queenside squares are free')
			if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
				self.mPrint('DEBUG', f'moves.append(Move(({r}, {c}), ({r}, {c-2}), ...))')
				moves.append(Move((r, c), (r, c-2), self.board, castle=True, queenCastle=True))

	#just collapse this ^ and forget about it

class CastleRights():
	def __init__(self, K, Q, k, q) -> None:
		self.K = K
		self.Q = Q
		self.k = k
		self.q = q
	def getRights(self) -> tuple[bool, bool, bool, bool]:
		return self.K, self.Q, self.k, self.q

class Move():
	ranksToRows = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6, "8": 7}
	rowsToRanks = {v: k for k, v in ranksToRows.items()}
	filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
	colsToFiles = {v: k for k, v in filesToCols.items()}

	def __init__(self, startSq, endSq, boardState, enPassant=False, pawnPromotion = False, castle = False, queenCastle = False, kingCastle = False) -> None:
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

		self.promotionChoice = 'Q'
		self.pawnPromotion = pawnPromotion

		self.isCastle = castle
		self.kingCastle = kingCastle
		self.queenCastle = queenCastle

		self.enPassant = enPassant
		if self.enPassant:
			self.pieceCaptured = 'BP' if self.pieceMoved == 'WP' else 'WP'

		self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
		self.algebraicNotation = ''
		self.algebraicNotationSuffixes = ''

		self.givesCheckmate = False #TODO implement

	
		#self.mPrint("ENGINE", f"moveID: {self.moveID} ({self.getChessNotation()})")

	def __eq__(self, other: object) -> bool:
			if isinstance(other, Move):
				return self.moveID == other.moveID
			return False
	
	def findMoveFromAlgebraic(algebraic, moves):
		algebraic = algebraic.lower()
		for m in moves:	#compare lowercase, I don't believe it makes a difference
			if m.algebraicNotation.lower() == algebraic:
				return m
			elif 'x' in m.algebraicNotation and (algebraic == m.algebraicNotation.replace('x', '').lower()): #maybe user forgot to add x (Nxd2 == Nd2)
				return m
			elif f'{m.algebraicNotation.lower()}{m.algebraicNotationSuffixes.lower()}' == 'algebraic': #maybe user added a '+' to assert dominance
				return m
		return None

	def setAlgebraicNotation(legalMoves : list) -> None:
		#Not passing self and doing it piece by piece because for the algebrai notation
		#we need to consider the position of every piece at the same time to calculate ambiguities
		#returns algebraic notation starting from coordinates

		moves = [] #needed to calculate ambiguities
		for move in legalMoves:
			#					0					        1  			                   2
			moves.append((move.pieceMoved[1], (move.startRow, move.startCol), (move.endRow, move.endCol)))
			#moves = [(piecemoved, (sR,sC), (eR,eC)), ... for each move]
		# if piece is not pawn:
		for x, move in enumerate(moves): #foreach move
			if move[0] != 'P':
				#add the prefix
				legalMoves[x].algebraicNotation += move[0]
				
				#if ANY of the moves another piece (of the same type) has the same endSquare:
				for y in legalMoves: #compare move with every other move
			#		print(f'y in legalMoves: {y.pieceMoved}')
			#		print(f'pieceMoved: {y.pieceMoved[1]} - {move[0]}')
					if y.pieceMoved[1] == move[0]: #it's the same piece
			#			print(f'startSq: {(y.startRow, y.startCol)} - {move[1]}')
						if (y.startRow, y.startCol) != move[1]: #check if the startSq is different
			#				print(f"endSq: {(y.endRow, y.endCol)} - {move[2]}")
							if (y.endRow, y.endCol) == move[2]: #check if they are going in the same square
								#ambiguity found add the column to the prefix (e.g. Ncxd2)
								legalMoves[x].algebraicNotation += Move.colsToFiles[legalMoves[x].startCol]
								break #no need to check for other ambiguities
							else:pass #if the endSq is different, there is not ambiguity
						else:pass #if the startSq is equal, we found the same piece.
					else:pass #if the piece is different, there is not ambiguity
				if(legalMoves[x].pieceCaptured != '--'): #add capture after every check (Nx) / (Ncx)
					legalMoves[x].algebraicNotation += 'x'
				
			# if piece is pawn:
			else:
				if legalMoves[x].pieceCaptured != '--':
					legalMoves[x].algebraicNotation += f'{Move.colsToFiles[legalMoves[x].startCol]}x'
			
			if(move[0] == 'K'): #check for castling
				if legalMoves[x].kingCastle == True:
					legalMoves[x].algebraicNotation = 'O-O'
					continue
				if legalMoves[x].queenCastle == True:
					legalMoves[x].algebraicNotation = 'O-O-O'
					continue

			print(f'x: {x}, move: {move}')
			#add endsquare
			legalMoves[x].algebraicNotation += Move.colsToFiles[legalMoves[x].endCol]
			legalMoves[x].algebraicNotation += Move.rowsToRanks[legalMoves[x].endRow]

			if move[0] == 'P':
				#enpassant
				if legalMoves[x].enPassant:
					legalMoves[x].algebraicNotationSuffixes += 'e.p.'
				#promotion
				if legalMoves[x].pawnPromotion:
					legalMoves[x].algebraicNotation += legalMoves[x].promotionChoice
			
			if legalMoves[x].pieceCaptured[1] == 'K':
				legalMoves[x].algebraicNotationSuffixes += '+'
			if legalMoves[x].givesCheckmate:
				legalMoves[x].algebraicNotationSuffixes += '#'
			
		print('Calculated algebraic symbols')

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


Rank = row 
File = column

K: King
Q: Queen
R: Rook		(T torre)
B: Bishop	(A alfiere)
N: Knight	(C cavallo)
P: Pawn (although, by convention, P is usually omitted from notation)
To write a move, give the name of the piece and the square to which it moves.
If a piece is captured, we include the symbol x for "captures" before the destination square.

e.g.,
Nc3	  (cavallo->c3) l'unico cavallo che può andare a c3 è b1
f5	  (pedone->f5)  la P è omessa, pedone nero va avanti di 2
e4	  (pedone->e4)  pedone bianco va avanti di 2
fxe4  (P omessa) pedone nella colonna f, mangia(x) pedina in e4
Nxe4  kNight mangia la pedina in e4 (l'unico cavallo che può farlo è c3)
Nf6   kNight va in f6
Nxf6+ kNight mangia in f6 e mette in scacco (+)
gxf6  (P) pedone nella colonna g mangia in f6
Qh5#  Regina va in h5 e fa scacco matto

x: captures
0-0: kingside castle
0-0-0: queenside castle
+: check (or ch)
++: double check
#: checkmate
!: good move
?: poor move

# Avoiding Ambiguity
In situations where regular notation is ambiguous, add an extra letter or number to specify the origin of the piece that moves.
e.g.
[R, -, -, -, -, -, -, R]
Rd1  -> Rook va a d1, ma quale dei due???
Rad1 -> Notazione corretta. R in colonna a va a d1

When a pawn makes a capture, always include the originating file

capturing by enPassant:
add "e.p" suffix e.g. exd6e.p.

pawn promotion
e8Q -> white pawn becomes queen (also (e8=Q))
"""
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
#those emojis suck so will implement when emojis will be better
charToBlackEmoji = {'R': '♖', 'N': '♘', 'B': '♗', 'K': '♔', 'Q': '♕', 'P': '♙'}
charToWhiteEmoji = {'R': '♜', 'N': '♞', 'B': '♝', 'K': '♚', 'Q': '♛', 'P': '♟'}
"""
