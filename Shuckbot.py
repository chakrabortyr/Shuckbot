import logging
from datetime import datetime

import discord

from modules import tags, imagesearch, metar, imagefun

with open("keys.txt", "r") as file:  # file format: google key, owner ID, avwx key, bot client key on separate lines
    lines = file.read().splitlines()
    googleKey = lines[0]
    ownerID = int(lines[1])
    avwxKey = lines[2]
    clientKey = lines[3]

imagesearch.init(googleKey)
logging.basicConfig(level=logging.INFO)

defaultPrefix = ';'
commands = [
    # {'command': 'prefix <character>', 'info': "Changes the command prefix for the server"},
    {'command': 'i/im/img <query>', 'info': "Google image searches for an image"},
    {'command': 't/tag <tag> | t/tag add/edit <tag> <content> | t/tag owner/remove <tag>',
     'info': 'Access, add, edit, and remove a tag, or find its owner'},
    {'command': 'metar <ICAO airport code>', 'info': 'Meteorological aviation data'},
    {'command': 'ping', 'info': 'Measures Shuckbot\'s ping'},
    {'command': 'hold/holding <image URL / @user>', 'info': 'A perplexed man will hold your image'}
]

client = discord.Client()


@client.event
async def on_message(message):
    if message.clean_content.startswith(';') and not message.author.bot and \
            len(message.clean_content) > 1:  # prefixes.search(q.guild == message.guild.id)[0]['prefix'])

        content = message.clean_content[1:]  # remove prefix

        # if content.lower().startswith("prefix"):
        #     if not message.author.permissions_in(message.channel).manage_roles:
        #         await message.channel.send("You must have the **Manage Roles** permission to do that.")
        #     elif len(content) < 8 or content[7] == ' ':
        #         await message.channel.send("Enter a character to set the prefix to.")
        #     elif len(content) > 8:
        #         await message.channel.send("Only enter one character to set the prefix to.")
        #     else:
        #         prefixes.update({'prefix': content[7]}, q.guild == message.guild.id)
        #         await message.channel.send("Prefix changed to " + content[7] + '.')

        if content.lower().startswith("ping"):
            now = datetime.now()
            sent = await message.channel.send("Measuring ping...")
            diff = sent.created_at - now
            await sent.edit(content="Pong! Shuckbot's ping is **" + str(int(diff.microseconds / 1000)) + "**ms.")

        if content.lower().startswith("help"):
            bill = client.get_user(ownerID)
            embed = discord.Embed()
            embed.title = "Shuckbot help"
            embed.type = "rich"
            embed.colour = discord.Color.gold()
            for item in commands:
                embed.add_field(name=item['command'], value=item['info'], inline=False)
            embed.set_footer(text="Shuckbot, by billofbong", icon_url=bill.avatar_url)
            await message.channel.send(embed=embed)

        if content.lower().startswith(("img", "i", "im")) and ' ' in message.clean_content:
            await imagesearch.search(message)

        if content.lower().startswith(("tag", "t")):
            if ' ' not in message.clean_content:
                await tags.syntax_error(message)
            else:
                arg = content.split(' ')[1].lower()  # the first argument

                if arg == 'add':
                    await tags.add(message)

                elif arg == 'remove' or arg == "delete":
                    await tags.remove(message, ownerID)

                elif arg == 'edit':
                    await tags.edit(message, ownerID)

                elif arg == 'owner':
                    args = message.clean_content.split(' ')
                    tag_owner = client.get_user(tags.owner(message))
                    if tag_owner == 0:
                        await message.channel.send("Tag **" + args[2] + "** does not exist")
                    else:
                        await message.channel.send("Tag **" + args[2] + "** is owned by `" + str(tag_owner) + "`")

                elif arg == 'list':
                    await tags.owned(message)

                else:
                    await tags.get(message)

        if content.lower().startswith("metar"):
            await metar.metar(message, avwxKey)

        if content.lower().startswith(("holding", "hold")):
            await imagefun.holding_imagemaker(message)

    if message.clean_content.lower() == "b" or message.clean_content.lower() == "n":
        await imagesearch.advance(message)

    if message.clean_content.lower().startswith("p") and len(message.clean_content.lower()) <= 3:
        await imagesearch.jump(message)

    if message.clean_content.lower() == "s":
        await imagesearch.stop(message)



client.run(clientKey)
