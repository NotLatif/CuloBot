import os
import json
import os
from PIL import Image

spritesFolder = 'chessGame/sprites/'
gamesFolder = f'chessGame/games/'

def doesDesignExist(design) -> bool: return os.path.isdir(f'{spritesFolder}{design}')

def renderBoard(colors, id) -> str:
	"""Reders a chessboards with the given colors and returns it's path"""
	#TODO add bezels with letters/numbers
	print(f'COLORS: {colors}')
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
	def __init__(self, cg, designName, board) -> None:
		self.boardFolder = f'{spritesFolder}{designName}'

		self.boardGS = board # list[][] containing board data
		self.bezels = self.getBoardBezels()
		self.cg = cg

		self.sprites = self.loadSprites()

	def mPrint(self, prefix, value):
		self.cg.mPrint(prefix, value, 'RENDERER')

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

	def drawBoard(self) -> tuple[str]: #TODO if isCheck draw red square
		"""Responsible for the graphics of the game"""
		self.mPrint('INFO', 'Drawing board')
		
		# Opening the image file and converting it to RGBA format.
		boardImg = Image.open(f"{self.boardFolder}/chessboard.png").convert("RGBA")
		squareSizePx = (boardImg.size[0] - self.bezels['left'] - self.bezels['right']) // 8

		#Drawing the pieces on the board
		for r, x in zip(range(8), range(7, -1, -1)):
			for c in range(8):
				piece = self.boardGS[r][c]
				if (piece != "--"):						#r?
					pasteCoords = (self.bezels['left'] + c * squareSizePx, self.bezels['top'] + x * squareSizePx)
					boardImg.paste(self.sprites[piece], pasteCoords, self.sprites[piece])
		self.mPrint('INFO', 'Done')
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
			self.mPrint('WARN', f'Board {self.boardFolder} has no json file, I\'m  assuming no bezel')
			return [0,0]