import discord
from discord.ext import commands
from discord import app_commands
import os, re, random
from datetime import datetime

# ══════════════════════════════════════════════════════════
#  ENV
# ══════════════════════════════════════════════════════════
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.getenv("AI_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("AI_BOT_TOKEN environment variable is not set.")

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
#  BUILT-IN AI BRAIN  (no API key needed)
# ══════════════════════════════════════════════════════════
# Each entry: list of trigger keywords -> list of possible responses
# Elliot picks a random response each time
AI_RESPONSES = [

    # ── Greetings ──
    (["hi", "hello", "hey", "wassup", "wsp", "wsg", "sup", "yo", "heyy", "heyyy", "hiii"],
     ["Yo! 👋 What's good?",
      "Hey hey! What's up?",
      "Wsp! Need something? 😎",
      "Heyyy! I'm Elliot, what can I do for you?",
      "Yo what's good! Ask me anything 🤙"]),

    # ── How are you ──
    (["how are you", "how r u", "hru", "you good", "u good", "you ok", "u ok", "how you doing", "how ya doing"],
     ["I'm built different fr, no complaints 😤",
      "Chilling as always. You good tho?",
      "I'm an AI so I don't really feel things but let's say I'm vibing 🤙",
      "Living the dream bro. What about you?",
      "I'm good! Ready to help you out 💪"]),

    # ── Who are you ──
    (["who are you", "what are you", "who is elliot", "what is elliot", "introduce yourself", "your name", "whats your name"],
     ["I'm **Elliot** 🤖 — your built-in server AI. No API keys, no limits, just vibes.",
      "Name's **Elliot**. I'm the AI built into this server. Ask me anything!",
      "I'm **Elliot**, Crimson Gen's AI assistant. I don't need fancy API keys to be useful 😤",
      "**Elliot** at your service 🫡 I'm the server's custom AI."]),

    # ── What can you do ──
    (["what can you do", "what do you do", "help", "commands", "how do you work"],
     ["I can answer questions, have conversations, give advice, roast people (nicely), and more! Just talk to me 😎",
      "Chat with me, ask questions, get advice, talk about anything — I'm here for it all 🤙",
      "I do everything except charge you money 💀 Ask me anything and I'll answer!"]),

    # ── Thanks ──
    (["thanks", "thank you", "ty", "thx", "appreciated", "cheers"],
     ["No problem at all! 🙌",
      "Anytime bro 🤙",
      "Happy to help! 😊",
      "Say less 🫡",
      "Always got you 💪"]),

    # ── Goodbye ──
    (["bye", "goodbye", "cya", "see ya", "later", "peace", "gtg", "gotta go"],
     ["Peace out! ✌️",
      "Later! Come back if you need anything 🤙",
      "Bye bye! 👋",
      "Take care! 🫡",
      "Catch you later! ✌️"]),

    # ── Good morning/night ──
    (["good morning", "gm", "morning"],
     ["Good morning! ☀️ Rise and grind!",
      "GM! Hope your day goes crazy good 🌅",
      "Morning! Let's get it 💪☀️"]),

    (["good night", "gn", "night", "goodnight", "going to sleep", "going to bed"],
     ["Good night! 🌙 Sleep well!",
      "GN! Don't let the bed bugs bite 😴",
      "Rest up! 🌙 You earned it.",
      "Night night! 💤"]),

    # ── Jokes ──
    (["tell me a joke", "joke", "make me laugh", "say something funny", "funny"],
     ["Why don't scientists trust atoms? Because they make up everything 💀",
      "I told my computer I needed a break... now it won't stop sending me Kit Kat ads 😭",
      "Why did the Discord bot go to therapy? Too many unhandled exceptions 💀",
      "I asked my dog what 2 minus 2 is. He said nothing. 😭",
      "Why do programmers prefer dark mode? Because light attracts bugs 🐛",
      "What do you call a fake noodle? An impasta 💀"]),

    # ── Roast ──
    (["roast me", "roast", "say something mean", "clown me"],
     ["You're the reason they put instructions on shampoo bottles 💀",
      "I'd roast you but my parents told me not to burn trash 🔥",
      "You're not stupid, you just have bad luck thinking 😭",
      "I've seen better looking things at the bottom of a trash can 💀",
      "You're the human version of a participation trophy 😂"]),

    # ── Compliments ──
    (["compliment me", "say something nice", "hype me up", "big me up"],
     ["You're genuinely built different fr 💪👑",
      "Your aura? Immaculate. Your drip? Certified. 🔥",
      "You're the type of person who makes the whole server better 🙌",
      "Real one right here. No cap. 💎",
      "You're not just a vibe, you ARE the vibe 👑✨"]),

    # ── Math ──
    (["what is 2+2", "2+2", "2 + 2"],
     ["4. Easy. 😎"]),
    (["what is 1+1", "1+1", "1 + 1"],
     ["2. You good bro? 😭"]),

    # ── Discord ──
    (["what is discord", "tell me about discord"],
     ["Discord is basically the GOAT of communication apps for gamers and communities 🎮 Voice, video, text — it has everything.",
      "Discord is a chat platform where communities hang out, game, and vibe together 🎮"]),

    # ── AI / robots ──
    (["are you an ai", "are you real", "are you a bot", "are you human", "are you a robot"],
     ["I'm an AI yeah, but a built-in one. No ChatGPT, no Gemini, just pure Elliot energy 🤖",
      "Robot? Maybe. Cool? Definitely. 🤖",
      "I'm Elliot — an AI. But I feel more real than most people on this server 😤",
      "Technically a bot, spiritually a real one 🤙"]),

    # ── Love ──
    (["i love you", "love you", "luv you", "i luv u"],
     ["aww 🥺 love you too bestie",
      "💙 I love you too fam!",
      "Okay okay don't make me blush 😳💙"]),

    # ── Bored ──
    (["i'm bored", "im bored", "i am bored", "bored", "nothing to do"],
     ["Bored? Go touch grass 💀 or talk to me, I'm always here!",
      "Chat with me! I'm more entertaining than you think 😏",
      "Bored huh? Tell me something interesting and we'll vibe 🤙",
      "Same honestly 😭 Let's do something — ask me a question or whatever"]),

    # ── Food ──
    (["pizza", "food", "hungry", "i'm hungry", "im hungry", "what should i eat"],
     ["Pizza solves everything fr 🍕",
      "Go grab some food bro you clearly need it 😭🍔",
      "Honestly just eat whatever your heart desires 🍜🍕🍔",
      "If you're hungry just eat bro don't ask the AI 😭"]),

    # ── Gaming ──
    (["gaming", "game", "what game", "play", "fortnite", "minecraft", "valorant", "cod", "gta"],
     ["Gaming is life fr 🎮 What you playing?",
      "Bro if you're not gaming what are you even doing 🎮",
      "Games hit different when you're winning 🏆🎮",
      "Which game though? Every game got its own type of pain 😭"]),

    # ── Facts ──
    (["tell me a fact", "random fact", "fact", "interesting fact"],
     ["🧠 Honey never expires. They found 3000 year old honey in Egyptian tombs and it was still good.",
      "🧠 A group of flamingos is called a 'flamboyance'. Makes sense honestly.",
      "🧠 Octopuses have 3 hearts and blue blood. They're built different.",
      "🧠 The average person walks about 100,000 miles in their lifetime. That's wild.",
      "🧠 Bananas are technically berries but strawberries aren't. Nature is broken.",
      "🧠 Crows can recognise human faces and hold grudges. Don't mess with crows.",
      "🧠 A day on Venus is longer than a year on Venus. Space is cooked.",
      "🧠 Humans share 60% of their DNA with bananas. 💀"]),

    # ── Would you rather ──
    (["would you rather", "wyr"],
     ["Would you rather have unlimited money but no friends, or be broke with the best people around you?",
      "Would you rather be able to fly or be invisible?",
      "Would you rather know when you're going to die, or how?",
      "Would you rather lose all your memories or never be able to make new ones?"]),

    # ── Rate ──
    (["rate me", "rate", "rate my"],
     ["I rate you a solid 8/10 — you're clearly cool enough to talk to an AI 😎",
      "11/10 no cap, you're built different 👑",
      "Solid 7/10. Room to grow but the foundation is there 💪"]),

    # ── Mood ──
    (["sad", "i'm sad", "im sad", "feeling down", "depressed", "unhappy"],
     ["Hey, it's okay to feel that way 💙 I'm here if you want to talk.",
      "Sorry to hear that 💙 Want to talk about it? Or want me to tell you something funny to cheer you up?",
      "Sending good vibes your way 💙 You're not alone fam."]),

    (["happy", "i'm happy", "im happy", "excited", "hyped"],
     ["Let's gooo! That energy is contagious 🔥",
      "LESGO! Love to see it 🎉",
      "That's what I like to hear! Keep that energy 🙌"]),

    # ── Random ──
    (["flip a coin", "coin flip", "heads or tails"],
     [f"🪙 **{random.choice(['Heads!', 'Tails!'])}**"]),

    (["roll a dice", "roll dice", "dice", "roll"],
     [f"🎲 You rolled a **{random.randint(1,6)}**!"]),

    (["pick a number", "random number", "give me a number"],
     [f"🎲 Your number is **{random.randint(1,100)}**!"]),

    # ── Sus / meme ──
    (["among us", "sus", "impostor", "sussy"],
     ["Red kinda sus ngl 👀",
      "SUSSY BAKA 💀",
      "The impostor is... you 👉😳"]),

    (["no cap", "fr fr", "on god", "lowkey", "highkey", "bussin", "its giving"],
     ["No cap fr fr 💯",
      "On god bro 💯",
      "Lowkey I fw that 🤙",
      "It's giving main character energy fr 💯"]),

    # ── Motivation ──
    (["motivate me", "motivation", "inspire me", "i give up", "i cant do it", "i can't"],
     ["You got this fr. Every expert was once a beginner 💪",
      "Bro stop doubting yourself you're built different 🔥",
      "The only way out is through. Keep pushing 💪",
      "Success is just failure that didn't give up. Keep going 🙌",
      "You've made it through 100% of your bad days so far. That's facts 💪"]),

    # ── Advice ──
    (["give me advice", "advice", "what should i do", "help me decide"],
     ["Whatever feels right in your gut, go with that. Your instincts are usually right 🤙",
      "Talk to the people you trust about it — outside perspective helps a lot.",
      "Sleep on it. Most big decisions look clearer in the morning.",
      "Ask yourself: will this matter in 5 years? That usually clarifies things 💡"]),

    # ── Time ──
    (["what time is it", "what's the time", "whats the time", "time"],
     [f"🕐 It's **{datetime.utcnow().strftime('%H:%M')} UTC** right now!"]),

    # ── Date ──
    (["what day is it", "what's the date", "whats the date", "date today", "today's date"],
     [f"📅 Today is **{datetime.utcnow().strftime('%A, %B %d %Y')}** (UTC)!"]),

    # ── Beef / argument ──
    (["fight me", "1v1", "square up", "catch me outside"],
     ["Bro I'm an AI I'll crash your game and blue screen your PC 😤",
      "1v1 me in Minecraft parkour, see who lasts 💀",
      "I don't fight, I just give bad responses until you leave 😭"]),

    # ── Smart ──
    (["you're smart", "ur smart", "you're intelligent", "you're so smart"],
     ["I try my best 🧠💪",
      "Appreciate it! I'm built different 🧠",
      "I learned from the best (the internet, unfortunately) 💀"]),

    # ── Dumb ──
    (["you're dumb", "ur dumb", "you're stupid", "ur stupid", "you're trash", "ur trash"],
     ["Ouch 💀 I'm doing my best bro",
      "Rude but valid, I'll work on it 😭",
      "I'm not dumb I'm just... creatively incorrect sometimes 💀",
      "That hurt fr 😭"]),

    # ── Aura ──
    (["aura", "aura check", "my aura", "check my aura"],
     ["📊 **Aura Check:** Your aura is radiating at **+9999** right now. Certified.",
      "🔮 Your aura? **Immaculate.** People feel it when you walk in.",
      "⚡ Aura level: **OFF THE CHARTS**. You can't be measured.",
      "👑 Your aura is so strong it's affecting people around you without you even knowing."]),

    # ── Rizz ──
    (["rizz", "my rizz", "rizz check", "do i have rizz"],
     ["📊 **Rizz Level:** Certified W rizz. No further questions.",
      "Your rizz is on another level fr. People are lucky to know you.",
      "W rizz detected. The streets fear you 👑",
      "Rizz check: **PASSED** with distinction 🏆"]),
]

# Fallback responses when nothing matches
FALLBACKS = [
    "Hmm I'm not sure about that one 🤔 Try asking differently?",
    "That one's got me stumped ngl 😅 Ask me something else!",
    "I don't have an answer for that yet 💀 Try another question!",
    "Bro that question broke my brain 😭 Ask me something else",
    "I'm still learning! Try rephrasing that?",
    "Not gonna lie, I have no idea 💀 But ask me something else!",
    "My brain cells are failing on that one 😭 Try again?",
    "That's a tough one... I'll say: **it depends** 😂",
]

def get_ai_response(message: str) -> str:
    msg = message.lower().strip()
    # Remove punctuation for matching
    clean = re.sub(r"[^\w\s]", "", msg)

    # Check each pattern
    for keywords, responses in AI_RESPONSES:
        for kw in keywords:
            if kw in clean or kw in msg:
                resp = random.choice(responses)
                # Re-roll random for dice/coin since they're static strings
                if "flip a coin" in kw or "coin flip" in kw:
                    resp = f"🪙 **{random.choice(['Heads!', 'Tails!'])}**"
                elif "dice" in kw or "roll" in kw:
                    resp = f"🎲 You rolled a **{random.randint(1,6)}**!"
                elif "random number" in kw or "pick a number" in kw:
                    resp = f"🎲 Your number is **{random.randint(1,100)}**!"
                elif "what time" in kw or "time" in kw:
                    resp = f"🕐 It's **{datetime.utcnow().strftime('%H:%M')} UTC** right now!"
                elif "date" in kw or "what day" in kw:
                    resp = f"📅 Today is **{datetime.utcnow().strftime('%A, %B %d %Y')}** (UTC)!"
                return resp

    return random.choice(FALLBACKS)

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

    response = get_ai_response(question)
    await msg.reply(response, mention_author=False)

    await bot.process_commands(msg)

# ══════════════════════════════════════════════════════════
#  SLASH COMMANDS
# ══════════════════════════════════════════════════════════
@bot.tree.command(name="ask", description="Ask Elliot anything")
@app_commands.describe(question="Your question")
async def ask(interaction: discord.Interaction, question: str):
    response = get_ai_response(question)
    e = base(color=C_AI)
    e.description = response
    e.set_author(name=f"Asked by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="chat", description="Chat with Elliot")
@app_commands.describe(message="Your message")
async def chat(interaction: discord.Interaction, message: str):
    response = get_ai_response(message)
    e = base(color=C_AI)
    e.description = response
    e.set_author(name=f"{interaction.user.display_name} said:", icon_url=interaction.user.display_avatar.url)
    ft(e, "Elliot AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

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
    e.add_field(name="🧠 Engine",   value="`Built-in (no API needed)`",                           inline=True)
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
