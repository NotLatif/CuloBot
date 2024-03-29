"""
♟️ Interacts with the engine to play chess
"""
import Engine as Engine
import os
import json
import gameRenderer
from datetime import date

from mPrint import mPrint as mp
def mPrint(tag, text):
    mp(tag, 'chessMain', text)

#helper functions
def doesBoardExist(b) -> bool:
	return True if b in getSavedBoards() else False

def getDesignNames() -> list:
	mPrint('DEBUG', 'design ' + gameRenderer.spritesFolder)
	return next(os.walk(gameRenderer.spritesFolder))[1]

def getSavedBoards() -> dict[str, str]:
	try:
		with open('chessGame/boards.json', 'r') as f:
			boards = json.load(f)
	except FileNotFoundError:
		with open('chessGame/boards.json', 'w') as fp:
			boards = {"default":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 0"}
			json.dump(boards, fp , indent=2)
	return boards

def renderBoard(fen:str, id, designName = 'default') -> tuple[str]:
	if fen.count('/') == 7 and ('k' in fen and 'K' in fen):
		pass #it's a fen
	elif doesBoardExist(fen):
		fen = getSavedBoards()[fen]
	else:
		return 'Invalid'

	mPrint('INFO', 'GENERATING BOARD')
	#a little expensive maybe but whatever nobody will use this code anyways
	cg = ChessGame(str(f'temprender_{id}'))
	gs = Engine.GameState(cg)
	renderer = gameRenderer.GameRenderer(cg, designName, gs)
	gs.boardFromFEN(fen)
	imagePathTuple = renderer.drawBoard()
	return imagePathTuple


class ChessGame: #now a class so it can store the gameID, and for future management
	def __init__(self, gameID, players = ["",""], serverName = "?", round = "?", result = "?", FEN = "?"):
		self.gameID = gameID
		self.spritesFolder = gameRenderer.spritesFolder
		self.board_filename = f"{self.spritesFolder}chessboard.png"
		self.outPath = gameRenderer.gamesFolder
		self.logFile = f'{self.outPath}{self.gameID}.log'
		
		#PEG SPECIFIC:
		self.players = players
		self.date = date.today().strftime("%Y.%m.%d")
		self.round = round
		self.serverName = serverName
		self.result = result
		self.FEN = FEN #initial fen

		self.boards = getSavedBoards()

		if not os.path.exists(self.outPath): #make games folder if it does not exist
			mPrint('DEBUG', 'making games folder')
			os.makedirs(self.outPath)

		if not os.path.exists(f'{self.outPath}\logs'): #create log folder inside games if not exist
			mPrint('DEBUG', 'making logs file')
			os.makedirs(f'{self.outPath}\logs')
		
		with open(f'{self.logFile}', 'w'): #make log file
			pass

		#DO NOT USE mPrint BEFORE THIS POINT (may cause errors)
		mPrint('INFO', f'Initializing game {self.gameID}')
		mPrint('INFO', f'players: {players[0]} vs {players[1]}')


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

	renderer = gameRenderer.GameRenderer(cg, 'old', gs)
	
	for x in gs.board:
		print(x)

	#cg.loadSprites() #FIXME

	#ask for move
	while True:
		#moveMade = False
		
		renderer.drawBoard() #FIXME
		
		mPrint('DEBUG', 'Requesting board FEN')
		mPrint('GAME', f'FEN: {gs.getFEN()}')
		#if moveMade:
		validMoves = gs.getValidMoves()

		if gs.checkMate:
			mPrint('GAME', 'CHECKMATE!')
			break
		elif gs.staleMate:
			mPrint('GAME', 'StaleMate!')
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

			mPrint("USER", playerMoves)
			
			move = Engine.Move(playerMoves[0], playerMoves[1], gs.board)
		
		else: #move is probably in algebraic notation (or a typo)
			move = Engine.Move.findMoveFromAlgebraic(userMove, validMoves)

		moveMade = False
		for i in range(len(validMoves)):
			if move == validMoves[i]:
				mPrint("GAME", f"Valid move: {move.getChessNotation()}")
				
				gs.makeMove(validMoves[i]) #play the move generated by the engine
				
				moveMade = True
		if not moveMade:
			mPrint("GAMEErr", "Illegal move.")

if __name__ == '__main__':
	main()