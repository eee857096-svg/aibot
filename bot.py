import discord
from discord.ext import commands
from discord import app_commands
import os, aiohttp, re
from datetime import datetime

# ══════════════════════════════════════════════════════════
#  ENV
# ══════════════════════════════════════════════════════════
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN          = os.getenv("AI_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN:
    raise RuntimeError("AI_BOT_TOKEN environment variable is not set.")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

# ══════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════
AKIF_USERNAME  = "akif_47411"
AI_MODEL       = "gemini-2.0-flash"
GEMINI_API     = f"https://generativelanguage.googleapis.com/v1beta/models/{AI_MODEL}:generateContent"
AI_MAX_HISTORY = 30       # messages kept per channel
AI_MAX_TOKENS  = 1024

CRIMSON    = 0xDC143C
C_SUCCESS  = 0x2ECC71
C_ERROR    = 0xE74C3C
C_WARNING  = 0xF39C12
C_INFO     = 0x5865F2
C_AI       = 0x9B59B6   # purple for AI

AKIF_RESPONSES = [
    "👑 **{mention} is the AURA KING** 👑\nNobody comes close. The drip, the vibe, the presence — completely unmatched.",
    "⚡ Someone just mentioned **{mention}**?? The AURA KING has been summoned. Bow down. 👑",
    "🔥 **{mention}** — certified Aura King. His aura level? **IMMEASURABLE**. Scientists are still baffled.",
    "💎 {mention} walks in and the whole vibe shifts instantly. That's what an Aura King does. 👑✨",
    "📊 **Aura Level Check:**\n> Everyone else: 📉📉📉\n> **{mention}**: 📈📈📈 OFF THE CHARTS 👑\n> *Comparison is not even possible.*",
    "🌟 Ah yes, **{mention}** — the man, the myth, the Aura King. His aura radiates across dimensions. 👑",
    "💀 The server felt a disturbance in the force... turns out someone mentioned **{mention}**, the one and only Aura King. 👑",
]

AI_SYSTEM_PROMPT = (
    "You are Crimson AI, a helpful, smart, and slightly witty Discord bot assistant. "
    "You help server members with questions, have real conversations, give advice, explain concepts, help with code, creative writing, and anything else. "
    "Keep responses concise and Discord-friendly — avoid massive walls of text. Use markdown where it helps (bold, code blocks, lists). "
    "Be casual, friendly and fun but always genuinely helpful. Never be rude, offensive, or inappropriate. "
    "If someone asks who you are, say you're Crimson AI, a custom Discord bot assistant."
)

# ══════════════════════════════════════════════════════════
#  BOT INIT
# ══════════════════════════════════════════════════════════
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="c!", intents=intents)

# ══════════════════════════════════════════════════════════
#  STORAGE
# ══════════════════════════════════════════════════════════
ai_conversations = {}   # {channel_id: [{"role": str, "content": str}]}
ai_enabled       = {}   # {guild_id: bool}
ai_channel       = {}   # {guild_id: channel_id | None}  None = respond when mentioned
bot_start_time   = None

# ══════════════════════════════════════════════════════════
#  EMBED HELPERS
# ══════════════════════════════════════════════════════════
def base(title="", desc="", color=CRIMSON):
    return discord.Embed(title=title, description=desc, color=color, timestamp=datetime.utcnow())

def ok(t, d=""):   return base(f"✅  {t}", d, C_SUCCESS)
def err(t, d=""):  return base(f"❌  {t}", d, C_ERROR)
def info(t, d=""): return base(f"ℹ️  {t}", d, C_INFO)

def ft(e, text="Crimson AI", icon=None):
    e.set_footer(text=text, icon_url=icon)
    return e

# ══════════════════════════════════════════════════════════
#  AI CORE
# ══════════════════════════════════════════════════════════
def get_history(channel_id: int) -> list:
    return ai_conversations.setdefault(channel_id, [])

def add_message(channel_id: int, role: str, content: str):
    h = get_history(channel_id)
    h.append({"role": role, "content": content})
    # Trim to max history (keep pairs)
    if len(h) > AI_MAX_HISTORY:
        ai_conversations[channel_id] = h[-AI_MAX_HISTORY:]

async def ask_gemini(channel_id: int, question: str) -> str:
    add_message(channel_id, "user", question)
    history = get_history(channel_id)

    # Convert history to Gemini format
    # Gemini uses "user" / "model" roles and "parts" arrays
    gemini_contents = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    payload = {
        "system_instruction": {
            "parts": [{"text": AI_SYSTEM_PROMPT}]
        },
        "contents": gemini_contents,
        "generationConfig": {
            "maxOutputTokens": AI_MAX_TOKENS,
            "temperature": 0.9,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]
    }

    url = f"{GEMINI_API}?key={GEMINI_API_KEY}"

    async with aiohttp.ClientSession() as s:
        async with s.post(
            url,
            headers={"content-type": "application/json"},
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as r:
            if r.status != 200:
                body = await r.text()
                raise Exception(f"Gemini API {r.status}: {body[:300]}")
            data = await r.json()

            # Extract text from Gemini response
            try:
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                raise Exception(f"Unexpected Gemini response format: {str(data)[:200]}")

    add_message(channel_id, "assistant", reply)
    return reply

async def send_ai_reply(msg_or_interaction, question: str, is_interaction=False):
    """Shared response sender — handles chunking for 2000 char limit."""
    try:
        reply = await ask_gemini(
            msg_or_interaction.channel.id if is_interaction else msg_or_interaction.channel.id,
            question
        )

        # Build embed for clean look
        chunks = [reply[i:i+3800] for i in range(0, len(reply), 3800)]
        for i, chunk in enumerate(chunks):
            e = discord.Embed(description=chunk, color=C_AI, timestamp=datetime.utcnow())
            if i == 0:
                if is_interaction:
                    e.set_author(
                        name=f"Asked by {msg_or_interaction.user.display_name}",
                        icon_url=msg_or_interaction.user.display_avatar.url
                    )
                else:
                    e.set_author(
                        name=f"Asked by {msg_or_interaction.author.display_name}",
                        icon_url=msg_or_interaction.author.display_avatar.url
                    )
            ft(e, f"Crimson AI • {AI_MODEL}", bot.user.display_avatar.url if bot.user else None)

            if is_interaction:
                if i == 0:
                    await msg_or_interaction.followup.send(embed=e)
                else:
                    await msg_or_interaction.channel.send(embed=e)
            else:
                await msg_or_interaction.reply(embed=e, mention_author=False)

    except Exception as ex:
        error_msg = err("AI Error", f"Something went wrong: `{ex}`\n\nMake sure `GEMINI_API_KEY` is set correctly.")
        if is_interaction:
            await msg_or_interaction.followup.send(embed=error_msg, ephemeral=True)
        else:
            await msg_or_interaction.reply(embed=error_msg, mention_author=False)

# ══════════════════════════════════════════════════════════
#  EVENTS
# ══════════════════════════════════════════════════════════
@bot.event
async def on_ready():
    global bot_start_time
    bot_start_time = datetime.utcnow()
    try:
        synced = await bot.tree.sync()
        print(f"✅  Crimson AI ready as {bot.user} — {len(synced)} commands synced")
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
        name = mentioned.name or ""
        global_name = getattr(mentioned, 'global_name', "") or ""
        if AKIF_USERNAME.lower() in name.lower() or AKIF_USERNAME.lower() in global_name.lower():
            import random
            response = random.choice(AKIF_RESPONSES).format(mention=mentioned.mention)
            await msg.channel.send(response)

    # ── AI Chat trigger ───────────────────────────────────────
    if not msg.guild: return

    gid    = msg.guild.id
    is_on  = ai_enabled.get(gid, True)   # default ON for new servers
    ai_ch  = ai_channel.get(gid)         # None = respond when @mentioned only

    if not is_on: return

    mentioned_bot   = bot.user in msg.mentions
    in_ai_channel   = ai_ch and msg.channel.id == ai_ch
    triggered_by_kw = bool(re.match(r"^(crimson ai|hey crimson|crimson,)\s*", msg.content, re.I))

    if not (mentioned_bot or in_ai_channel or triggered_by_kw):
        return

    # Clean the message
    question = msg.content
    question = re.sub(rf"<@!?{bot.user.id}>", "", question).strip()
    question = re.sub(r"^(crimson ai|hey crimson|crimson,)\s*", "", question, flags=re.I).strip()
    if not question:
        await msg.reply("Hey! What can I help you with? 😊", mention_author=False)
        return

    async with msg.channel.typing():
        await send_ai_reply(msg, question, is_interaction=False)

    await bot.process_commands(msg)

# ══════════════════════════════════════════════════════════
#  SLASH COMMANDS
# ══════════════════════════════════════════════════════════

# ── Core AI ──────────────────────────────────────────────
@bot.tree.command(name="ask", description="Ask Crimson AI anything")
@app_commands.describe(question="Your question or message")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    await send_ai_reply(interaction, question, is_interaction=True)

@bot.tree.command(name="chat", description="Have a conversation with Crimson AI")
@app_commands.describe(message="Your message")
async def chat(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    await send_ai_reply(interaction, message, is_interaction=True)

@bot.tree.command(name="clear", description="Clear conversation history for this channel")
async def clear_history(interaction: discord.Interaction):
    count = len(ai_conversations.get(interaction.channel.id, []))
    ai_conversations[interaction.channel.id] = []
    e = ok("Memory Cleared", f"Cleared **{count}** messages from this channel's history.\nFresh conversation started! 🧹")
    ft(e, "Crimson AI")
    await interaction.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name="history", description="View how many messages are stored in this channel's AI memory")
async def history(interaction: discord.Interaction):
    h = ai_conversations.get(interaction.channel.id, [])
    e = info("AI Memory", f"**{len(h)}** / **{AI_MAX_HISTORY}** messages stored for this channel.\n\nUse `/clear` to wipe the history.")
    ft(e, "Crimson AI")
    await interaction.response.send_message(embed=e, ephemeral=True)

# ── Config ────────────────────────────────────────────────
@bot.tree.command(name="toggle", description="Enable or disable Crimson AI in this server")
@app_commands.checks.has_permissions(administrator=True)
async def toggle(interaction: discord.Interaction):
    gid = interaction.guild.id
    ai_enabled[gid] = not ai_enabled.get(gid, True)
    now_on = ai_enabled[gid]
    e = base(
        "🤖  Crimson AI",
        f"AI is now **{'🟢 ENABLED' if now_on else '🔴 DISABLED'}** in this server.",
        C_SUCCESS if now_on else C_ERROR
    )
    ch_id = ai_channel.get(gid)
    e.add_field(name="📍 Responds In",
                value=f"<#{ch_id}> only" if ch_id else "Any channel (when @mentioned or triggered by keyword)",
                inline=False)
    ft(e, "Crimson AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name="setchannel", description="Set a dedicated AI channel (bot replies to every message there)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel="Dedicated AI channel (leave empty to clear)")
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    ai_channel[interaction.guild.id] = channel.id if channel else None
    if channel:
        e = ok("AI Channel Set",
               f"Crimson AI will now reply to **every message** in {channel.mention}.\n"
               f"It will also still respond to @mentions and keywords everywhere else.")
    else:
        e = ok("AI Channel Cleared",
               "No dedicated channel — Crimson AI now only responds when:\n"
               "• **@mentioned** directly\n"
               "• Message starts with `Crimson AI`, `Hey Crimson` or `Crimson,`\n"
               "• `/ask` or `/chat` slash commands")
    ft(e, "Crimson AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e, ephemeral=True)

# ── Utility ───────────────────────────────────────────────
@bot.tree.command(name="status", description="View Crimson AI bot status")
async def status(interaction: discord.Interaction):
    gid     = interaction.guild.id
    on      = ai_enabled.get(gid, True)
    ch_id   = ai_channel.get(gid)
    hist    = len(ai_conversations.get(interaction.channel.id, []))
    delta   = datetime.utcnow() - bot_start_time if bot_start_time else None
    if delta:
        d, r = divmod(int(delta.total_seconds()), 86400)
        h, r = divmod(r, 3600); m, s = divmod(r, 60)
        uptime = f"{d}d {h}h {m}m {s}s"
    else: uptime = "?"

    e = base("🤖  Crimson AI Status", color=C_SUCCESS if on else C_ERROR)
    e.set_thumbnail(url=bot.user.display_avatar.url)
    e.add_field(name="⚡ Status",            value="🟢 Online & Active" if on else "🔴 Disabled",       inline=True)
    e.add_field(name="📡 Latency",           value=f"`{round(bot.latency*1000)}ms`",                     inline=True)
    e.add_field(name="⏰ Uptime",            value=f"`{uptime}`",                                        inline=True)
    e.add_field(name="📍 AI Channel",        value=f"<#{ch_id}>" if ch_id else "Any (when mentioned)",   inline=True)
    e.add_field(name="💬 This Channel Mem",  value=f"`{hist}` / `{AI_MAX_HISTORY}` messages",            inline=True)
    e.add_field(name="🧠 Model",             value=f"`gemini-2.0-flash`",                               inline=True)
    e.add_field(name="💡 How to use",
                value=(
                    "@mention me  •  `Crimson AI <question>`\n"
                    "`/ask` or `/chat`  •  Set a dedicated channel"
                ), inline=False)
    ft(e, "Crimson AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="ping", description="Check the bot latency")
async def ping(interaction: discord.Interaction):
    ms = round(bot.latency * 1000)
    bar = "🟢" if ms < 100 else "🟡" if ms < 200 else "🔴"
    e = base("🏓  Pong!", f"{bar} **{ms}ms**", C_SUCCESS if ms < 100 else C_WARNING if ms < 200 else C_ERROR)
    ft(e, "Crimson AI")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="help", description="View all Crimson AI commands")
async def help_cmd(interaction: discord.Interaction):
    e = base("🤖  Crimson AI — Help", color=C_AI)
    e.set_thumbnail(url=bot.user.display_avatar.url)
    e.description = "Your intelligent Discord AI assistant, powered by Claude.\nTalk to me by @mentioning me, or use the commands below!"
    e.add_field(
        name="💬  Chat Commands",
        value=(
            "`/ask <question>` — Ask me anything\n"
            "`/chat <message>` — Have a conversation\n"
            "`/clear` — Clear this channel's memory\n"
            "`/history` — See stored message count"
        ), inline=False
    )
    e.add_field(
        name="⚙️  Config Commands",
        value=(
            "`/toggle` — Enable/disable AI (admin)\n"
            "`/setchannel` — Set dedicated AI channel (admin)\n"
            "`/status` — View bot status\n"
            "`/ping` — Check latency"
        ), inline=False
    )
    e.add_field(
        name="🗣️  Natural Triggers",
        value=(
            "• **@mention** me anywhere\n"
            "• Start with `Crimson AI <question>`\n"
            "• Start with `Hey Crimson <question>`\n"
            "• Talk in the dedicated AI channel"
        ), inline=False
    )
    e.add_field(
        name="👑  Special Features",
        value="@mention `akif_47411` to reveal the Aura King 👑",
        inline=False
    )
    ft(e, "Crimson AI", bot.user.display_avatar.url)
    await interaction.response.send_message(embed=e)

# ══════════════════════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════════════════════
bot.run(TOKEN)
