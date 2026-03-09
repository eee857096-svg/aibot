import discord
from discord.ext import commands
from discord import app_commands
import os, re, random, aiohttp, asyncio
from datetime import datetime

# ══════════════════════════════════════════════════════════
#  ENV
# ══════════════════════════════════════════════════════════
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN        = os.getenv("AI_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TOKEN:
    raise RuntimeError("AI_BOT_TOKEN environment variable is not set.")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable is not set.")

# ══════════════════════════════════════════════════════════
#  GROQ CONFIG
# ══════════════════════════════════════════════════════════
GROQ_URL    = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL  = "llama-3.3-70b-versatile"
GROQ_SYSTEM = (
    "You are Elliot, a friendly and funny AI assistant living inside a Discord server called Crimson Gen. "
    "You have a casual, Gen Z personality — you use words like 'bro', 'fr', 'ngl', 'W', 'L', 'no cap' etc naturally. "
    "Keep responses SHORT and Discord-friendly — 1-3 sentences max unless the question genuinely needs more. "
    "Never use giant walls of text. Use emojis where it feels natural. "
    "Be helpful, accurate, and entertaining. If you don't know something, say so honestly. "
    "Do NOT use markdown headers or bullet lists unless specifically asked."
)

# ══════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════
AKIF_USERNAME = "akif_47411"
BOT_NAME      = "Elliot"
CRIMSON       = 0xDC143C
C_SUCCESS     = 0x2ECC71
C_ERROR       = 0xE74C3C
C_WARNING     = 0xF39C12
C_INFO        = 0x5865F2
C_AI          = 0x9B59B6

AKIF_RESPONSES = [
    "👑 **{mention} is the AURA KING** 👑\nNobody comes close. The drip, the vibe, the presence — completely unmatched.",
    "⚡ Someone just mentioned **{mention}**?? The AURA KING has been summoned. Bow down. 👑",
    "🔥 **{mention}** — certified Aura King. His aura level? **IMMEASURABLE**. Scientists are baffled.",
    "💎 {mention} walks in and the whole vibe shifts. That's what an Aura King does. 👑✨",
    "📊 **Aura Level Check:**\n> Everyone else: 📉📉📉\n> **{mention}**: 📈📈📈 OFF THE CHARTS 👑",
    "🌟 Ah yes, **{mention}** — the man, the myth, the Aura King. His aura radiates across dimensions. 👑",
    "💀 The server felt a disturbance... turns out someone mentioned **{mention}**, the one and only Aura King. 👑",
]

# ══════════════════════════════════════════════════════════
#  GROQ AI ENGINE
# ══════════════════════════════════════════════════════════
# Per-channel conversation history {channel_id: [{"role":..,"content":..}]}
chat_history = {}
MAX_HISTORY  = 20   # messages kept per channel

async def ask_groq(channel_id: int, user_message: str) -> str:
    """Send message to Groq and return response. Maintains history per channel."""
    if channel_id not in chat_history:
        chat_history[channel_id] = []

    # Add user message to history
    chat_history[channel_id].append({"role": "user", "content": user_message})

    # Trim history if too long
    if len(chat_history[channel_id]) > MAX_HISTORY:
        chat_history[channel_id] = chat_history[channel_id][-MAX_HISTORY:]

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": GROQ_SYSTEM}] + chat_history[channel_id],
        "max_tokens": 512,
        "temperature": 0.85,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_URL, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"].strip()
                    # Save assistant reply to history
                    chat_history[channel_id].append({"role": "assistant", "content": reply})
                    return reply
                elif resp.status == 429:
                    return "I'm getting rate limited rn 😅 Try again in a sec!"
                else:
                    text = await resp.text()
                    print(f"❌ Groq error {resp.status}: {text}")
                    return f"Something went wrong on my end 😭 (Error {resp.status})"
    except asyncio.TimeoutError:
        return "Took too long to respond 😭 Try again!"
    except Exception as e:
        return f"Ran into an error bro 😭 Try again!"

# ══════════════════════════════════════════════════════════
#  BOT INIT
# ══════════════════════════════════════════════════════════
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="e!", intents=intents)

# ── Storage ──
ai_enabled   = {}   # {guild_id: bool}
ai_channel   = {}   # {guild_id: channel_id | None}
bot_start_time = None

# ══════════════════════════════════════════════════════════
#  EMBED HELPERS
# ══════════════════════════════════════════════════════════
def base(title="", desc="", color=CRIMSON):
    return discord.Embed(title=title, description=desc, color=color, timestamp=datetime.utcnow())

def ok(t, d=""):    return base(f"✅  {t}", d, C_SUCCESS)
def err(t, d=""):   return base(f"❌  {t}", d, C_ERROR)
def info(t, d=""):  return base(f"ℹ️  {t}", d, C_INFO)

def ft(e, text="Elliot AI", icon=None):
    e.set_footer(text=text, icon_url=icon)
    return e

# ══════════════════════════════════════════════════════════
#  EVENTS
# ══════════════════════════════════════════════════════════
@bot.event
async def on_ready():
    global bot_start_time
    bot_start_time = datetime.utcnow()
    try:
        synced = await bot.tree.sync()
        print(f"✅  Elliot AI ready as {bot.user} — {len(synced)} commands synced")
    except Exception as e:
        print(f"❌  Sync failed: {e}")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="your questions 🤖"),
        status=discord.Status.online
    )

@bot.event
async def on_message(msg: discord.Message):
    if msg.author.bot: return

    # ── Akif Aura King ────────────────────────────────────────
    for mentioned in msg.mentions:
        name = (mentioned.name or "").lower()
        gname = (getattr(mentioned, 'global_name', "") or "").lower()
        if AKIF_USERNAME.lower() in name or AKIF_USERNAME.lower() in gname:
            await msg.channel.send(random.choice(AKIF_RESPONSES).format(mention=mentioned.mention))

    # ── AI trigger check ──────────────────────────────────────
    if not msg.guild: return
    gid   = msg.guild.id
    is_on = ai_enabled.get(gid, True)
    ai_ch = ai_channel.get(gid)

    if not is_on: return

    mentioned_bot  = bot.user in msg.mentions
    in_ai_channel  = ai_ch and msg.channel.id == ai_ch
    keyword_trigger = bool(re.match(r"^(elliot[,!]?|hey elliot)\s*", msg.content, re.I))

    if not (mentioned_bot or in_ai_channel or keyword_trigger):
        return

    # Clean message
    question = msg.content
    question = re.sub(rf"<@!?{bot.user.id}>", "", question).strip()
    question = re.sub(r"^(elliot[,!]?|hey elliot)\s*", "", question, flags=re.I).strip()

    if not question:
        greetings = ["Yo! What's good? 👋", "Hey! Ask me anything 😎", "Wsp! What you need? 🤙"]
        await msg.reply(random.choice(greetings), mention_author=False)
        return

    async with msg.channel.typing():
        response = await ask_groq(msg.channel.id, question)
    await msg.reply(response, mention_author=False)

    await bot.process_commands(msg)

# ══════════════════════════════════════════════════════════
#  SLASH COMMANDS
# ══════════════════════════════════════════════════════════
@bot.tree.command(name="ask", description="Ask Elliot anything")
@app_commands.describe(question="Your question")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    response = await ask_groq(interaction.channel_id, question)
    e = base(color=C_AI)
    e.description = response
    e.set_author(name=f"Asked by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.followup.send(embed=e)

@bot.tree.command(name="chat", description="Chat with Elliot")
@app_commands.describe(message="Your message")
async def chat(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    response = await ask_groq(interaction.channel_id, message)
    e = base(color=C_AI)
    e.description = response
    e.set_author(name=f"{interaction.user.display_name} said:", icon_url=interaction.user.display_avatar.url)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.followup.send(embed=e)

@bot.tree.command(name="joke", description="Get a random joke from Elliot")
async def joke(interaction: discord.Interaction):
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything 💀",
        "I told my computer I needed a break... now it won't stop sending me Kit Kat ads 😭",
        "Why did the Discord bot go to therapy? Too many unhandled exceptions 💀",
        "I asked my dog what 2 minus 2 is. He said nothing. 😭",
        "Why do programmers prefer dark mode? Because light attracts bugs 🐛",
        "What do you call a fake noodle? An impasta 💀",
        "I used to hate facial hair but then it grew on me 💀",
        "Why can't a nose be 12 inches long? Because then it'd be a foot 😭",
        "I'm reading a book about anti-gravity. It's impossible to put down 💀",
    ]
    e = base("😂  Joke Time", random.choice(jokes), C_AI)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="fact", description="Get a random interesting fact")
async def fact(interaction: discord.Interaction):
    facts = [
        "🧠 Honey never expires. They found 3000 year old honey in Egyptian tombs and it was still good.",
        "🧠 A group of flamingos is called a 'flamboyance'.",
        "🧠 Octopuses have 3 hearts and blue blood. They're genuinely built different.",
        "🧠 The average person walks about 100,000 miles in their lifetime.",
        "🧠 Bananas are technically berries but strawberries aren't. Nature is broken.",
        "🧠 Crows can recognise human faces and hold grudges. Don't mess with crows.",
        "🧠 A day on Venus is longer than a year on Venus.",
        "🧠 Humans share 60% of their DNA with bananas. 💀",
        "🧠 The average cloud weighs about 1.1 million pounds.",
        "🧠 There are more possible iterations of a game of chess than atoms in the observable universe.",
        "🧠 Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
        "🧠 Nintendo was founded in 1889. They started making playing cards.",
        "🧠 A bolt of lightning is 5x hotter than the surface of the sun.",
    ]
    e = base("🧠  Random Fact", random.choice(facts), C_AI)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="roast", description="Get Elliot to roast someone")
@app_commands.describe(user="Who to roast")
async def roast(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    roasts = [
        "You're the reason they put instructions on shampoo bottles 💀",
        "I'd roast you but my parents told me not to burn trash 🔥",
        "You're not stupid, you just have bad luck thinking 😭",
        "You're the human version of a participation trophy 😂",
        "I've seen better looking things at the bottom of a trash can 💀",
        "You're like a software update — whenever I see you, I think 'not now' 💀",
        "Your secrets are safe with me. I never pay attention to what you say anyway 😭",
        "I'm not saying I hate you, but I would unplug your life support to charge my phone 💀",
    ]
    e = base(f"🔥  Roasting {target.display_name}", random.choice(roasts), C_ERROR)
    e.set_thumbnail(url=target.display_avatar.url)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="compliment", description="Get Elliot to compliment someone")
@app_commands.describe(user="Who to compliment")
async def compliment(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    compliments = [
        "You're genuinely built different fr 💪👑",
        "Your aura? Immaculate. Your drip? Certified. 🔥",
        "You're the type of person who makes the whole server better 🙌",
        "Real one right here. No cap. 💎",
        "You're not just a vibe, you ARE the vibe 👑✨",
        "Honestly one of the most solid people in this server 💙",
        "You bring good energy wherever you go fr 🌟",
        "The world needs more people like you no cap 💪",
    ]
    e = base(f"💙  Big Up {target.display_name}", random.choice(compliments), C_SUCCESS)
    e.set_thumbnail(url=target.display_avatar.url)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="rate", description="Elliot rates something out of 10")
@app_commands.describe(thing="What to rate")
async def rate(interaction: discord.Interaction, thing: str):
    score = random.randint(1, 10)
    bars = "█" * score + "░" * (10 - score)
    colors = {range(1,4): C_ERROR, range(4,7): C_WARNING, range(7,11): C_SUCCESS}
    color = next((v for k,v in colors.items() if score in k), C_AI)
    comments = {
        range(1,3): "Yikes... 💀",
        range(3,5): "Not great ngl 😬",
        range(5,7): "Mid honestly 😐",
        range(7,9): "Pretty solid! 👍",
        range(9,11): "An absolute W 👑🔥"
    }
    comment = next((v for k,v in comments.items() if score in k), "")
    e = base(f"📊  Rating: {thing}", color=color)
    e.description = f"**{score}/10** — {comment}\n`{bars}`"
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads! 🪙", "Tails! 🪙"])
    e = base("🪙  Coin Flip", f"**{result}**", C_AI)
    ft(e, "Elliot AI")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="dice", description="Roll a dice")
@app_commands.describe(sides="Number of sides (default 6)")
async def dice(interaction: discord.Interaction, sides: int = 6):
    if sides < 2: sides = 6
    result = random.randint(1, sides)
    e = base("🎲  Dice Roll", f"You rolled a **{result}** out of {sides}!", C_AI)
    ft(e, "Elliot AI")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="8ball", description="Ask the magic 8 ball a question")
@app_commands.describe(question="Your yes/no question")
async def eightball(interaction: discord.Interaction, question: str):
    answers = [
        "✅ It is certain.", "✅ Without a doubt.", "✅ Yes, definitely.",
        "✅ You may rely on it.", "✅ As I see it, yes.", "✅ Most likely.",
        "🤔 Reply hazy, try again.", "🤔 Ask again later.", "🤔 Cannot predict now.",
        "❌ Don't count on it.", "❌ My reply is no.", "❌ Very doubtful.",
        "❌ Outlook not so good.", "❌ My sources say no.",
    ]
    answer = random.choice(answers)
    color = C_SUCCESS if answer.startswith("✅") else C_WARNING if answer.startswith("🤔") else C_ERROR
    e = base("🎱  Magic 8 Ball", color=color)
    e.add_field(name="❓ Question", value=question, inline=False)
    e.add_field(name="🎱 Answer",   value=f"**{answer}**", inline=False)
    ft(e, "Elliot AI")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="aura", description="Check someone's aura level")
@app_commands.describe(user="Who to check (default: yourself)")
async def aura(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    level = random.randint(1000, 99999)
    tier = (
        ("💀 Negative Aura", C_ERROR)          if level < 10000 else
        ("😐 Average Aura", C_WARNING)          if level < 30000 else
        ("😎 Good Aura", C_INFO)                if level < 60000 else
        ("🔥 Strong Aura", C_SUCCESS)           if level < 85000 else
        ("👑 AURA KING", CRIMSON)
    )
    e = base(f"🔮  Aura Check — {target.display_name}", color=tier[1])
    e.set_thumbnail(url=target.display_avatar.url)
    e.add_field(name="⚡ Aura Level", value=f"**{level:,}**",  inline=True)
    e.add_field(name="🏅 Tier",       value=tier[0],           inline=True)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="rizz", description="Check someone's rizz level")
@app_commands.describe(user="Who to check (default: yourself)")
async def rizz(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    score = random.randint(0, 100)
    tier = (
        ("💀 No Rizz", C_ERROR)           if score < 20 else
        ("😬 Low Rizz", C_WARNING)         if score < 40 else
        ("😐 Mid Rizz", C_INFO)            if score < 60 else
        ("😏 Decent Rizz", C_SUCCESS)      if score < 80 else
        ("👑 MAX RIZZ", CRIMSON)
    )
    bar = "█" * (score // 10) + "░" * (10 - score // 10)
    e = base(f"😏  Rizz Check — {target.display_name}", color=tier[1])
    e.set_thumbnail(url=target.display_avatar.url)
    e.add_field(name="💯 Rizz Score", value=f"**{score}/100**\n`{bar}`", inline=True)
    e.add_field(name="🏅 Tier",       value=tier[0],                     inline=True)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    ms = round(bot.latency * 1000)
    bar = "🟢" if ms < 100 else "🟡" if ms < 200 else "🔴"
    e = base("🏓  Pong!", f"{bar} **{ms}ms**",
             C_SUCCESS if ms < 100 else C_WARNING if ms < 200 else C_ERROR)
    ft(e, "Elliot AI")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="toggle", description="Enable or disable Elliot AI in this server")
@app_commands.checks.has_permissions(administrator=True)
async def toggle(interaction: discord.Interaction):
    gid = interaction.guild.id
    ai_enabled[gid] = not ai_enabled.get(gid, True)
    now_on = ai_enabled[gid]
    e = base("🤖  Elliot AI",
             f"AI is now **{'🟢 ENABLED' if now_on else '🔴 DISABLED'}**",
             C_SUCCESS if now_on else C_ERROR)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name="setchannel", description="Set a dedicated channel where Elliot replies to every message")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel="Dedicated AI channel (leave empty to clear)")
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    ai_channel[interaction.guild.id] = channel.id if channel else None
    if channel:
        e = ok("AI Channel Set", f"Elliot will reply to **every message** in {channel.mention}.")
    else:
        e = ok("AI Channel Cleared", "Elliot now only responds when:\n• @mentioned\n• Message starts with `Elliot,` or `Hey Elliot`\n• `/ask` or `/chat` used")
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name="status", description="View Elliot AI status")
async def status(interaction: discord.Interaction):
    gid    = interaction.guild.id
    on     = ai_enabled.get(gid, True)
    ch_id  = ai_channel.get(gid)
    delta  = datetime.utcnow() - bot_start_time if bot_start_time else None
    if delta:
        d, r = divmod(int(delta.total_seconds()), 86400)
        h, r = divmod(r, 3600); m, s = divmod(r, 60)
        uptime = f"{d}d {h}h {m}m {s}s"
    else: uptime = "?"
    e = base("🤖  Elliot AI Status", color=C_SUCCESS if on else C_ERROR)
    e.set_thumbnail(url=bot.user.display_avatar.url)
    e.add_field(name="⚡ Status",    value="🟢 Active" if on else "🔴 Disabled",                 inline=True)
    e.add_field(name="📡 Latency",  value=f"`{round(bot.latency*1000)}ms`",                       inline=True)
    e.add_field(name="⏰ Uptime",   value=f"`{uptime}`",                                          inline=True)
    e.add_field(name="📍 Channel",  value=f"<#{ch_id}>" if ch_id else "Any (when mentioned)",     inline=True)
    e.add_field(name="🧠 Engine",   value="`Groq (llama3-70b-8192)`",                            inline=True)
    e.add_field(name="💬 Triggers", value="`@mention` • `Elliot,` • `/ask`",                      inline=True)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="help", description="View all Elliot AI commands")
async def help_cmd(interaction: discord.Interaction):
    e = base("🤖  Elliot AI — Commands", color=C_AI)
    e.set_thumbnail(url=bot.user.display_avatar.url)
    e.description = "Your built-in Discord AI. No API keys. Just Elliot. 🤙\nTalk to me by @mentioning me or using `Elliot, <message>`!"
    e.add_field(name="💬  Chat",
                value="`/ask` • `/chat` • `/joke` • `/fact` • `/8ball` • `/roast` • `/compliment`",
                inline=False)
    e.add_field(name="🎲  Fun",
                value="`/coinflip` • `/dice` • `/rate` • `/aura` • `/rizz`",
                inline=False)
    e.add_field(name="⚙️  Config",
                value="`/toggle` • `/setchannel` • `/status` • `/ping`",
                inline=False)
    e.add_field(name="🗣️  Natural Chat",
                value="@mention me OR start message with `Elliot,` / `Hey Elliot`",
                inline=False)
    e.add_field(name="👑  Easter Egg",
                value="@mention `akif_47411` to see the Aura King revealed 👑",
                inline=False)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

# ══════════════════════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════════════════════
bot.run(TOKEN)
