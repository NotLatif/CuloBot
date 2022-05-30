import os
import json
import os
from PIL import Image
import Engine

from mPrint import mPrint as mp
def mPrint(tag, text):
    mp(tag, 'chessRenderer', text)

spritesFolder = 'chessGame/sprites/'
gamesFolder = f'chessGame/games/'

def doesDesignExist(design) -> bool: return os.path.isdir(f'{spritesFolder}{design}')

def renderBoard(colors, id) -> str:
	"""Reders a chessboards with the given colors and returns it's path"""
	#TODO add bezels with letters/numbers
	mPrint('INFO' f'COLORS: {colors}')
	new = Image.new(mode="RGBA", size=(1000,1000))
	c1 = Image.new(mode="RGB", size=(125,125), color=colors[0])
	c2 = Image.new(mode="RGB", size=(125,125), color=colors[1])

	turn = True
	for i in range(8):
		for j in range(8):
			if ((i + j + 1) % 2 == 0):
				new.paste(c1, (i*125, j*125))
			else:
				new.paste(c2, (i*125, j*125))
			turn = not turn

	path = f'{spritesFolder}temp/{id}/chessboard'
	
	if not (os.path.exists(spritesFolder + 'temp/')):
		os.mkdir(spritesFolder + 'temp/')
	os.mkdir(spritesFolder + f'temp/{id}')

	new.save(f'{path}.png')

	bezels = {"bezel_left": 0,"bezel_right": 0,"bezel_top": 0}
	with open(f'{path}.json', 'w') as f:
		json.dump(bezels, f, indent=2)
	
	return f'temp/{id}/'
	

class GameRenderer():
	def __init__(self, cg, designName, boardGS : Engine.GameState) -> None:
		self.boardFolder = f'{spritesFolder}{designName}'

		self.boardGS = boardGS # list[][] containing board data
		self.bezels = self.getBoardBezels()
		self.cg = cg

		self.sprites = self.loadSprites()

	def loadSprites(self) -> dict:
		"""
			Inizializza la dict sprites con le immagini delle pedine
		"""
		boardImg = Image.open(f"{self.boardFolder}/chessboard.png").convert("RGBA")
		squareSizePx = (boardImg.size[0] - self.bezels['left'] - self.bezels['right']) // 8

		pieces = ["BR", "BB", "BN", "BQ", "BK", "BP", "WR", "WB", "WN", "WQ", "WK", "WP"]
		sprites = {}
		for piece in pieces:
			sprites[piece] = Image.open(f"{spritesFolder}{piece}.png").convert("RGBA")
			if sprites[piece].size[0] != squareSizePx:
				sprites[piece] = sprites[piece].resize((squareSizePx, squareSizePx))

		return sprites

	def drawBoard(self) -> tuple[str]:
		"""Responsible for the graphics of the game"""
		mPrint('INFO', 'Drawing board')
		
		# Opening the image file and converting it to RGBA format.
		boardImg = Image.open(f"{self.boardFolder}/chessboard.png").convert("RGBA")
		squareSizePx = (boardImg.size[0] - self.bezels['left'] - self.bezels['right']) // 8

		for row in self.boardGS.board:
			print(row)

		def invert(n):
			return 7-n
		
		if self.boardGS.lastMoveStart != (): #Esiste una mossa
			mPrint('DEBUG', f'self.boardGS.lastMoveStart: {self.boardGS.lastMoveStart}')	
			if os.path.isfile(f"{self.boardFolder}/last_move_start.png"):
				lastMoveStart = Image.open(f"{self.boardFolder}/last_move_start.png").convert("RGBA")
				pasteCoords = (self.bezels['left'] + self.boardGS.lastMoveStart[1] * squareSizePx, self.bezels['top'] + invert(self.boardGS.lastMoveStart[0]) * squareSizePx)
				mPrint('DEBUG', f'pasteCoords: {pasteCoords}')				
				boardImg.paste(lastMoveStart, pasteCoords)
			
		if self.boardGS.lastMoveEnd != (): #Esiste una mossa
			mPrint('DEBUG', f'self.boardGS.lastMoveEnd: {self.boardGS.lastMoveEnd}')		
			if os.path.isfile(f"{self.boardFolder}/last_move_end.png"):
				lastMoveEnd = Image.open(f"{self.boardFolder}/last_move_end.png").convert("RGBA")
				pasteCoords = (self.bezels['left'] + self.boardGS.lastMoveEnd[1] * squareSizePx, self.bezels['top'] + invert(self.boardGS.lastMoveEnd[0]) * squareSizePx)
				mPrint('DEBUG', f'pasteCoords: {pasteCoords}')
				boardImg.paste(lastMoveEnd, pasteCoords)
				
			
		if(self.boardGS.inCheck == True): #check / checkmate
			checkPos = self.boardGS.whiteKpos if self.boardGS.whiteMoves else self.boardGS.blackKpos
			if os.path.isfile(f"{self.boardFolder}/king_check.png"):
				checkSquare = Image.open(f"{self.boardFolder}/king_check.png").convert("RGBA")
				pasteCoords = (self.bezels['left'] + checkPos[1] * squareSizePx, self.bezels['top'] + invert(checkPos[0]) * squareSizePx)
				boardImg.paste(checkSquare, (pasteCoords))
			#else: #idk maybe if file is not there, that board does not want to show checks
			#	checkSquare = Image.open(f"{self.cg.spritesFolder}/king_check.png").convert("RGBA")
			

		#Drawing the pieces on the board
		for r, x in zip(range(8), range(7, -1, -1)):
			for c in range(8):
				piece = self.boardGS.board[r][c]
				if (piece != "--"):						#r?
					pasteCoords = (self.bezels['left'] + c * squareSizePx, self.bezels['top'] + x * squareSizePx)
					boardImg.paste(self.sprites[piece], pasteCoords, self.sprites[piece])
		
		mPrint('INFO', 'Done')
		#Compress
		boardImg.resize((300,300)).save(f'{gamesFolder}{self.cg.gameID}.png')
		
		return (f'{gamesFolder}{self.cg.gameID}.png', self.cg.gameID)
	
	def getBoardBezels(self) -> list:
		bezels = {} #left, bottom, right, top
		try:
			data = {}
			with open(f'{self.boardFolder}/chessboard.json', 'r') as f:
				data = json.load(f)

			for key in data:
				bezels[key[6:]] = data[key]
			return bezels

		except Exception:
			mPrint('WARN', f'Board {self.boardFolder} has no json file, I\'m  assuming no bezel')
			return [0,0]