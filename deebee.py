import discord
import ast
from discord.ext import commands
from discord.utils import get

################################
description = "Testing a feature that would allow for the use of discord channels as databases"
TOKEN = 'OTMzODExMTk0MzIwNTMxNDU4.Yem9cg.tUs_UCR3LF4Wsu5HPUgPlERh8po'
REQ_CHANNEL = 802794891364270100
DB_CHANNEL = 955692381460643880

# discord stuff
client = discord.Client()
Embed = discord.Embed
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix="$", description=description, intents=intents)

################################
# MESSAGES #

# Reactions to verify user
BOT_NAME = "Deebee"

COMMAND_DB = "db_query"


################################


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


# TODO: maybe create a feature where the bot encrypts the db in smt like base64?
async def db_select(table_id, row_id):
    """
    Helps select an information from an element in an (unencrypted) database channel
    :param table_id:
    :param row_id:
    :return:
    """
    # maybe in the future it doesn't have to be hardcoded here
    db_channel = client.get_channel(DB_CHANNEL)

    async for message in db_channel.history(limit=200):
        if message.content.startswith(table_id):
            table = message.content[len(table_id) + 1:]

            try:
                table = ast.literal_eval(table)
            except SyntaxError:
                table = "Error with syntax for following table element: " + \
                        message.content[len(table_id) + 1:]

            if type(table) is list:
                if not all(type(x) == int for x in table):
                    table = [str(n).strip() for n in table]

                if row_id:
                    row_id = int(row_id)
                    if len(table) > row_id >= 0:
                        content = str(table[row_id])
                    else:
                        content = "ERROR WITH REQUEST: row number is bigger than table or" + \
                                  " row number not specified for list type."
                else:
                    content = "ERROR WITH REQUEST: row number is bigger than table or" + \
                              " row number not specified for list type."
            elif type(table) is dict:
                # row_id = row_id.replace('"', "'")
                found = False
                for key in table.keys():
                    if str(key) in row_id:
                        content = str(table[key])
                        found = True
                    break
                if not found:
                    content = "ERROR WITH REQUEST: row id was not specified or was not found" +\
                              " in data (of dict type)"
                    # content = row_id
            else:
                content = str(table)
    return content


async def db_parse_request(message):
    request = message.content[len(COMMAND_DB) + 1:]

    # if query includes specific row number
    if "," in request:
        args = request.split(",")
        args = [arg.strip() for arg in args]
        table_id = args[0]
        row_id = args[1]

    # else just go for first element
    else:
        table_id = request.strip()
        row_id = 0

    return table_id, row_id


@client.event
async def on_message(message):
    channel = message.channel

    if message.author == client.user:
        return
    if message.channel.id == REQ_CHANNEL:
        if message.content.startswith(COMMAND_DB):
            table_id, row_id = await db_parse_request(message)
            try:
                content = await db_select(table_id, row_id)
                await channel.send(content)
            except UnboundLocalError:
                await channel.send("Unknown error with command, probably check your syntax!")

client.run(TOKEN)