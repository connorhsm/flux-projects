import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.utils import get
import requests
import util.config_manager as config


class Issue(commands.Cog):

    def __init__(self, flux):
        self.flux = flux

    @commands.command(brief='Create a new issue for DigiPol', help='Create a new issue for the app. The bot will ask you to complete the required information.')
    @commands.max_concurrency(1, per=BucketType.user, wait=False)
    @commands.has_role('App Issue Creator')
    async def issue(self, ctx):
        await ctx.message.delete()

        embed = discord.Embed(description='You\'re now creating a new issue for the app, please complete the following information:', colour=discord.Colour.green())
        await ctx.author.send(embed=embed)

        fields = [['text', 'Title', 256],
                    ['date', 'Start date'],
                    ['date', 'End date'],
                    ['text', 'Question', 256],
                    ['text', 'Description', 256],
                    ['text', 'Sponsor', 256]]
        
        field_handler = self.flux.get_cog('Field')
        ans = await field_handler.field_handler(ctx.author, fields)

        # Last value of ans will be True if all questions were asked
        if len(ans) == 0 or ans[-1] != True:
            return

        # Form dictionary for API request
        issue = {
            "token": config.read(('Bot', 'issue_token')),
            "data": {"chamber": "Public",
                    "short_title": ans[0],
                    "start_date": str(ans[1]),
                    "end_date": str(ans[2]),
                    "question": ans[3],
                    "description": ans[4],
                    "sponsor": ans[5]}}
        
        # Make the API POST request
        resp = requests.post('https://1j56c60pb0.execute-api.ap-southeast-2.amazonaws.com/dev/issue', json=issue)

        # Raise an error if we don't get an OK response
        if resp.status_code != 200:
            raise commands.CommandError(f'POST /dev/issue {resp.status_code} {resp.text}')

        embed = discord.Embed(description='You have successfully created a new issue for the app.', colour=discord.Colour.green())
        await ctx.author.send(embed=embed)


def setup(flux):
    flux.add_cog(Issue(flux))