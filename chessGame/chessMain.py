"""
♟️ Interacts with the engine to play chess
"""
from colorama import Fore, Style, init
import Engine as Engine
import os
import json
import gameRenderer
init()

#helper functions
def doesBoardExist(b) -> bool:
	return True if b in getSavedBoards() else False

def getDesigns() -> list:
	return next(os.walk(gameRenderer.spritesFolder))[1]

def getSavedBoards() -> dict[str:str]:
	try:
		with open('chessGame/boards.json', 'r') as f:
			boards = json.load(f)
	except FileNotFoundError:
		with open('chessGame/boards.json', 'w') as fp:
			boards = {"default":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 0"}
			json.dump(boards, fp , indent=2)
	return boards

def renderBoard(fen:str, id, boardName = 'default') -> tuple[str]:
	if fen.count('/') == 7 and ('k' in fen and 'K' in fen):
		pass #it's a fen
	elif doesBoardExist(fen):
		fen = getSavedBoards()[fen]
	else:
		return 'Invalid'

	print('GENERATING BOARD')
	#a little expensive maybe but whatever nobody will use this code anyways
	cg = ChessGame(str(f'temprender_{id}'))
	gs = Engine.GameState(cg)
	renderer = gameRenderer.GameRenderer(cg, boardName, gs.board)
	gs.boardFromFEN(fen)
	imagePathTuple = renderer.drawBoard()
	return imagePathTuple


class ChessGame: #now a class so it can store the gameID, and for future management
	def __init__(self, gameID, players = [0,0]):
		self.gameID = gameID
		self.spritesFolder = gameRenderer.spritesFolder
		self.board_filename = f"{self.spritesFolder}chessboard.png"
		self.outPath = gameRenderer.gamesFolder
		self.logFile = f'{self.outPath}{self.gameID}.log'
		self.dimension = 8

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
		#p2 can be 'ENGINE' or 'RENDERER
		if p2 == 'ENGINE' : p2 = f'{Fore.YELLOW}{p2}{Fore.RESET} '
		if p2 == 'RENDERER' : p2 = f'{Fore.CYAN}{p2}{Fore.RESET} '
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
		print(f'{style}{col}[{p2}{col}{prefix}] {value}{Fore.RESET}')
		if log:
			self.appendToLog(f'[{p2}{prefix}] {value}')


	def appendToLog(self, text) -> None:
		with open(f'{self.logFile}', 'a') as f:
			f.write(f'{text}\n')

	def getOutputFile(self) -> str:
		return f'{self.outPath}{self.gameID}.png'


##Only use for testing the engine
def main(): 
	cg = ChessGame(1)
	gs = Engine.GameState(cg)

	gs.boardFromFEN(cg.boards['default'])

	renderer = gameRenderer.GameRenderer(cg, 'old', gs.board)
	
	for x in gs.board:
		print(x)

	#cg.loadSprites() #FIXME

	#ask for move
	while True:
		#moveMade = False
		
		renderer.drawBoard() #FIXME
		
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