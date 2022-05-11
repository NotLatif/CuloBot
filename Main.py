"""
Input, interacts with engine, makes image
"""
from email.mime import image
from PIL import Image
import Engine

board_filename = "chess/chessboard.png"
output = "chess/out.png"

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

def mPrint(state, value):
    print(f"[{state}] : {value}")

def loadSprites() -> None:
    """
        Inizializza la dict sprites con le immagini delle pedine
    """
    pieces = ["NT", "NA", "NC", "NQ", "NK", "NP", "BT", "BA", "BC", "BQ", "BK", "BP"]
    for piece in pieces:
        sprites[piece] = Image.open(f"chess/{piece}.png").convert("RGBA")
    #possiamo accedere ad uno sprite così e.g.: sprites["BP"]

def drawGameState(boardGS) -> Image:
    """Responsible for the graphics of the game"""
    #Drawing the pieces on the board
    boardImg = Image.open(f"{board_filename}").convert("RGBA")
    for c, x in enumerate(posx):
        for r, y in enumerate(posy):
            piece = boardGS[r][c]
            if (piece != "--"):
                boardImg.paste(sprites[piece], (posx[x], posy[y]), sprites[piece])
    boardImg.save(output)
    return boardImg


def main():
    gs = Engine.GameState()
    loadSprites()
    

    #ask for move
    while True:
        #moveMade = False
        mPrint("DEBUG", "Generating board")
        drawGameState(gs.board)
        
        #if moveMade:
        mPrint("DEBUG", "Generating possible moves")
        validMoves = gs.getAllPossibleMoves()
        

        userMove = input("Move (A1A1): ").replace('/', '').replace(',','').replace(' ','').lower()
        if(userMove == "undo"):
            gs.undoMove()
            continue

        playerMoves = [#omg this is so confusing
            #                          rank (1)                              file (A)
            (Engine.Move.ranksToRows[userMove[1]], Engine.Move.filesToCols[userMove[0]]),
            (Engine.Move.ranksToRows[userMove[3]], Engine.Move.filesToCols[userMove[2]])
        ]

        print(playerMoves)
        
        move = Engine.Move(playerMoves[0], playerMoves[1], gs.board)
        if move in validMoves:
            print(f"Valid move: {move.getChessNotation()}")
            gs.makeMove(move)
            #moveMade = True
        else:
            mPrint("GAME", "Invalid move:")
            mPrint("GAME", f"your move: {move.moveID} ({move.getChessNotation()})")

    


if __name__ == '__main__':
    main()