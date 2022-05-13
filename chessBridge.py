import asyncio
import random
import discord
import Main as chessMain

def num2emoji(num : int):
	words = []
	for digit in str(num):
		if digit == '0': words.append('zero')
		if digit == '1': words.append('one')
		if digit == '2': words.append('two')
		if digit == '3': words.append('three')
		if digit == '4': words.append('four')
		if digit == '5': words.append('five')
		if digit == '6': words.append('six')
		if digit == '7': words.append('seven')
		if digit == '8': words.append('eight')
		if digit == '9': words.append('nine')
	return f':{"::".join(words)}:'

def getOverallWinnerName(players, score) -> str:
	if score[0] == score[1]:
		return "Pareggio"
	return str(players[0]) if score[0]>score[1] else str(players[1])

async def loadGame(threadChannel : discord.Thread, bot, players : list[discord.Member], fetchThread : tuple[discord.Message, discord.Embed]):
	"""links bot.py with chess game (Main.py)
		
		:param threadChannel: the thread where the bot will send messages about the game.
		:param bot: the discord bot client.
		:param players: the chess game players(`discord.Member`) IN THIS ORDER > `[black, white]`
		:param fetchThread: list containing `[the message that created the thread, the embed of the message]`
	"""
	"""TODO
	- Mini database of games won / games lost
	- keep track also of scores between players
		-eg:	("luigi", "Mario", 23, 25) -> meaning that of all the game played between luigi VS mario ever
												luigi won 23 times and mario won 25 times
	- Add support for chess notation input (implement in Engine.py or watever)
	- keep track of move history between different rounds and don't delete them after each one (maybe also store them in the mini database
	- (not important): thread.id does not change with each round, so the script will only save the last game output file 
	- BUG sometimes bot fails to send the board image, possible fix: add 'resend' command to send another one
	- minor BUG, using undo after the first move does not resend image (since gs.turnCount will decrement to 0)
	"""
	
	score = [0, 0]
	emojis = ('🌑', '⚪') #('🖤', '🤍') (black, white) 	< order matters
#	players  [black, white] because: players[False] -> Black, players[True] -> White
# 									useful for using with gs.whiteMoves
	# cg = ChessGame(1)
	# gs = Engine.GameState(1, cg)
	chessGame = chessMain.ChessGame(threadChannel.id, players)
	
	while True: #matchloop
		gs = chessMain.Engine.GameState(threadChannel.id, chessGame)

		didIllegalMove = [False, ''] #[bool, str]
		boardMessages = [] #needed to delete the last edited board and avoid chat clutter
							#this will keep max two boards loaded at a time [board0, board1]
							#will delete the last -> [board1, board2]

		chessGame.loadSprites()
		chessGame.drawGameState(gs.board, gs.gameID)	#Don't really like this mess, will clean later
		validMoves = gs.getValidMoves()

		#send first board
		with open(chessGame.getOutputFile(gs.gameID), "rb") as fh:
			f = discord.File(fh, filename=chessGame.getOutputFile(gs.gameID))
			boardMessages.append(await threadChannel.send(file=f)) #add first board to list

		while True: #gameloop
			turn = gs.whiteMoves #if turn = 1, players[turn] is white, if turn = 0 players[turn is black]
#									 turn = True						  turn = False
			lastTurn = not gs.whiteMoves #needed to find winners

			#generate board and moves
			if not didIllegalMove[0] or gs.turnCount == 0: #no need to regenerate if last move was illegal
				chessGame.drawGameState(gs.board, gs.gameID) #will check below in the code for illegal moves
				validMoves = gs.getValidMoves()

			#send board img to discord
			if gs.turnCount != 0: #Don't resend the first image
				with open(chessGame.getOutputFile(gs.gameID), "rb") as fh:
					f = discord.File(fh, filename=chessGame.getOutputFile(gs.gameID))
					boardMessages.append(await threadChannel.send(file=f))
					await boardMessages[0].delete() #delete last board
					del boardMessages[0] #remove last board from list -> the current one will be at boardMessages[0]
			
		#MACRO TASK: ask for a move or command
			#1. make an embed with the request
			embed = discord.Embed(
				title= f'Fai una mossa {str(players[turn])[:-5]}!',
				description = '''
					Scrivi in chat posizione iniziale e posizione finale del pedone
					e.g.: A2A4\n
					scrivi "undo" per annullare l'ultima mossa
					scrivi "stop" per fermare la partita
				''',
				color = 0xf2f2f2 if (turn == 1) else 0x030303
			)
			
			#2a. if previous move was illegal modify the embed with the info
			if didIllegalMove[0]:
				embed.title = 'Mossa non valida'
				embed.description += f'\n{didIllegalMove[1]}'
				embed.color = 0xdc143c

				didIllegalMove = [False, '']
			
			#2b. if previous move resulted in check modify the embed with the info
			elif gs.inCheck: #using elif, because last move cannot be illegal, so if it is, the player currently in check made an illegal move and should be notified
				embed.title = 'Scacco!'
				embed.description = 'Fai una mossa per difendere il tuo Re'
				embed.color = 0xf88070

			embed.set_footer(text=f'È il turno di {players[turn]} {emojis[turn]}')#I'm too good at this shit #godcomplex

			#2c. GAMEOVER SCRIPT if checkmate or stalemate modify the embed and end the game
			async def roundOverActions(reason : str, players : list[discord.Member], rematchMsg : discord.Message):
				winner = players[lastTurn] #winner is whoever had the turn BEFORE the current one
				chessGame.mPrint('GAME', f'Game won by {winner}, <gameID:{gs.gameID}>')
				
				#edit and send the main channel embed
				embed = fetchThread[1]
				embed.title = f'{reason}\n{emojis[0]} {players[0]} {num2emoji(score[0])} :vs: {num2emoji(score[1])} {players[1]} {emojis[1]}'
				embed.description = f'Match winner: {str(winner)[:-5]} {emojis[lastTurn]}\nOverall winner: {f"{getOverallWinnerName(players, score)}"}'
				embed.set_footer(text=f'ID: {threadChannel.id}, now voting for rematch...')
				embed.color = 0xf2f2f2 if lastTurn == 1 else 0x030303 
				await fetchThread[0].edit(embed=embed)
				
				#ask for another round
				reactions = ('⛔', '✅')
				await rematchMsg.add_reaction(reactions[0])
				await rematchMsg.add_reaction(reactions[1])
				
				votingPlayers = list(players) # < one of the few times learning things in school saved ma A LOT of time 
				#								for who does not know votingPlayers = players is a reference (like an alias)
				#								here I am writing things like people will look at my repo 😢

				async def notEnoughVotes():
					newThreadName = f'GG, {str(players[0])[:-5]} {score[0]}-VS-{score[1]} {str(players[1])[:-5]}'
					embed = discord.Embed(
						title = 'Non Hanno votato abbastanza giocatori.',
						color = 0xbe1931
					)
					await rematchMsg.edit(embed = embed)
					
					embed.title = f'-- GAME OVER --\n{emojis[0]} {players[0]} {num2emoji(score[0])} :vs: {num2emoji(score[1])} {players[1]} {emojis[1]}'
					embed.color = 0xf2f2f2 if players[lastTurn] else 0x030303
					embed.set_footer(text=f'ID: {threadChannel.id}')
					await fetchThread[0].edit(embed=embed)
					await threadChannel.edit(name = f'{newThreadName}', reason=reason, locked=True, archived=True)
				
				def rematchVoteCheck(reaction, user): #TODO check if the different reactions are from different user (and not one user reacting 2 times)
					chessGame.mPrint('DEBUG', f'CHECK1, {user}, {[v.id for v in votingPlayers]}')
					if user in votingPlayers:
						votingPlayers.remove(user)
						return str(reaction.emoji) in reactions and user != bot.user
					return False

				try:
					r1, temp = await bot.wait_for('reaction_add', timeout=120.0, check=rematchVoteCheck)
					r2, temp = await bot.wait_for('reaction_add', timeout=120.0, check=rematchVoteCheck)
				except asyncio.TimeoutError:
					await notEnoughVotes()
					return 0
				else:
					del temp # don't really need it
					print(f'reactions: {r1} {r2} == {reactions[1]}')
					if r1.emoji == reactions[1] and r2.emoji == reactions[1]: #both votes are yes
						chessGame.mPrint('INFO', 'will rematch')
						newEmbedTitle = f'{emojis[0]} {players[0]} {num2emoji(score[0])} :vs: {num2emoji(score[1])} {players[1]} {emojis[1]}'
						newThreadName = f'{str(players[0])[:-5]} {score[0]}-VS-{score[1]} {str(players[1])[:-5]}'
						
						embed = discord.Embed(
							title = 'Rivincita!',
							color = 0x77b255
						)
						embed.set_footer(text = "Generating rematch... please wait!")
						await rematchMsg.edit(embed = embed)

						embed = fetchThread[1]
						embed.title = f'*Generating rematch...*\n{newEmbedTitle}'
						embed.color = 0xf4900c
						embed.set_footer(text=f'ID: {threadChannel.id}')
						print('landmark0')
						await fetchThread[0].edit(embed=embed)
						print('landmark1')
					

						#switch players
						p = players[0]
						players[0] = players[1]
						players[1] = p

						s = score[0]
						score[0] = score[1]
						score[1] = s

						print('before sleep')
						await asyncio.sleep(random.randrange(2, 5))
						print('after sleep')
						print(newThreadName)
						#await threadChannel.edit(name=newThreadName) #BUG game halts after 3rd round?

						embed.title = f'Round {score[0] + score[1] + 1}\n{emojis[0]} {players[0]} {num2emoji(score[0])} :vs: {num2emoji(score[1])} {players[1]} {emojis[1]}'
						embed.color = 0x27E039
						await fetchThread[0].edit(embed=embed)
						return 1
					else:
						await notEnoughVotes()
						return 0

			if gs.checkMate:
				score[lastTurn] += 1
				embed.title = 'CHECKMATE!'
				embed.description = f'Congratulazioni {players[lastTurn]} {emojis[lastTurn]}'
				embed.color = 0xf2f2f2 if lastTurn == 1 else 0x030303 
				embed.set_footer(text='Rivincita? (vota entro 2 minuti)')
				rematchMsg = await threadChannel.send(embed=embed)
				resp = await roundOverActions('CHECKMATE', players, rematchMsg)
				if(resp):
					#rematch
					break
				else:
					#gameOver
					return
				 
			elif gs.staleMate:
				score[lastTurn] += 1
				embed.title = 'Stalemate!'
				embed.description = f'Congratulazioni {players[lastTurn]}'
				embed.color = 0xf2f2f2 if lastTurn == 1 else 0x030303
				embed.set_footer(text='Rivincita? (vota entro 2 minuti)')
				rematchMsg = await threadChannel.send(embed=embed)
				resp = await roundOverActions('Stalemate!', players, rematchMsg)
				if(resp):
					#rematch
					break
				else:
					#gameOver
					return 
			
			#3. send the embed
			inputAsk = await threadChannel.send(embed=embed)

			#4. a little stupid but loop until get a good message (from the right player)
			validInput = False
			command = ''
			while not validInput: #input loop
				#a. await for input
				def check(m):	#check if message was sent in thread using ID
					return m.channel.id == threadChannel.id and m.author in players

				userMessage = await bot.wait_for('message', check=check)

				#b. process commands that can be made by both players at any point in the game
				if(userMessage.content == "stop"):
					#send embed to thread
					embed = discord.Embed(title='❌ Partita annullata ❌')
					await threadChannel.send(embed=embed)
					#edit and send the main channel embed
					embed = fetchThread[1]
					embed.title = f'-- GAME OVER --\n{emojis[0]} {players[0]} {num2emoji(score[0])} :vs: {num2emoji(score[1])} {players[1]} {emojis[1]}'
					embed.description = f'❌ Partita annullata ❌\nOverall winner: {getOverallWinnerName(players, score)}'
					embed.color = 0xd32c41
					embed.set_footer(text=f'ID: {threadChannel.id}')
					await fetchThread[0].edit(embed=embed)
					await threadChannel.edit(reason='Partita annullata', locked=True, archived=True)
					chessGame.mPrint('GAME', f'Game stopped by user, <gameID:{gs.gameID}, user:{userMessage.author}>')
					chessGame.mPrint('GAME', f'Game stats: <{gs.getStats()}>')
					return -1
				
				elif(userMessage.content == "undo"): #ctrl-z
					gs.undoMove()
					break
				
				#c. check if message author has the turn
				if turn == 1 and userMessage.author == players[1]: #avoid players making moves for the opposite team
					validInput = True #out of the input loop
				elif turn == 0 and userMessage.author == players[0]: #TODO check with friend if this is backwards
					validInput = True
				else:
					await userMessage.delete()
			
			#5. delete the embed to avoid clutter
			await inputAsk.delete()
			chessGame.mPrint("USER", f'{userMessage.author}, comando: {userMessage.content}')

			if(userMessage.content == 'undo'):
				continue
			
		#MACRO TASK: parse user input
			#1. create distinction between input (str) and message (discord.Message)
			userMove = userMessage.content

			#2. Detect if user wants to perform a command
			#		Commands below here can only be performed by the player that has the turn
			if(userMove == "command"): #ctrl-z
				pass
			
			#3. Parse user input
			userMove = userMove.replace('/', '').replace(',','').replace(' ','').lower()
			chessGame.mPrint('DEBUG', f'userMove: {userMove}')

			#4. Check if user input has valid values
			if (len(userMove) != 4 or #TODO add support for algebraic notation
				userMove[0] not in 'abcdefgh' or userMove[2] not in 'abcdefgh' or 
				userMove[1] not in '12345678' or userMove[3] not in '12345678'):
				didIllegalMove = [True, f'Input invalido formato: A1A1, riprova\nHai inserito: {userMove}\n']
				await userMessage.delete()
				continue
			
		#MACRO TASK: move the pieces
			#1. create a structure to hold the data 	
			userMove = [#omg this is so confusing wth #impostorsyndrome
				#                       rank (1->8)                              file (A->H)
				(chessMain.Engine.Move.ranksToRows[userMove[1]], chessMain.Engine.Move.filesToCols[userMove[0]]),
				(chessMain.Engine.Move.ranksToRows[userMove[3]], chessMain.Engine.Move.filesToCols[userMove[2]])
			]
			
			#2. send the move to the engine for elaboration
			move = chessMain.Engine.Move(userMove[0], userMove[1], gs.board)

			moveMade = False
			#3. detect if move is valid
			for i in range(len(validMoves)):
				if move == validMoves[i]:
					chessGame.mPrint("GAME", f"Valid move: {move.getChessNotation()}")
					gs.makeMove(validMoves[i]) #play the move generated by the engine
					moveMade = True
			if not moveMade:	
				#if move was not made then
				#3F. if move is invalid notify the user and ask again for input
				didIllegalMove = [True, f'Illegal move {move.getChessNotation()}']
				await userMessage.delete()
				chessGame.mPrint("GAMEErr", "Invalid move.")
				chessGame.mPrint("GAME", f"your move: {move.moveID} ({move.getChessNotation()})")