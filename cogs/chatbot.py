from discord.ext import commands

import dialogflow_v2 as dialogflow
from keys import project_id


class ChatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session_client = dialogflow.SessionsClient()

    @commands.command(aliases=['talk', 't'])
    async def chat(self, ctx, *, text):
        """Talk to me"""
        session = self.session_client.session_path(project_id, ctx.author.id)
        # print('Session path: {}\n'.format(session))

        text_input = dialogflow.types.TextInput(text=text, language_code='en-US')

        query_input = dialogflow.types.QueryInput(text=text_input)

        response = self.session_client.detect_intent(session=session, query_input=query_input)

        # print('=' * 20)
        # print('Query text: {}'.format(response.query_result.query_text))
        # print('Detected intent: {} (confidence: {})\n'.format(
        #     response.query_result.intent.display_name,
        #     response.query_result.intent_detection_confidence))
        # print('Fulfillment text: {}\n'.format(
        #     response.query_result.fulfillment_text))

        await ctx.send(response.query_result.fulfillment_text)


def setup(bot):
    bot.add_cog(ChatBot(bot))
