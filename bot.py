# -*- coding: utf-8 -*-
import discord
from discord import Embed
from discord.ext import tasks
from datetime import datetime
import os
import requests
import random
import json

TOKEN = os.environ["TOKEN"]
client = discord.Client(intents=discord.Intents.all())


# 次回送信予定時刻を06:00-8:30までの間でランダムに設定
def setting_time_set():
    setting_time_h = random.randint(6, 8)
    if setting_time_h == 8:
        setting_time_m = random.randint(0, 30)
    else:
        setting_time_m = random.randint(0, 59)

    setting_time = f"{setting_time_h:02}:{setting_time_m:02}"
    return setting_time


def set_tem():
    choice_list = ["３６．４", "３６．５", "３６．６"]
    choice_ans = random.choice(choice_list)  # 36.4-36.6までの間でランダムに選択
    return choice_ans


time_set = setting_time_set()  # 起動時に初回の次回送信時刻を設定
tem_set = set_tem()


# Embedの関数
async def template_embed(message, title, name_1, name_2, value_1, color, description=None):
    ch = client.get_channel(message)
    embed_time = datetime.now().strftime("%Y年%m月%d日-%H:%M")
    embed = Embed(title=title, description=description, color=color)
    embed.add_field(name=name_1, value=f"{value_1}", inline=True)
    embed.add_field(name=name_2, value=f"{tem_set}", inline=True)
    embed.set_footer(text=f"{embed_time}")
    await ch.send("<@343956207754805251>")
    await ch.send(embed=embed)


@client.event
async def on_ready():
    await template_embed(message=768274673984208926, title="起動ログ", name_1="次回の送信予定時刻", value_1=time_set,
                         name_2="送信予定の体温", color=discord.Color.orange())


@client.event
async def on_message(message):
    if message.content == "/reset":
        await reset(message)

    if message.content == "/now":
        await now(message)


async def reset(message):
    global time_set
    global tem_set

    time_set = setting_time_set()
    tem_set = set_tem()

    await template_embed(message=768274673984208926, title="リセットされました", name_1="次回の送信予定時刻", name_2="送信予定の体温",
                         value_1=time_set, color=discord.Color.purple())
    await template_embed(message=message.channel.id, title="リセットされました",  name_1="次回の送信予定時刻", name_2="送信予定の体温",
                         value_1=time_set, color=discord.Color.purple())


async def now(message):
    await template_embed(message=message.channel.id, title="現在の状況", name_1="次回の送信予定時刻", name_2="送信予定の体温",
                         value_1=time_set, color=discord.Color.greyple())


@tasks.loop(seconds=60)
async def loop():
    global time_set
    global tem_set

    now_t = datetime.now().strftime('%H:%M')
    print(f"現在の時刻：{now_t}／送信予定時刻：{time_set}／送信予定体温：{tem_set}")

    if now_t == time_set:  # 送信予定時刻になった？
        dt_now = datetime.now().strftime("%Y-%m-%d")  # 現在時刻を2020-01-01の形で取得、dt_nowに格納

        file_name = "cfg.json"
        with open(file_name, "r", encoding="utf-8")as f:
            cfg = json.load(f)
            cfg["output"]["ans_1"] = f"{dt_now}"
            cfg["output"]["ans_4"] = f"{tem_set}"

            params = {"entry.{}".format(cfg["entry"][k]): cfg["output"][k] for k in cfg["entry"].keys()}
            res = requests.get(cfg["form_url"] + "formResponse", params=params)

        if res.status_code == 200:
            await template_embed(message=768274673984208926, title="ログ情報", description=f"[URL]({res.url})",
                                 name_1="完了状態", name_2="送信された体温", value_1="成功しました", color=discord.Color.green())
        else:
            res.raise_for_status()
            await template_embed(message=768274673984208926, title="ログ情報", name_1="完了状態", name_2="送信予定だった体温",
                                 value_1="エラーが発生しました。", color=discord.Color.red())

    else:
        if now_t == "21:00":
            time_set = setting_time_set()
            tem_set = set_tem()
            await template_embed(message=768274673984208926, title="送信時刻更新のお知らせ", name_1="次回の送信予定時刻", name_2="送信予定の体温",
                                 value_1=time_set, color=discord.Color.blue())


loop.start()
client.run(TOKEN)
