import os
#os.system("pip install english_words")
os.system('pip install nltk')
import nltk

nltk.download('words')
from nltk.corpus import words

setofwords = set(words.words())

import nltk

nltk.download('words')
import discord
from discord.ext import commands
from discord.ext import tasks
from keep_alive import keep_alive

client = discord.Client()
client = commands.Bot(command_prefix=".")

# opens file and saves words to discordle_words
file = open("DiscordleWordList.txt", "r")
discordle_words = file.read().splitlines()
file.close()

#dictionary corresponding with name and lives
lives = {}
daily_word_num = 0
solved = False
secretWord = 'hello'
solver = None
discordle_channel = None


# should loop every 24 hours and send msg plus change word hopefully
@tasks.loop(hours=24.0)
async def new_word():
    # saves secret word which changes daily
    # secretWord = discordle_words[random.randrange(1, len(discordle_words))]
    global solved
    global secretWord
    global daily_word_num
    global discordle_words
    global lives
    global discordle_channel
    solved = False
    lives.clear()
    secretWord = discordle_words[daily_word_num]
    if (daily_word_num < len(discordle_words) - 1):
        daily_word_num += 1
    else:
        daily_word_num = 0

    server_file = open("servers.txt", "r+")
    servers = server_file.readlines()
    print('new_word is running')
    for i in range(len(servers)):
        print(servers[i])
        cur_server = servers[i][:-3]
        try:
          channel_file = open(f"{cur_server}_channel.txt", "r+")
        except:
          return
        channel_id = channel_file.readline()
        print(channel_id)
        channel = client.get_channel(int(channel_id))
        await channel.send(f':date: New daily Discordle is ready! :date:')
        channel_file.close()
    for i in range(len(servers)):
      replace_line("servers.txt", i, f'{servers[i][:-3]} 0\n')
    server_file.close()


@client.event
async def on_ready():
    new_word.start()
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name="!help for more"))


@client.event
async def on_message(message):
    message_author = message.author.name
    global solved
    global secretWord
    global solver
    global discordle_channel
    global lives
    
    solved_return = False
    server_in_list = False
    list = []
    server = message.guild.name.strip(' ')
    f = open('servers.txt', "a+")
    servers = f.readlines()
    for i in range(len(servers)):
      if(servers[i].strip() == server):
        server_in_list = True
    if (message.content == "!start" and not server_in_list):
        f.write(f'{server} 0\n')
        f.close()
        file = f'{server}_channel.txt'
        f = open(file, "w+")
        if (os.stat(file).st_size == 0):
            f.write(str(message.channel.id))
        await message.channel.send("Discordle is enabled in this channel!")
    returnString = ''
    if message.author == client.user:
        return
    if (not message.content.startswith("!")):
        return
    file = f'{server}_leaderboard.txt'
    f = open(file, "a+")
    f.close()
    if (message.content == "!leaderboard"):
        sort_file(f'{server}_leaderboard.txt')
        lines = open(f'{server}_leaderboard.txt', 'r').readlines()
        loop = 10
        if (os.stat(f'{server}_leaderboard.txt').st_size == 0):
            await message.channel.send(
                "No winners yet. Try guessing the word to be the first winner!"
            )
        else:
            if (len(lines) < 10):
                loop = len(lines)
            for i in range(loop):
                returnString = returnString + f'{i+1}. {lines[i]}'
            await message.channel.send(f'```{returnString}```')
        return
    #if (message.content == "!setchannel"):
    #discordle_channel = message.channel
    #return
    if (message.content == "!help"):
        await message.channel.send(
            "```Discordle is Discords very own competitive/collaborative game of Wordle! \n!help - Displays help message with brief info on Discordle \n!start - command to start the daily game of Discordle in the desired channel \n!leaderboard - Displays the top 10 Discordle users in the server\n!guess <word> - Guess <word> to see if it's today's Discordle ```"
        )
        return
    if (not message.content.startswith("!guess")):
        return
    fs = open("servers.txt", "r")
    server_statuses = fs.readlines()
    for i in range(len(server_statuses)):
      if(server_statuses[i][:-3] == server and int(server_statuses[i][-2]) == 1):
        await message.channel.send(f'Today\'s Discordle has already been solved by {solver} :tada:')
        solved_return = True 
        return
    fs.close()
    if solved_return:
      return

    string = message.content[7:].lower()
    print(f'{string} is the guessed word\n{secretWord} is the secret word\n')
    if (not string in setofwords):
        await message.channel.send(
            ':no_entry_sign: Invalid guess : Not a valid word :no_entry_sign:')
        return
    if (len(string) != len(secretWord)):
        await message.channel.send(
            ':no_entry_sign: Invalid guess : Wrong Length :no_entry_sign:')
        return
    if (message_author in lives and int(lives[message_author]) == 0):
        await message.channel.send(
            ':no_entry_sign: Invalid guess : You don\'t have any lives left :no_entry_sign:'
        )
        return
    if (message_author not in lives):
        lives[message_author] = 5
    else:
        lives[message_author] = int(lives[message_author]) - 1
    #CONVERT STRING TO EMOTES
    newword = []
    for i in range(len(string)):
        newword.append(f':regional_indicator_{string[i]}: ')
    emoteString = ''.join(newword)
    # if string is not in valid word string list
    await message.channel.send(f'{emoteString}')

    # compare each character
    for i in range(len(string)):
        if (secretWord[i] == string[i]):
            list.append(':green_square: ')
        else:
            list.append(':black_large_square: ')

    # see if any character from message is in the secret word
    for i in range(len(string)):
        for j in range(len(string)):
            if (secretWord[j] == string[i]):
                if (list[i] != ':green_square: '):
                    list[i] = ':yellow_square: '

    for k in range(len(string)):
        countS = 0
        countSW = 0
        if (list[k] == ':yellow_square: '):
            for l in range(len(string)):
                if (string[k] == secretWord[l]):
                    countSW = countSW + 1
                if (string[k] == string[l]
                        and list[l] != ':black_large_square: '):
                    countS = countS + 1
        if (countS > countSW):
            list[k] = ':black_large_square: '
    returnString = ''.join(list)
    await message.channel.send(returnString)
    counter = 0
    for i in list:
        if (i == ':green_square: '):
            counter = counter + 1
    if (counter == len(string)):
        solver = message.author.name
        await message.channel.send(
            f'Today\'s Discordle has been solved by {message.author.mention} :tada:'
        )
        f = open("servers.txt", "r+")
        server_lines = f.readlines()
        print("SOMEHTING")
        for i in range(len(server_lines)):
          if(server_lines[i][:-3].strip() == server):
            replace_line("servers.txt", i, f'{server} 1\n')         
        f.close()
        lineNum = -1
        file = f'{server}_leaderboard.txt'
        f = open(file, "r+")
        Lines = f.readlines()
        present = False
        for line in Lines:
            lineNum = lineNum + 1
            if (line[:-3] == message.author.name):
                print(f"{line[:-3]} = {message.author.name}")
                replace_line(file, lineNum, f"{line[:-2]}{int(line[-2]) + 1}\n")
                present = True
                print("present = true")
                return   
        f.close()
        if (not present):
            print("present = false")
            f = open(file, 'a')
            f.write(f"{message.author.name} 1\n")
            f.close()
        print(server)
    else:
        if (lives[message_author] > 4):
            await message.channel.send(
                f'{message.author.name} has {lives[message_author]} lives left :sparkling_heart:'
            )
        elif (lives[message_author] > 2):
            await message.channel.send(
                f'{message.author.name} has {lives[message_author]} lives left :heart:'
            )
        elif (lives[message_author] > 0):
            await message.channel.send(
                f'{message.author.name} has {lives[message_author]} lives left :mending_heart:'
            )
        else:
            await message.channel.send(
                f'{message.author.name} has {lives[message_author]} lives left :broken_heart:'
            )


def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def sort_file(file):
    # Swap the elements to arrange in order
    f = open(file, "r+")
    list = f.readlines()
    for iter_num in range(len(list) - 1, 0, -1):
        for x in range(iter_num):
            if int(list[x][-2]) < int(list[x + 1][-2]):
                temp = list[x]
                list[x] = list[x + 1]
                list[x + 1] = temp
    line_num = len(list)
    f.close()
    f = open(file, "w")
    #for x in range(line_num):
    #print(f'{list[x]}{x}\n')
    line_num = len(list)
    for x in range(line_num):
        f.write(f'{list[x]}')
    f.close()


keep_alive()
client.run('insert_token_here')
