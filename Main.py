"""
♟️ 
Input, interacts with engine, makes image
#TODO move chessMain and chessEngine in chessGame/ (causes problem when calling main) too lazy to fix for now
"""
from PIL import Image
from colorama import Fore, Style, init
import Engine as Engine
import os
import json


#helper functions
def doesBoardExist(b) -> bool:
	return True if b in getSavedBoards() else False

def getSavedBoards() -> dict[str:str]:
	try:
		with open('chessGame/boards.json', 'r') as f:
			boards = json.load(f)
	except FileNotFoundError:
		with open('chessGame/boards.json', 'w') as fp:
			boards = {"default":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 0"}
			json.dump(boards, fp , indent=2)
	return boards

def renderBoard(fen:str, id) -> tuple[str]:
	if fen.count('/') == 7 and ('k' in fen and 'K' in fen):
		pass #it's a fen
	elif doesBoardExist(fen):
		fen = getSavedBoards()[fen]
	else:
		return 'Invalid'

	print('GENERATING BOARD')
	#a little expensive maybe but whatever nobody will use this code anyways
	cg = ChessGame(str(f'temprender_{id}'))
	cg.loadSprites()
	gs = Engine.GameState(str(f'temprender_{id}'), cg)
	gs.boardFromFEN(fen)
	image = cg.drawGameState(gs.board, str(f'temprender_{id}'))
	return image
	


class ChessGame: #now a class so it can store the gameID, and for future management
	def __init__(self, gameID, players = [0,0]):
		self.gameID = gameID
		self.spritesFolder = "chessGame/sprites/"
		self.board_filename = f"{self.spritesFolder}chessboard.png"
		self.outPath = 'chessGame/games/'
		self.logFile = f'{self.outPath}/logs/{self.gameID}.log'
		self.dimension = 8 #8 caselle
		self.sprites = {}
		self.posy = {
		#   c :  y
			1 : 409,
			2 : 353,
			3 : 297,
			4 : 241,
			5 : 185,
			6 : 129,
			7 : 73,
			8 : 17
		}
		self.posx = {
		#    r  : x
			"A" : 40,
			"B" : 96,
			"C" : 153,
			"D" : 209,
			"E" : 265,
			"F" : 321,
			"G" : 377,
			"H" : 433
		}

		self.boards = getSavedBoards()

		if not os.path.exists(self.outPath): #make games folder if it does not exist
			print('making games folder')
			os.makedirs(self.outPath)

		if not os.path.exists(f'{self.outPath}\logs'): #create log folder inside games if not exist
			print('making logs file')
			os.makedirs(f'{self.outPath}\logs')
		
		with open(f'{self.logFile}', 'w'): #make log file
			pass

		#DO NOT USE mPrint BEFORE THIS POINT (may cause errors)
		self.mPrint('INFO', f'Initializing game {self.gameID}')
		self.mPrint('INFO', f'players: {players[0]} vs {players[1]}')

	def mPrint(self, prefix, value, p2 = '', ):
		#p2 is only used by engine
		log = False
		
		style = Style.RESET_ALL

		if prefix == 'INFO':
			log = True
		if prefix == 'GAME':
			log = True
			col = Fore.GREEN
		elif prefix == 'WARN':
			log = True
			col = Fore.YELLOW
			style = Style.BRIGHT
		elif prefix == 'ERROR' or prefix == 'FATAL' or prefix == 'GAMEErr':
			log = True
			col = Fore.RED
			style = Style.BRIGHT
		elif prefix == 'DEBUG':
			col = Fore.LIGHTMAGENTA_EX
		elif prefix == 'MOVE':
			col = Fore.LIGHTBLACK_EX
		elif prefix == 'VARS':
			col = Fore.LIGHTYELLOW_EX
			style = Style.DIM
		elif prefix == 'FUNC':
			col = Fore.LIGHTBLACK_EX
		elif prefix == 'USER':
			log = True
			col = Fore.CYAN
		else:
			col = Fore.WHITE	
#							  p2 is only used for ENGINE
		print(f'{style}{col}[{Fore.YELLOW}{p2}{Fore.RESET}{col}{prefix}] {value}{Fore.RESET}')
		if log:
			self.appendToLog(f'[{p2}{prefix}] {value}')

	def loadSprites(self) -> dict:
		"""
			Inizializza la dict sprites con le immagini delle pedine
		"""
		pieces = ["BR", "BB", "BN", "BQ", "BK", "BP", "WR", "WB", "WN", "WQ", "WK", "WP"]
		for piece in pieces:
			self.sprites[piece] = Image.open(f"{self.spritesFolder}{piece}.png").convert("RGBA")
		return self.sprites
		#possiamo accedere ad uno sprite così e.g.: sprites["BP"]

	def appendToLog(self, text) -> None:
		with open(f'{self.logFile}', 'a') as f:
			f.write(f'{text}\n')

	def drawGameState(self, boardGS, id) -> tuple[str]: #TODO if isCheck draw red square
		"""Responsible for the graphics of the game"""
		self.mPrint("DEBUG", "Generating board")

		#Drawing the pieces on the board
		boardImg = Image.open(f"{self.board_filename}").convert("RGBA")
		for c, x in enumerate(self.posx):
			for r, y in enumerate(self.posy):
				piece = boardGS[r][c]
				if (piece != "--"):
					boardImg.paste(self.sprites[piece], (self.posx[x], self.posy[y]), self.sprites[piece])
		boardImg.save(self.getOutputFile(id))
		
		self.mPrint("DEBUG", "Board Generated")
		return (self.outPath, id)

	def getOutputFile(self, id:int) -> str:
		return f'{self.outPath}{id}.png'


	


##Only use for testing the engine
def main(): 
	cg = ChessGame(1)
	gs = Engine.GameState(1, cg)
	#gs.boardFromFEN('rrrrkrrr/pp1ppppp/2p4n/3P1p2/5p2/4P2P/PPPP1PP1/RNBQKBNR b - b5 34 2')
	gs.boardFromFEN(cg.boards['default'])
	
	for x in gs.board:
		print(x)

	cg.loadSprites()

	#ask for move
	while True:
		#moveMade = False
		
		cg.drawGameState(gs.board, 1)
		gs.mPrint('DEBUG', 'Requesting board FEN')
		cg.mPrint('GAME', f'FEN: {gs.getFEN()}')
		#if moveMade:
		validMoves = gs.getValidMoves()

		if gs.checkMate:
			cg.mPrint('GAME', 'CHECKMATE!')
			break
		elif gs.staleMate:
			cg.mPrint('GAME', 'StaleMate!')
			break
		
		userMove = input("Move (A1A1): ").replace('/', '').replace(',','').replace(' ','').lower()
		if(userMove == "undo"):
				gs.undoMove()
				continue

		if (len(userMove) == 4 and #this should be enough
				userMove[0] in 'abcdefgh' and userMove[2] in 'abcdefgh' and 
				userMove[1] in '12345678' and userMove[3] in '12345678'): #Move is type A2A2
				
			playerMoves = [#omg this is so confusing
				#                          rank (1)                              file (A)
				(Engine.Move.ranksToRows[userMove[1]], Engine.Move.filesToCols[userMove[0]]),
				(Engine.Move.ranksToRows[userMove[3]], Engine.Move.filesToCols[userMove[2]])
			]

			cg.mPrint("USER", playerMoves)
			
			move = Engine.Move(playerMoves[0], playerMoves[1], gs.board)
		
		else: #move is probably in algebraic notation (or a typo)
			move = Engine.Move.findMoveFromAlgebraic(userMove, validMoves)

		moveMade = False
		for i in range(len(validMoves)):
			if move == validMoves[i]:
				cg.mPrint("GAME", f"Valid move: {move.getChessNotation()}")
				
				gs.makeMove(validMoves[i]) #play the move generated by the engine
				
				moveMade = True
		if not moveMade:
			cg.mPrint("GAMEErr", "Illegal move.")

if __name__ == '__main__':
	main()