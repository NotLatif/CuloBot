import asyncio
import random
import discord
import Main as chessGame

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

def getWinner(players, score) -> bool:
	if score[0] == score[1]:
		return "Pareggio"
	return players[0] if score[0]>score[1] else players[1]

async def loadGame(threadChannel : discord.Thread, bot, players : list[discord.Member], fetchThread : tuple[discord.Thread, discord.Embed]):
	"""links bot.py with chess game (Main.py)
		
	"""
	"""TODO
	- Mini database of games won / games lost
	- keep track also of scores between players
		-eg:	("luigi", "Mario", 23, 25) -> meaning that of all the game played between luigi VS mario ever
												luigi won 23 times and mario won 25 times
	- Add support for chess notation input (implement in Engine.py or watever)
	- keep track of move history between different rounds and don't delete them after each one (maybe also store them in the mini database
	- (not important): thread.id does not change with each round, so the script will only save the last game output file 
	- add more info to the mPrint and log the important stuff
	- [BUG] when voting for a rematch one player can vote 2 times alone and get a rematch
	- FIXME OH COME ON WTF WHY ARE ALL COLORS BACKWARDS I CAN'T
	"""
	
	score = [0, 0]
	emojis = ('⚪', '🌑') #('🤍', '🖤') (white, black) 	< order matters it's a tuple afterall
	
	while True: #matchloop
		p1,p2 = players #p1 is white, p2 is black (will switch every match)

		didIllegalMove = [False, ''] #[bool, str]
		boardMessages = [] #needed to delete the last edited board and avoid chat clutter
							#this will keep max two boards loaded at a time [board0, board1]
							#will delete the last -> [board1, board2]

		gs = chessGame.Engine.GameState(threadChannel.id)
		chessGame.loadSprites()
		chessGame.drawGameState(gs.board, gs.gameID)	#Don't really like this mess, will clean later
		validMoves = gs.getValidMoves()

		#send first board
		with open(chessGame.getOutputFile(gs.gameID), "rb") as fh:
			f = discord.File(fh, filename=chessGame.getOutputFile(gs.gameID))
			boardMessages.append(await threadChannel.send(file=f)) #add first board to list

		while True: #gameloop
			whitesTurn = not gs.whiteMoves #needed to avoid confusion, because: wM = gs.whiteMoves
				#if wM == True:  players[not wM] -> p1	(notWm is 0)	equal to players[0] < True = 1
				#if wM == False: players[not wM] -> p2	(notWm is 1)	equal to players[0] < False = 0
				#this tripped me up, but basically the players tuple is backwards, wM returns True (1)
					#but players[1] is Black, so just invert that
			lastTurn = gs.whiteMoves
				#needed to avoid confusion when calling checks checkmates etc because, e.g.: 
				#winner[not whitesTurn] feels weird/wrong and can lead to confusion
				#TODO reorginize code logic to avoid this variable

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
				title= f'Fai una mossa {str(players[whitesTurn])[:-5]}!',
				description = 'Scrivi in chat posizione iniziale e posizione finale del pedone\ne.g.: A2A4\n\nscrivi "undo" per annullare l\'ultima mossa\nscrivi "stop" per fermare la partita',
				color = 0xf2f2f2 if not whitesTurn else 0x030303
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

			embed.set_footer(text=f'È il turno di {players[whitesTurn]} {emojis[whitesTurn]}')#I'm too good at this shit #godcomplex

			#2c. if checkmate or stalemate modify the embed and end the game
			async def roundOverActions(reason : str, players : list[discord.Member], rematchMsg : discord.Message):
				winner = players[lastTurn] #winner is whoever had the turn BEFORE the current one
				chessGame.mPrint('GAME', f'Game won by {winner}, <gameID:{gs.gameID}>')
				
				#edit and send the main channel embed
				embed = fetchThread[1]
				embed.title = f'{reason}\n{emojis[0]} {players[0]} {num2emoji(score[0])} :vs: {num2emoji(score[1])} {players[1]} {emojis[1]}'
				embed.description = f'Match winner: {str(winner)[:-5]} {emojis[lastTurn]}\nGame winner: {f"{getWinner(players, score)}"}' #FIXME actually keep track of score
				embed.set_footer(text=f'ID: {threadChannel.id}, now voting for rematch...')
				embed.color = 0xf2f2f2 if not gs.getWinner() == 'N' else 0x030303 
				await fetchThread[0].edit(embed=embed)
				
				#ask for another round
				reactions = ('⛔', '✅')
				await rematchMsg.add_reaction(reactions[0])
				await rematchMsg.add_reaction(reactions[1])
				
				def check1(reaction, user): #TODO check if the different reactions are from different user (and not one user reacting 2 times)
					return str(reaction.emoji) in reactions and user != bot.user
				def check2(reaction, user):
					return str(reaction.emoji) in reactions and user != bot.user
				players = [0, 0]
				
				async def notEnoughVotes():
					newThreadName = f'GG, {str(players[0])[:-5]} {score[0]}-VS-{score[1]} {str(players[1])[:-5]}'
					embed = discord.Embed(
						title = 'Non Hanno votato abbastanza giocatori.',
						colour = 0xbe1931
					)
					await rematchMsg.edit(embed = embed)
					
					embed.title = f'-- GAME OVER --\n{emojis[0]} {players[0]} {num2emoji(score[0])} :vs: {num2emoji(score[1])} {players[1]} {emojis[1]}'
					embed.colour = 0xf2f2f2 if not getWinner(players, score) == 'N' else 0x030303
					embed.set_footer(text=f'ID: {threadChannel.id}')
					await fetchThread[0].edit(embed=embed)
					await threadChannel.edit(name = f'{newThreadName}', reason=reason, locked=True, archived=True)

				try:
					r1, players[0] = await bot.wait_for('reaction_add', timeout=120.0, check=check1)
					r2, players[1] = await bot.wait_for('reaction_add', timeout=120.0, check=check2)
				except asyncio.TimeoutError:
					await notEnoughVotes()
					return 0
				else:
					print(f'reactions: {r1} {r2} == {reactions[1]}')
					if r1.emoji == reactions[1] and r2.emoji == reactions[1]: #both votes are yes
						newEmbedTitle = f'{emojis[0]} {players[0]} {num2emoji(score[0])} :vs: {num2emoji(score[1])} {players[1]} {emojis[1]}'
						newThreadName = f'{str(players[0])[:-5]} {score[0]}-VS-{score[1]} {str(players[1])[:-5]}'
						
						embed = discord.Embed(
							title = 'Rivincita!',
							colour = 0x77b255
						)
						embed.set_footer(text = "Generating rematch... please wait!")
						await rematchMsg.edit(embed = embed)

						embed = fetchThread[1]
						embed.title = f'*Generating rematch...*\n{newEmbedTitle}'
						embed.color = 0xf4900c
						embed.set_footer(text=f'ID: {threadChannel.id}')
						await fetchThread[0].edit(embed=embed)
						await threadChannel.edit(name=newThreadName, reason=reason)

						fetchThread[0].edit()

						#switch players
						p = players[0]
						players[0] = players[1]
						players[1] = p

						#TODO FIXME not really sure if I need to also switch the scores(I think so) it's to late to test with a friend, will do tomorrow maybe
						s = score[0]
						score[0] = score[1]
						score[1] = s

						await asyncio.sleep(random.randint(2, 5))

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
				embed.color = 0xf2f2f2 if not gs.getWinner() == 'N' else 0x030303 
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
				embed.color = 0xf2f2f2 if not gs.getWinner() == 'N' else 0x030303
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

			#a little stupid but loop until get a good message (from the right player)
			validInput = False
			while not validInput: #input loop
				#4. await for input
				def check(m):	#check if message was sent in thread using ID
					return m.channel.id == threadChannel.id and m.author in players

				userMessage = await bot.wait_for('message', check=check)

				#process commands that can be made by both players at any point in the game
				if(userMessage.content == "stop"):
					#send embed to thread
					embed = discord.Embed(title='❌ Partita annullata ❌')
					await threadChannel.send(embed=embed)
					#edit and send the main channel embed
					embed = fetchThread[1]
					embed.title = f'-- GAME OVER --\n{emojis[0]} {players[0]} {num2emoji(score[0])} :vs: {num2emoji(score[1])} {players[1]} {emojis[1]}'
					embed.description = '❌ Partita annullata ❌'
					embed.color = 0xd32c41
					embed.set_footer(text=f'ID: {threadChannel.id}')
					await fetchThread[0].edit(embed=embed)
					await threadChannel.edit(reason='Partita annullata', locked=True, archived=True)
					chessGame.mPrint('INFO', f'Game stopped by user, <gameID:{gs.gameID}>')
					return -1

				if whitesTurn and userMessage.author == p1: #avoid players making moves for the opposite team
					validInput = True #out of the input loop
				elif not whitesTurn and userMessage.author == p2: #TODO check with friend if this is backwards
					validInput = True
				else:
					await userMessage.delete()
			
			#5. delete the embed to avoid clutter
			await inputAsk.delete()
			chessGame.mPrint("USER", f'{userMessage.author}, comando: {userMessage.content}')
			
		#MACRO TASK: parse user input
			#1. create distinction between input (str) and message (discord.Message)
			userMove = userMessage.content

			#2. Detect if user wants to perform a command
			if(userMove == "undo"): #ctrl-z
				gs.undoMove()
			
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