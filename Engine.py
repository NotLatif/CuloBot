"""
Stores information about the current game, detects legal moves, logs moves, etc
"""
class GameState():
    def __init__(self) -> None:
        #board: 8x8 2d list of str (2chr)
        #N = Nero, B = Bianco, Torre Alfiere Cavallo Queen King Pedone
        self.board = [
            ["BT", "BC", "BA", "BQ", "BK", "BA", "BC", "BT"], #A Bianco 
            ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"], #B
            ["--", "--", "--", "--", "--", "--", "--", "--"], #C
            ["--", "--", "--", "--", "--", "--", "--", "--"], #D
            ["--", "--", "--", "--", "--", "--", "--", "--"], #E
            ["--", "--", "--", "--", "--", "--", "--", "--"], #F
            ["NP", "NP", "NP", "NP", "NP", "NP", "NP", "NP"], #G
            ["NT", "NC", "NA", "NQ", "NK", "NA", "NC", "NT"], #H Nero 
        ]
        self.whiteMoves = True
        self.moveLog = []

    def makeMove(self, move):
        """
        Makes a move and logs it
        
        :param move: the move to be made
        """
        #we can assume the move is valid
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteMoves = not self.whiteMoves

    def undoMove(self):
        """
        Undo last move
        """
        if (len(self.moveLog) != 0):
            lastMove = self.moveLog.pop()
            self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
            self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
            self.whiteMoves = not self.whiteMoves

    def getValidMoves(self):
        #All moves considering checks (if you move a piece do you expose the K?)
        return self.getAllPossibleMoves() #temp.
        

    def getAllPossibleMoves(self):
        #generating the moves
        moves = []
        for r in range(len(self.board)):  #foreach col
            for c in range(len(self.board[r])): #foreach row (of col)
                pieceColor = self.board[r][c][0] 
                #??
                if (pieceColor == "B" and self.whiteMoves) or (pieceColor == "N" and not self.whiteMoves):
                    piece = self.board[r][c][1]
                    if piece == "P": #pedone
                        self.getPMoves(r, c, moves)
                    elif piece == "T":
                        self.getTMoves(r, c, moves)
        return moves

    def getPMoves(self, r, c, moves):   #FIXME
        if self.whiteMoves: #pedoni bianchi
            #is the square in front empty?
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2] == "--": #If it's the first move and can go 2 up
                    moves.append(Move((r, c), (r+2, c), self.board))
        return moves

    def getTMoves(self, r, c, moves):
        pass



class Move():
    ranksToRows = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6, "8": 7}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, boardState) -> None:
        self.startCol = startSq[0]       #A
        self.startRow = startSq[1]       #1
        self.endCol = endSq[0]       #B 
        self.endRow = endSq[1]       #1
        self.pieceMoved = boardState[self.startRow][self.startCol]
        self.pieceCaptured = boardState[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 +self.endCol
        print(f"moveID: {self.moveID}")

    def __eq__(self, other: object) -> bool:
            if isinstance(other, Move):
                return self.moveID == other.moveID
            return false

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]