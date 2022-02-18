import random

import disnake
from disnake.ext import commands
from Tools.exceptions import CustomError
from Tools.buttons import Warns


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(
        description="Можете теперь спокойно выдавать предупреждения uwu."
    )
    @commands.has_permissions(ban_members=True)
    async def warn(self, inter, member: disnake.Member, *, reason: str = None):
        warn_id = random.randint(10000, 99999)
        embed = await self.bot.embeds.simple(title=f"(>-<)!!! {member.name} предупреждён!")
        embed.set_footer(text=f"ID: {warn_id} | {reason if reason else 'Нет причины'}")
        
        if inter.author == member:
            raise CustomError("Зачем вы пытаетесь себя предупредить?")
        elif inter.author.top_role.position <= member.top_role.position:
            raise CustomError("Ваша роль равна или меньше роли упомянутого участника.")
        else:
            embed.description = f"**{member.name}** было выдано предупреждение"
            await self.bot.config.DB.warns.insert_one({"guild": inter.guild.id, "member": member.id, "reason": reason if reason else "Нет причины", "warn_id": warn_id})

        await inter.send(embed=embed)

    @commands.slash_command(
        description="Просмотр всех предупреждений участника"
    )
    async def warns(self, inter, member: disnake.Member = commands.Param(lambda inter: inter.author)):
        if member.bot:
            raise CustomError("Невозможно просмотреть предупреждения **бота**")
        elif await self.bot.config.DB.warns.count_documents({"guild": inter.guild.id, "member": member.id}) == 0:
            raise CustomError("У вас/участника отсутствуют предупреждения.")
        else:
            random_array = [f"{i['reason']} | {i['warn_id']}" async for i in self.bot.config.DB.warns.find({"guild": inter.guild.id, 'member': member.id})]
            data = random.choices(random_array, k=10 if len(random_array) >= 10 else None)
            warn_description = "\n".join(data) if len(data) > 10 else "\n".join(data) + "\n\nЧтобы просмотреть все свои предупреждения, нажмите на кнопку ниже."

            embed = await self.bot.embeds.simple(
                title=f"Вилкой в глаз или... Предупреждения {member.name}",
                description=warn_description,
                thumbnail=member.display_avatar.url,
                footer={
                    "text": "Предупреждения участника", 
                    "icon_url": self.bot.user.avatar.url
                }
            )

        if len(data) < 10:
            view = None
        else:
            view = Warns(member)

        await inter.send(embed=embed, view=view)

    @commands.slash_command(
        description="Удаление предупреждений участника"
    )
    @commands.has_permissions(ban_members=True)
    async def unwarn(self, inter, member: disnake.Member, warn_id: int):
        if inter.author == member:
            raise CustomError("Вы не можете снять предупреждение с себя.")
        elif await self.bot.config.DB.warns.count_documents({"guild": inter.guild.id, "member": member.id}) == 0:
            raise CustomError("У этого чудика нет предупреждений(")
        elif await self.bot.config.DB.warns.count_documents({"guild": inter.guild.id, "warn_id": warn_id}) == 0:
            raise CustomError("Такого warn-ID не существует.")
        else:
            await self.bot.config.DB.warns.delete_one({"guild": inter.guild.id, "member": member.id, "warn_id": warn_id})
            await inter.send(embed=await self.bot.embeds.simple(
                title=f"Снятие предупреждения с {member.name}", 
                description="Предупреждение участника было снято! :з", 
                footer={"text": f"Модератор: {inter.author.name}", "icon_url": inter.author.display_avatar.url}
            )
        )

def setup(bot):
    bot.add_cog(Moderation(bot))
