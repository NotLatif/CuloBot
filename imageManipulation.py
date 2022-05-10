from PIL import Image

def main():
    boardImg = "chess/chessboard.png"
    output = "chess/out.png"

    posy = {
#       n :  y
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
        "A" : 40,
        "B" : 96,
        "C" : 153,
        "D" : 209,
        "E" : 265,
        "F" : 321,
        "G" : 377,
        "H" : 433
    }
    class Piece:
        def __init__(self, filename, position, type) -> None:
            """
            Chess piece constructor
            
            :param filename: The name of the file that contains the image of the sprite
            :param position: (x, y)
            :param type: (P, T, A, C, R, Re)
            """
            filename = self.name
            position = self.position #(x, y)
            type = self.type
        
        def isValidMove(self, newPos) -> bool:
            pass
        
        def getSprite(self) -> str:
            return self.filename

    class Chess:
        def __init__(self, board_filename, p1, p2) -> None:
            board_filename = self.board_filename
            p1 = self.p1
            p2 = self.p2

        def boardInit(self) -> None:
            pass

        def boardUpdate(self, piece, position) -> Image:
            try: 
                with Image.open(self.board_filename) as board:
                    w, h = board.size
                    board = board.convert("RGBA")

                    np = Image.open("chess/NRe.png").convert("RGBA")

                    for x in posx:
                        for y in posy:
                            board.paste(np, (posx[x], posy[y]), np)
    

                    board.save(output) #send
                    return board
            except IOError as e:
                print("IOError")
                print(e.__traceback__)
    
    #game
    blacks = [
        Piece("chess/NT.png", (posx["A"], posy[1]), "T"),
        Piece("chess/NA.png", (posx["B"], posy[1]), "A"),
        Piece("chess/NC.png", (posx["C"], posy[1]), "C"),
        Piece("chess/NR.png", (posx["D"], posy[1]), "R"),
        Piece("chess/NRe.png", (posx["E"], posy[1]), "Re"),
        Piece("chess/NC.png", (posx["F"], posy[1]), "C"),
        Piece("chess/NA.png", (posx["G"], posy[1]), "A"),
        Piece("chess/NT.png", (posx["H"], posy[1]), "T"),
        Piece("chess/NP.png", (posx["A"], posy[2]), "P"),
        Piece("chess/NP.png", (posx["B"], posy[2]), "P"),
        Piece("chess/NP.png", (posx["C"], posy[2]), "P"),
        Piece("chess/NP.png", (posx["D"], posy[2]), "P"),

    ]
    whites = [
        Piece("chess/NT.png", (posx["A"], posy[1]), "T"),
        Piece("chess/NA.png", (posx["B"], posy[1]), "A"),
        Piece("chess/NC.png", (posx["C"], posy[1]), "C"),
        Piece("chess/NR.png", (posx["D"], posy[1]), "R"),
        Piece("chess/NRe.png", (posx["E"], posy[1]), "Re"),
        Piece("chess/NC.png", (posx["F"], posy[1]), "C"),
        Piece("chess/NA.png", (posx["G"], posy[1]), "A"),
        Piece("chess/NT.png", (posx["H"], posy[1]), "T"),
    ]


    game = Chess(boardImg, "p1", "p2")


if __name__ == '__main__':
    main()

#board = board.rotate(180)

#area = (0,0,w/2,h/2)
#board = board.crop(area)

#board = board.resize((w//2,h//2))