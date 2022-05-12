"""
♟️ 
Input, interacts with engine, makes image
#TODO move chessMain and chessEngine in chessGame/ (causes problem when calling main) too lazy to fix for now
"""
from PIL import Image
from colorama import Fore, Style, init
import Engine as Engine
import os


spritesFolder = "chessGame/sprites/"
board_filename = f"{spritesFolder}chessboard.png"
outPath = 'chessGame/games/'

dimension = 8 #8 caselle
sprites = {}
posy = {
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
posx = {
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

def mPrint(prefix, value):
	style = Style.RESET_ALL

	if prefix == 'GAME':
		col = Fore.GREEN
	elif prefix == 'WARN':
		col = Fore.YELLOW
	elif prefix == 'ERROR' or prefix == 'FATAL' or prefix == 'GAMEErr':
		col = Fore.RED
		style = Style.BRIGHT
	elif prefix == 'DEBUG':
		col = Fore.MAGENTA
	elif prefix == 'ENGINE':
		col = Fore.YELLOW
		style = Style.DIM
	elif prefix == 'FUNC':
		col = Fore.BLACK
		reqlog = True
	elif prefix == 'USER':
		col = Fore.CYAN
	else:
		col = Fore.WHITE	
	

	print(f'{style}{col}[{prefix}] {value}{Fore.RESET}')

def loadSprites() -> dict:
	"""
		Inizializza la dict sprites con le immagini delle pedine
	"""
	pieces = ["NT", "NA", "NC", "NQ", "NK", "NP", "BT", "BA", "BC", "BQ", "BK", "BP"]
	for piece in pieces:
		sprites[piece] = Image.open(f"{spritesFolder}{piece}.png").convert("RGBA")
	return sprites
	#possiamo accedere ad uno sprite così e.g.: sprites["BP"]

def drawGameState(boardGS, id) -> Image:
	"""Responsible for the graphics of the game"""
	mPrint("DEBUG", "Generating board")
	
	if not os.path.exists(outPath): #make games folder if it does not exist
		mPrint('DEBUG', f'making path: {outPath}')
		os.makedirs(outPath)

	#Drawing the pieces on the board
	boardImg = Image.open(f"{board_filename}").convert("RGBA")
	for c, x in enumerate(posx):
		for r, y in enumerate(posy):
			piece = boardGS[r][c]
			if (piece != "--"):
				boardImg.paste(sprites[piece], (posx[x], posy[y]), sprites[piece])
	boardImg.save(getOutputFile(id))
	
	mPrint("DEBUG", "Board Generated")
	return boardImg

def getOutputFile(id:int) -> str:
	return f'{outPath}{id}.png'

def main(): 
	gs = Engine.GameState(1)
	loadSprites()
	

	#ask for move
	while True:
		#moveMade = False
		
		drawGameState(gs.board, 1)
		#if moveMade:
		validMoves = gs.getValidMoves()

		userMove = input("Move (A1A1): ").replace('/', '').replace(',','').replace(' ','').lower()
		if(userMove == "undo"):
			gs.undoMove()
			continue

		playerMoves = [#omg this is so confusing
			#                          rank (1)                              file (A)
			(Engine.Move.ranksToRows[userMove[1]], Engine.Move.filesToCols[userMove[0]]),
			(Engine.Move.ranksToRows[userMove[3]], Engine.Move.filesToCols[userMove[2]])
		]

		mPrint("USER", playerMoves)
		
		move = Engine.Move(playerMoves[0], playerMoves[1], gs.board)
		if move in validMoves:
			mPrint("GAME", f"Valid move: {move.getChessNotation()}")
			gs.makeMove(move)
			#moveMade = True
		else:
			mPrint("GAMEErr", "Invalid move.")
			mPrint("GAME", f"your move: {move.moveID} ({move.getChessNotation()})")


if __name__ == '__main__':
	main()