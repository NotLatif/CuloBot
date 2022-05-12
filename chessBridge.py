import discord
import Main as chessGame

async def loadGame(thread : discord.Thread, bot, players : tuple[discord.Member], fetchThread : tuple[discord.Thread, discord.Embed], ctx):
	"""links bot.py with chess game (Main.py)"""
	p1,p2 = players #p1 is white, p2 is black
	emojis = ('⚪', '🌑') #('🤍', '🖤') (white, black) 	< order matters it's a tuple afterall
	gs = chessGame.Engine.GameState(thread.id)
	chessGame.loadSprites()
	didIllegalMove = [False, ''] #[bool, str]

	boardMessages = [] #needed to delete the last edited board and avoid chat clutter

	chessGame.drawGameState(gs.board, gs.gameID)	#Don't really like this mess, will clean later
	validMoves = gs.getValidMoves()
	with open(chessGame.getOutputFile(gs.gameID), "rb") as fh:
		f = discord.File(fh, filename=chessGame.getOutputFile(gs.gameID))
		boardMessages.append(await thread.send(file=f))

	winner = None
	while True: #gameloop
		p1turn = gs.whiteMoves
		#generate board and moves
		if not didIllegalMove[0] or gs.turnCount == 0: #no need to regenerate if move did not go trhu
			chessGame.drawGameState(gs.board, gs.gameID)
			validMoves = gs.getValidMoves()

		#send board imga to discord
		if gs.turnCount != 0: #Don't resend the first image
			with open(chessGame.getOutputFile(gs.gameID), "rb") as fh:
				f = discord.File(fh, filename=chessGame.getOutputFile(gs.gameID))
				boardMessages.append(await thread.send(file=f))
				await boardMessages[0].delete()
				del boardMessages[0]
		
		
	#MACRO TASK: ask for a move or command
		#1. make an embed with the request
		embed = discord.Embed(
			title= f'Fai una mossa {str(players[not gs.whiteMoves])[:-5]}!',
			description = 'Scrivi in chat posizione iniziale e posizione finale del pedone\ne.g.: A2A4\n\nscrivi "undo" per annullare l\'ultima mossa\nscrivi "stop" per fermare la partita',
			color = 0xf2f2f2 if gs.whiteMoves else 0x030303
		)
		
		#2a. if previous move was illegal modify the embed with the info
		if didIllegalMove[0]:
			embed.title = 'Mossa non valida'
			embed.description = didIllegalMove[1]
			embed.color = 0xdc143c

			didIllegalMove = [False, '']
		
		#2b. if previous move resulted in check modify the embed with the info
		elif gs.inCheck: #using elif, because last move cannot be illegal, so if it is, the player currently in check made an illegal move and should be notified
			embed.title = 'Scacco!'
			embed.description = 'Fai una mossa per difendere il tuo Re'
			embed.color = 0xf88070

		embed.set_footer(text=f'È il turno di {players[not gs.whiteMoves]} {emojis[not gs.whiteMoves]}')#I'm too good at this shit #godcomplex

		#2c. if checkmate or stalemate modify the embed and end the game
		async def roundOverEditEmbed(reason, winner):
			#edit and send the main channel embed
			embed = fetchThread[1]
			embed.title = f'{emojis[gs.whiteMoves]} {reason}\n{emojis[0]} {players[0]} :one: :vs: :zero: {players[1]} {emojis[1]}'
			embed.description = f'Winner: {winner} {emojis[gs.whiteMoves]}' #FIXME actually keep track of score
			embed.set_footer(text=f'ID: {thread.id}')
			await fetchThread[0].edit(embed=embed)
			chessGame.mPrint('GAME', f'Game won by {winner}, <gameID:{gs.gameID}>')

		if gs.checkMate:
			embed.title = 'CHECKMATE!'
			embed.description = f'Congratulazioni {players[gs.whiteMoves]} {emojis[gs.whiteMoves]}'
			embed.color = 0xf2f2f2 if not gs.getWinner() == 'N' else 0x030303 
			embed.set_footer(text='Rivincita?') #TODO add reaction to vote for a rematch: switch teams and keep track of the score (update the embed)
			await roundOverEditEmbed('CHECKMATE', players[gs.whiteMoves])
			break #TODO add scoring system for rematch (after 60 seconds declare game over)

		elif gs.staleMate:
			embed.title = 'Stalemate!'
			embed.description = f'Congratulazioni {players[gs.whiteMoves]}'
			embed.color = 0xf2f2f2 if not gs.getWinner() == 'N' else 0x030303
			embed.set_footer(text='Rivincita?')
			await roundOverEditEmbed('Stalemate!', players[gs.whiteMoves])
			break #TODO add scoring system for rematch (after 60 seconds declare game over)

		
		
		#3. send the embed
		inputAsk = await thread.send(embed=embed)

		#4. await for input
		def check(m):	#check if message was sent in thread using ID
			return m.channel.id == thread.id and m.author in players

		userMessage = await bot.wait_for('message', check=check)

		if p1turn and userMessage.author != p1:
			await userMessage.delete()
			return False
		
		#5. delete the embed to avoid clutter
		await inputAsk.delete()
		chessGame.mPrint("USER", f'{userMessage.author}, comando: {userMessage.content}')
		
	#MACRO TASK: parse user input
		#1. create distinction between input (str) and message (discord.Message)
		userMove = userMessage.content

		#2. Detect if user wants to perform a command
		if(userMove == "undo"): #ctrl-z
			gs.undoMove()
			
		if(userMove == "stop"):
			#send embed to thread
			embed = discord.Embed(title='❌ Partita annullata ❌')
			await thread.send(embed=embed)
			#edit and send the main channel embed
			embed = fetchThread[1]
			embed.description = '❌ Partita annullata ❌'
			embed.color = 0xd32c41
			embed.set_footer(text=f'ID: {thread.id}')
			await fetchThread[0].edit(embed=embed)
			chessGame.mPrint('INFO', f'Game stopped by user, <gameID:{gs.gameID}>')
			break
		
		#3. Parse user input
		userMove = userMove.replace('/', '').replace(',','').replace(' ','').lower()
		chessGame.mPrint('DEBUG', f'userMove: {userMove}')

		#4. Check if user input has valid values
		#FIXME 'A', 'A1', 'A1A' will throw IndexError
		if (userMove[0] not in 'abcdefgh' or userMove[2] not in 'abcdefgh' or 
			userMove[1] not in '12345678' or userMove[3] not in '12345678'):
			didIllegalMove = [True, f'Input invalido formato: A1A1, riprova\nHai inserito: {userMove}\n']
			await userMessage.delete()
			continue
		
	#MACRO TASK: move the pieces
		#1. create a structure to hold the data 	
		userMove = [#omg this is so confusing wth #impostorsyndrome
			#                       rank (1->8)                              file (A->H)
			(chessGame.Engine.Move.ranksToRows[userMove[1]], chessGame.Engine.Move.filesToCols[userMove[0]]),
			(chessGame.Engine.Move.ranksToRows[userMove[3]], chessGame.Engine.Move.filesToCols[userMove[2]])
		]
		
		#2. send the move to the engine for elaboration
		move = chessGame.Engine.Move(userMove[0], userMove[1], gs.board)

		#3. detect if move is valid
		if move in validMoves:
			chessGame.mPrint("GAME", f"Valid move: {move.getChessNotation()}")
			gs.makeMove(move)
		else:
			#3F. if move is invalid notify the user and ask again for input
			didIllegalMove = [True, f'Illegal move {move.getChessNotation()}']
			await userMessage.delete()
			chessGame.mPrint("GAMEErr", "Invalid move.")
			chessGame.mPrint("GAME", f"your move: {move.moveID} ({move.getChessNotation()})")
		