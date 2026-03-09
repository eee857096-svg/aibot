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

# ── Topic knowledge base (keyword fragments → response lists) ──
# get_ai_response() scans the cleaned message for ANY of these substrings
TOPIC_MAP = [

    # ── Greetings ──────────────────────────────────────────
    (["hi ", "hello", "hey ", "wassup", "wsp", "wsg", "sup ", "yo ", "heyy", "hiii", "what's up", "whats up", "howdy"],
     ["Yo! 👋 What's good?", "Hey hey! What's up?", "Wsp! Need something? 😎",
      "Heyyy! I'm Elliot, ask me anything!", "Yo what's good! 🤙"]),

    # ── How are you ────────────────────────────────────────
    (["how are you", "how r u", "hru", "you good", "u good", "you ok", "u ok", "how you doing", "how ya doin"],
     ["I'm built different fr, no complaints 😤", "Chilling as always. You good tho?",
      "I'm vibing 🤙 What about you?", "Living the dream bro 💪"]),

    # ── Who/what are you ───────────────────────────────────
    (["who are you", "what are you", "who is elliot", "what is elliot", "introduce yourself", "your name", "whats your name", "what's your name"],
     ["I'm **Elliot** 🤖 — your built-in server AI. No API keys, no limits, just vibes.",
      "Name's **Elliot**. I'm the AI built into this server. Ask me anything!",
      "**Elliot** at your service 🫡 Crimson Gen's custom AI."]),

    # ── Capabilities ───────────────────────────────────────
    (["what can you do", "what do you do", "how do you work", "what are your features"],
     ["I can answer questions, explain topics, give advice, roast, hype, tell jokes and facts — just talk to me 😎",
      "Literally anything bro. Science, history, gaming, life advice, memes — ask away 🤙"]),

    # ── Thanks ─────────────────────────────────────────────
    (["thanks", "thank you", "ty ", "thx", "appreciated", "cheers", "thnx", "thx"],
     ["No problem! 🙌", "Anytime bro 🤙", "Happy to help! 😊", "Say less 🫡", "Always got you 💪"]),

    # ── Goodbye ────────────────────────────────────────────
    (["bye", "goodbye", "cya", "see ya", "later ", "peace out", "gtg", "gotta go", "take care"],
     ["Peace out! ✌️", "Later! 🤙", "Bye bye! 👋", "Take care! 🫡", "Catch you later ✌️"]),

    # ── Good morning ───────────────────────────────────────
    (["good morning", "gm ", "morning "],
     ["Good morning! ☀️ Rise and grind!", "GM! Hope your day goes crazy good 🌅", "Morning! Let's get it 💪"]),

    # ── Good night ─────────────────────────────────────────
    (["good night", "gn ", "goodnight", "going to sleep", "going to bed", "night night"],
     ["Good night! 🌙 Sleep well!", "GN! Don't let the bed bugs bite 😴", "Rest up! 🌙", "Night night! 💤"]),

    # ── Jokes ──────────────────────────────────────────────
    (["tell me a joke", "say a joke", "make me laugh", "say something funny", "joke time"],
     ["Why don't scientists trust atoms? Because they make up everything 💀",
      "I told my computer I needed a break... now it won't stop sending me Kit Kat ads 😭",
      "Why did the Discord bot go to therapy? Too many unhandled exceptions 💀",
      "I asked my dog what 2 minus 2 is. He said nothing 😭",
      "Why do programmers prefer dark mode? Because light attracts bugs 🐛",
      "What do you call a fake noodle? An impasta 💀",
      "I'm reading a book about anti-gravity. It's impossible to put down 😂",
      "Why did the scarecrow win an award? Because he was outstanding in his field 💀",
      "Two wifi antennas got married — the ceremony was okay but the reception was incredible 😭"]),

    # ── Roast ──────────────────────────────────────────────
    (["roast me", "roast someone", "say something mean", "clown me", "talk your trash"],
     ["You're the reason they put instructions on shampoo bottles 💀",
      "I'd roast you but my parents told me not to burn trash 🔥",
      "You're not stupid, you just have bad luck thinking 😭",
      "You're the human version of a participation trophy 😂",
      "Your WiFi password is probably 'password123' isn't it 💀",
      "You look like you pause Netflix to think 😭"]),

    # ── Compliments ────────────────────────────────────────
    (["compliment me", "say something nice", "hype me up", "big me up", "hype me"],
     ["You're genuinely built different fr 💪👑",
      "Your aura? Immaculate. Your drip? Certified 🔥",
      "You're the type of person who makes the whole server better 🙌",
      "Real one right here. No cap 💎",
      "You're not just a vibe, you ARE the vibe 👑✨",
      "Bro you're lowkey the goat of this server fr 🐐"]),

    # ── AI identity ────────────────────────────────────────
    (["are you an ai", "are you real", "are you a bot", "are you human", "are you a robot", "are you alive", "do you have feelings", "do you feel"],
     ["I'm an AI — no ChatGPT, no Gemini, pure built-in Elliot energy 🤖",
      "Technically a bot, spiritually a real one 🤙",
      "I'm Elliot. An AI. But I feel more real than half the people on this server 😤",
      "Robot? Maybe. Valid? Definitely. 🤖"]),

    # ── Love / feelings ────────────────────────────────────
    (["i love you", "love you", "luv you", "i luv u", "you're the best", "ur the best"],
     ["aww 🥺 love you too bestie", "💙 I love you too fam!", "Okay okay don't make me blush 😳💙"]),

    # ── Bored ──────────────────────────────────────────────
    (["im bored", "i'm bored", "i am bored", "nothing to do", "so bored"],
     ["Bored? Go touch grass 💀 or talk to me!", "Chat with me! I'm more entertaining than you think 😏",
      "Bored huh? Tell me something interesting and we'll vibe 🤙",
      "Same honestly 😭 Ask me a question or something"]),

    # ── Sad / mental health ────────────────────────────────
    (["im sad", "i'm sad", "feeling down", "feeling depressed", "i'm depressed", "im depressed", "feel empty", "feel lonely", "i'm lonely", "im lonely", "hurting", "i'm hurting"],
     ["Hey, it's okay to feel that way 💙 I'm here if you wanna talk.",
      "Sorry to hear that 💙 You're not alone fam. What's going on?",
      "Sending good vibes your way 💙 Things will get better, I promise.",
      "Sometimes life just hits different. You got people around you tho 💙"]),

    # ── Happy / hype ───────────────────────────────────────
    (["im happy", "i'm happy", "i'm excited", "im excited", "so hyped", "i'm hyped", "lesgo", "let's go", "lets go"],
     ["Let's GOOO! That energy is contagious 🔥", "LESGO! Love to see it 🎉",
      "That's what I like to hear! Keep that energy 🙌", "W energy fr 👑"]),

    # ── Angry ──────────────────────────────────────────────
    (["im angry", "i'm angry", "so mad", "i'm mad", "im mad", "pissed off", "furious"],
     ["Breathe bro 💨 Whatever it is, it's not worth blowing up over.",
      "Take a deep breath. What happened? 🤙",
      "Oof. Let it out then tell me what happened 👂"]),

    # ── Motivation ─────────────────────────────────────────
    (["motivate me", "need motivation", "inspire me", "i give up", "i cant do it", "i can't do it", "feeling like giving up", "want to quit"],
     ["You got this fr. Every expert was once a beginner 💪",
      "Bro stop doubting yourself you're built different 🔥",
      "The only way out is through. Keep pushing 💪",
      "Success is just failure that didn't quit. Keep going 🙌",
      "You've made it through 100% of your bad days so far. That's facts 💪",
      "One step at a time. You don't have to have it all figured out today 🤙"]),

    # ── Advice ─────────────────────────────────────────────
    (["give me advice", "need advice", "what should i do", "help me decide", "what do you think i should", "should i"],
     ["Go with your gut — your instincts are usually right 🤙",
      "Talk to someone you trust about it. Outside perspective helps a lot.",
      "Sleep on it. Most big decisions look clearer in the morning.",
      "Ask yourself: will this matter in 5 years? That usually clarifies things 💡",
      "Do what makes you feel the least amount of regret later. That's usually the right move."]),

    # ── Food ───────────────────────────────────────────────
    (["im hungry", "i'm hungry", "what should i eat", "recommend food", "best food", "food recommendation"],
     ["Pizza solves everything fr 🍕", "Go grab some food bro you clearly need it 😭🍔",
      "Honestly just eat whatever your heart desires 🍜🍕🍔",
      "Bro just eat, why are you asking the AI 😭"]),

    (["what is pizza", "tell me about pizza"],
     ["Pizza is arguably the greatest human invention 🍕 Dough + sauce + cheese + toppings = perfection."]),

    (["what is sushi", "tell me about sushi"],
     ["Sushi is a Japanese dish with vinegared rice, seafood, vegetables — absolutely elite food 🍣"]),

    (["what is ramen", "tell me about ramen"],
     ["Ramen is a Japanese noodle soup — broth, noodles, toppings. One of the GOATs of comfort food 🍜"]),

    # ── Drinks ─────────────────────────────────────────────
    (["what should i drink", "recommend a drink", "im thirsty", "i'm thirsty"],
     ["Water. Drink water bro. You're probably dehydrated rn 💧",
      "Water first, always 💧 Then maybe a juice or whatever you vibe with."]),

    # ── Gaming ─────────────────────────────────────────────
    (["what game should i play", "recommend a game", "best game", "games to play"],
     ["Depends on your vibe: Minecraft for chill, Valorant for stress 😭, GTA for chaos, Dark Souls for pain 🎮",
      "Try Minecraft if you haven't — it genuinely never gets old 🎮",
      "Honestly Valorant or CS2 if you want something competitive 🎯"]),

    (["fortnite"],
     ["Fortnite is still alive somehow 💀 You building or just vibing?",
      "Fortnite players really said 'I will never give up' and meant it 😭🎮"]),

    (["minecraft"],
     ["Minecraft is literally timeless bro 🏗️ What mode you playing — survival, creative, servers?",
      "Minecraft never dies fr. One of the GOATs 🎮"]),

    (["valorant"],
     ["Valorant is either peak fun or peak suffering, no in between 😭🎯",
      "What rank are you in Valorant? Let me guess... Silver? 💀"]),

    (["gta", "gta 5", "grand theft auto"],
     ["GTA is literally a vibe 🚗💨 Online or story mode?",
      "GTA Online with friends is genuinely one of the best gaming experiences ever 🎮"]),

    (["cod", "call of duty", "warzone"],
     ["CoD is W when it works, absolute pain when it doesn't 😭🎮",
      "Warzone or multiplayer? Either way respect the grind 💪"]),

    (["apex legends", "apex"],
     ["Apex is insane when you get a good squad 🔥 Solo queue though? Pain.",
      "Apex Legends movement is genuinely one of the best in any game 🎮"]),

    (["league of legends", "lol", "league"],
     ["League of Legends is just a relationship tester disguised as a game 😭",
      "I respect anyone who still plays League. The patience required is unreal 💀"]),

    (["roblox"],
     ["Roblox is unironically fun bro don't judge 😭🎮",
      "Roblox players are built different. That game has genuinely everything."]),

    (["pokemon", "pokémon"],
     ["Pokémon is literally a whole childhood fr 🎮 What gen is your fave?",
      "Pokémon never gets old. The competitive scene is actually wild too."]),

    (["fifa", "fc25", "ea sports"],
     ["FIFA (now EA FC) is the same game every year but we keep buying it 😭⚽",
      "EA FC is peak frustration disguised as football 😂⚽"]),

    # ── Music ──────────────────────────────────────────────
    (["what music should i listen to", "recommend music", "good music", "what song"],
     ["Depends on your mood — drill for hype, lo-fi for chill, rap for energy 🎵",
      "What vibe are you going for? I got a rec for every mood 🎧"]),

    (["what is rap", "tell me about rap", "rap music"],
     ["Rap is a genre built on rhythm, wordplay and storytelling over beats 🎤 Started in the Bronx, NYC in the 70s."]),

    (["what is drill", "drill music", "uk drill"],
     ["Drill is a dark, heavy subgenre of rap — UK drill especially is elite 🎤 Artists like Central Cee, Headie One put it on the map."]),

    (["what is jazz", "tell me about jazz"],
     ["Jazz is an American music genre born in New Orleans — improvisation, complex chords, timeless vibes 🎷"]),

    (["what is classical music", "classical music"],
     ["Classical music covers centuries of orchestral, piano, opera compositions — Mozart, Beethoven, Bach are the GOATs 🎼"]),

    # ── Movies / TV ────────────────────────────────────────
    (["recommend a movie", "what movie should i watch", "good movie", "best movie"],
     ["Inception if you want your brain melted 🎬, Interstellar if you want to cry about space, John Wick if you want action.",
      "Depends on your mood: horror, comedy, action, drama? Tell me and I'll rec something 🎬"]),

    (["what is netflix", "netflix"],
     ["Netflix is a streaming platform with movies, series, documentaries — basically the king of binge watching 📺"]),

    (["recommend a show", "what show should i watch", "good show", "best show", "what series"],
     ["Breaking Bad if you haven't watched it — non-negotiable 📺",
      "Attack on Titan if you're into anime, Peaky Blinders for crime drama, Squid Game for the chaos 🎬"]),

    (["what is anime", "tell me about anime"],
     ["Anime is Japanese animation — covers every genre from action to romance to horror. Massive art form fr 🎌"]),

    (["attack on titan", "aot"],
     ["Attack on Titan is genuinely one of the greatest stories ever told in any medium. The ending is controversial but the ride is unreal 🔥"]),

    (["naruto"],
     ["Naruto is a classic bro — the ninja world, the lore, the fights. Believe it 🍥",
      "Naruto hits different when you grow up and understand the themes fr."]),

    (["one piece"],
     ["One Piece is the longest running W in manga/anime history fr 🏴‍☠️ The world building is unmatched."]),

    (["dragon ball", "dbz"],
     ["Dragon Ball Z literally defined a generation of anime fans 🐉 The power scaling got cooked tho 💀"]),

    # ── Sports ─────────────────────────────────────────────
    (["what sport should i play", "best sport", "recommend a sport"],
     ["Basketball, football, swimming — depends what you enjoy. But any sport is good for your mental health 💪"]),

    (["football", "soccer"],
     ["Football (soccer) is the world's sport for a reason — billions of fans, pure passion ⚽",
      "Football is literally the most watched sport on earth ⚽ Who do you support?"]),

    (["basketball", "nba"],
     ["Basketball is elite — the skill level in the NBA is genuinely insane 🏀 You a fan?",
      "NBA is must-watch entertainment fr 🏀 Who's your team?"]),

    (["cricket"],
     ["Cricket is a sport of patience and skill 🏏 Test cricket is an art form honestly.",
      "Cricket has a massive global following — especially in South Asia and England 🏏"]),

    (["tennis"],
     ["Tennis is one of the most demanding sports mentally and physically 🎾 Djokovic, Alcaraz era is 🔥"]),

    (["mma", "ufc", "boxing"],
     ["MMA/UFC is peak combat sports entertainment 🥊 The skill and heart these fighters show is unreal.",
      "Boxing and MMA are both elite — nothing like a big fight night 🥊"]),

    # ── Science ────────────────────────────────────────────
    (["what is gravity", "tell me about gravity", "explain gravity"],
     ["Gravity is a fundamental force that attracts objects with mass toward each other 🌍 The more mass, the stronger the pull. Einstein described it as a curvature in spacetime."]),

    (["what is evolution", "explain evolution", "tell me about evolution"],
     ["Evolution is the process by which species change over time through natural selection 🧬 Organisms with traits that help them survive reproduce more, passing those traits on."]),

    (["what is dna", "explain dna", "tell me about dna"],
     ["DNA (deoxyribonucleic acid) is the molecule that carries genetic information in all living things 🧬 It's basically the instruction manual for building and running your body."]),

    (["what is photosynthesis", "explain photosynthesis"],
     ["Photosynthesis is how plants convert sunlight, water and CO2 into glucose and oxygen ☀️🌿 Basically plants are eating sunlight — wild right?"]),

    (["what is the speed of light", "speed of light", "how fast is light"],
     ["Light travels at about **299,792,458 metres per second** (roughly 300,000 km/s) in a vacuum ⚡ Nothing in the universe moves faster."]),

    (["what is a black hole", "tell me about black holes", "explain black holes", "black hole"],
     ["A black hole is a region of space where gravity is so strong that nothing — not even light — can escape 🌌 They form when massive stars collapse. The event horizon is the point of no return."]),

    (["what is the big bang", "big bang theory", "explain the big bang"],
     ["The Big Bang is the leading theory for the origin of the universe 🌌 About 13.8 billion years ago, all matter, energy, space and time exploded from an incredibly hot, dense point and has been expanding ever since."]),

    (["what is a planet", "how many planets", "planets in solar system", "solar system"],
     ["Our solar system has **8 planets**: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune 🪐 Pluto got demoted to dwarf planet in 2006 — still hurts."]),

    (["what is the sun", "tell me about the sun"],
     ["The Sun is a massive star at the center of our solar system ☀️ It's so big that about 1.3 million Earths could fit inside it. It's basically a giant nuclear fusion reactor."]),

    (["what is the moon", "tell me about the moon", "how far is the moon"],
     ["The Moon is Earth's only natural satellite 🌕 It's about 384,400 km away from Earth and is the reason we have tides. It takes about 27 days to orbit Earth."]),

    (["what is mars", "tell me about mars", "is mars habitable"],
     ["Mars is the 4th planet from the Sun 🔴 It has the largest volcano in the solar system (Olympus Mons) and a day is about 24.5 hours. SpaceX wants to colonise it."]),

    (["what is climate change", "global warming", "explain climate change"],
     ["Climate change refers to long-term shifts in global temperatures and weather patterns 🌍 Human activities — burning fossil fuels, deforestation — have accelerated it dramatically since the industrial revolution."]),

    (["what is the ocean", "tell me about the ocean", "how deep is the ocean"],
     ["The ocean covers about **71% of Earth's surface** 🌊 The deepest point is the Mariana Trench at about 11,000 metres. Over 80% of the ocean has never been explored — genuinely terrifying and fascinating."]),

    (["what is an atom", "explain atoms", "tell me about atoms"],
     ["Atoms are the basic building blocks of all matter ⚛️ They have a nucleus (protons + neutrons) surrounded by electrons. Everything you can see and touch is made of atoms."]),

    (["what is quantum physics", "quantum mechanics", "explain quantum"],
     ["Quantum mechanics is the branch of physics that describes how matter and energy behave at the subatomic scale ⚛️ Particles can exist in multiple states at once (superposition) and behave like both waves and particles. It's genuinely mind-bending."]),

    # ── Technology ─────────────────────────────────────────
    (["what is artificial intelligence", "what is ai", "explain ai", "tell me about ai"],
     ["AI (Artificial Intelligence) is the simulation of human intelligence by machines 🤖 It includes machine learning, natural language processing, computer vision and more. I'm a (very basic) example of it!"]),

    (["what is machine learning", "explain machine learning", "tell me about machine learning"],
     ["Machine learning is a type of AI where systems learn from data to improve over time without being explicitly programmed 🧠 It's how recommendation algorithms, image recognition and chatbots work."]),

    (["what is the internet", "explain the internet", "how does the internet work"],
     ["The internet is a global network of computers that communicate via standardised protocols (TCP/IP) 🌐 When you load a webpage, data travels across physical cables, routers and servers around the world in milliseconds."]),

    (["what is coding", "what is programming", "learn to code", "how to code"],
     ["Coding is writing instructions in a programming language that computers can execute 💻 Python is the best starting point — easy to learn, massively powerful.",
      "Programming is basically telling a computer exactly what to do, step by step 💻 Start with Python — seriously one of the best decisions you can make."]),

    (["what is python", "tell me about python", "learn python"],
     ["Python is one of the most popular programming languages 🐍 Easy syntax, huge community, used in AI, web dev, data science, automation — genuinely the GOAT starter language."]),

    (["what is javascript", "tell me about javascript", "learn javascript"],
     ["JavaScript is the language of the web 🌐 It runs in browsers and on servers (Node.js). If you want to build websites or web apps, JS is essential."]),

    (["what is html", "tell me about html"],
     ["HTML (HyperText Markup Language) is the skeleton of every webpage 🌐 It defines the structure — headings, paragraphs, links, images. It's not technically a programming language, more of a markup language."]),

    (["what is css", "tell me about css"],
     ["CSS (Cascading Style Sheets) is what makes websites look good 🎨 It controls colors, fonts, layouts, animations — everything visual on a webpage."]),

    (["what is a computer", "how does a computer work"],
     ["A computer processes data using a CPU (brain), stores it in RAM (short-term memory) and a hard drive (long-term memory), and displays output via GPU/monitor 💻 Everything runs on binary — 0s and 1s."]),

    (["what is cryptocurrency", "what is crypto", "tell me about crypto", "bitcoin"],
     ["Cryptocurrency is a digital/virtual currency secured by cryptography 💰 Bitcoin was the first (2009). It uses blockchain — a decentralised ledger. It's volatile, speculative, and fascinating tech simultaneously."]),

    (["what is blockchain", "explain blockchain"],
     ["Blockchain is a distributed database where data is stored in 'blocks' chained together 🔗 It's decentralised (no single owner), tamper-resistant, and is the tech behind most cryptocurrencies."]),

    (["what is nft", "tell me about nft"],
     ["NFTs (Non-Fungible Tokens) are unique digital assets on a blockchain 🖼️ They represent ownership of digital items. The hype died down a lot but the underlying tech still has uses."]),

    (["what is a virus", "computer virus", "malware"],
     ["A computer virus is malicious code that replicates and spreads to damage systems or steal data 🦠 Modern antivirus software and safe browsing habits are your best defence."]),

    (["what is vpn", "how does a vpn work"],
     ["A VPN (Virtual Private Network) encrypts your internet traffic and routes it through a server in another location 🔒 It masks your IP address and protects your privacy, especially on public WiFi."]),

    # ── History ────────────────────────────────────────────
    (["what is world war", "world war 1", "world war 2", "ww1", "ww2", "wwi", "wwii"],
     ["WW1 (1914-1918) was triggered by the assassination of Archduke Franz Ferdinand and killed ~20 million people 💀 WW2 (1939-1945) was even more devastating — about 70-85 million deaths, including the Holocaust.",
      "WW2 was the deadliest conflict in human history — 70-85 million deaths 💀 It ended with nuclear bombs on Hiroshima and Nagasaki and Germany's unconditional surrender."]),

    (["who is napoleon", "napoleon bonaparte", "tell me about napoleon"],
     ["Napoleon Bonaparte was a French military genius and emperor (1769-1821) ⚔️ He conquered most of Europe, modernised French law (Napoleonic Code), but was ultimately defeated at Waterloo in 1815."]),

    (["who is julius caesar", "julius caesar", "tell me about caesar"],
     ["Julius Caesar was a Roman general and statesman (100-44 BC) ⚔️ He conquered Gaul, crossed the Rubicon, became dictator of Rome, and was assassinated by senators including Brutus on the Ides of March."]),

    (["who is cleopatra", "tell me about cleopatra"],
     ["Cleopatra VII was the last active pharaoh of ancient Egypt 👑 She was politically brilliant, spoke 9 languages, and had relationships with both Julius Caesar and Mark Antony."]),

    (["ancient egypt", "tell me about egypt", "pyramids"],
     ["Ancient Egypt is one of the greatest civilisations in history 🏛️ The pyramids of Giza were built as tombs for pharaohs — and they're still standing after 4,500 years. The engineering is mind-blowing."]),

    (["what is the roman empire", "roman empire", "ancient rome"],
     ["The Roman Empire was one of the most powerful civilisations ever 🏛️ At its peak it controlled most of Europe, North Africa and parts of Asia. It lasted from 27 BC to 476 AD (Western) — over 500 years."]),

    (["who is einstein", "albert einstein", "tell me about einstein"],
     ["Albert Einstein (1879-1955) was the physicist who developed the theory of relativity — E=mc² 🧠 He won the Nobel Prize in 1921 and fundamentally changed our understanding of space, time, and energy."]),

    (["who is isaac newton", "newton", "tell me about newton"],
     ["Isaac Newton (1643-1727) discovered gravity (yes the apple story is basically true), developed calculus, and his 3 laws of motion literally describe how everything moves 🍎🧠 Arguably the greatest scientist who ever lived."]),

    (["who is tesla", "nikola tesla", "tell me about tesla"],
     ["Nikola Tesla (1856-1943) was a Serbian-American inventor and electrical engineer ⚡ He developed AC electricity, the Tesla coil, radio (contested), and contributed to X-rays. Genuinely ahead of his time."]),

    (["cold war", "what was the cold war", "tell me about the cold war"],
     ["The Cold War (1947-1991) was the geopolitical tension between the USA and USSR after WW2 🌍 It was a nuclear arms race, space race and proxy wars — without direct conflict between the superpowers."]),

    (["who was martin luther king", "mlk", "martin luther king"],
     ["Martin Luther King Jr. (1929-1968) was a Baptist minister and leader of the American civil rights movement ✊ His 'I Have a Dream' speech and nonviolent activism were pivotal in ending racial segregation in the US."]),

    (["who is nelson mandela", "nelson mandela", "tell me about mandela"],
     ["Nelson Mandela (1918-2013) was a South African anti-apartheid revolutionary who was imprisoned for 27 years and went on to become the first democratically elected president of South Africa 🙏 An absolute legend."]),

    # ── Geography ──────────────────────────────────────────
    (["what is the biggest country", "largest country", "biggest country in the world"],
     ["Russia is the largest country in the world by area 🌍 It covers about 17.1 million km² — nearly twice the size of the second largest (Canada)."]),

    (["what is the smallest country", "smallest country in the world"],
     ["Vatican City is the smallest country in the world 🌍 It's about 0.44 km² — basically a city block inside Rome."]),

    (["what is the tallest mountain", "highest mountain", "mount everest"],
     ["Mount Everest is the tallest mountain on Earth at **8,848.86 metres** above sea level 🏔️ Located in the Himalayas on the Nepal-Tibet border. Over 300 people have died trying to climb it."]),

    (["what is the amazon", "amazon rainforest", "tell me about the amazon"],
     ["The Amazon Rainforest covers about 5.5 million km² across 9 South American countries 🌿 It produces about 20% of the world's oxygen and is home to 10% of all species on Earth. It's currently being deforested at an alarming rate."]),

    (["what is the sahara", "sahara desert"],
     ["The Sahara is the world's largest hot desert at about 9 million km² 🏜️ It covers most of North Africa. Despite being mostly rock and sand, it has oases, mountains, and even occasional snow."]),

    (["capital of france", "what is the capital of france"],
     ["The capital of France is **Paris** 🇫🇷 Also known as the City of Light."]),

    (["capital of usa", "capital of america", "what is the capital of the usa"],
     ["The capital of the USA is **Washington D.C.** 🇺🇸 Not New York — a common misconception."]),

    (["capital of uk", "capital of england", "capital of britain"],
     ["The capital of the UK is **London** 🇬🇧 Home to Big Ben, Buckingham Palace, and the best football league in the world (debatable 😂)."]),

    (["capital of japan", "what is the capital of japan"],
     ["The capital of Japan is **Tokyo** 🇯🇵 The most populous metropolitan area in the world with about 37 million people."]),

    (["capital of australia", "what is the capital of australia"],
     ["The capital of Australia is **Canberra** 🇦🇺 (Not Sydney — everyone thinks it's Sydney 💀)"]),

    # ── Math ───────────────────────────────────────────────
    (["what is pi", "what is π", "tell me about pi"],
     ["Pi (π) is the ratio of a circle's circumference to its diameter 🔵 It's approximately **3.14159265...** and it goes on forever with no repeating pattern — it's irrational."]),

    (["what is the pythagorean theorem", "pythagoras", "pythagorean theorem"],
     ["The Pythagorean theorem states that in a right triangle: **a² + b² = c²** 📐 where c is the hypotenuse (longest side). It's one of the most fundamental theorems in mathematics."]),

    (["what is calculus", "explain calculus", "tell me about calculus"],
     ["Calculus is the branch of mathematics dealing with rates of change (differentiation) and accumulation of quantities (integration) 📊 Developed by Newton and Leibniz independently. It's the foundation of physics and engineering."]),

    (["1+1", "1 + 1", "what is 1+1"],
     ["2. You good bro? 😭"]),

    (["2+2", "2 + 2", "what is 2+2"],
     ["4. Easy 😎"]),

    (["what is infinity", "explain infinity"],
     ["Infinity (∞) is not a number — it's a concept representing something without any bound or limit ♾️ In maths, there are actually different sizes of infinity (Cantor proved this) which is genuinely one of the most mind-bending things ever."]),

    # ── Language / Words ───────────────────────────────────
    (["what does", "what is the meaning of", "define ", "what does it mean"],
     ["Good question! I don't have a dictionary built in for every word, but Google or Merriam-Webster will sort you out instantly 📖",
      "For definitions I'd hit up dictionary.com or just Google it — instant results 📖"]),

    (["how many languages", "how many languages are there"],
     ["There are approximately **7,100 languages** spoken in the world today 🌍 About 40% of them are endangered with fewer than 1,000 speakers."]),

    (["most spoken language", "what is the most spoken language"],
     ["**Mandarin Chinese** has the most native speakers (~920 million) 🌏 But **English** is the most widely spoken language overall when you include second-language speakers."]),

    # ── Health / Body ──────────────────────────────────────
    (["how to lose weight", "weight loss", "lose weight fast"],
     ["Sustainable weight loss = caloric deficit + exercise + sleep + consistency 💪 No shortcuts. Eat well, move more, sleep enough. That's literally it.",
      "Diet is about 80% of weight loss. Focus on eating less processed food, more protein and vegetables 🥗"]),

    (["how to get abs", "how to build muscle", "how to get fit", "get in shape"],
     ["Consistency beats intensity every time 💪 Compound exercises (squats, deadlifts, bench, pull-ups) + progressive overload + enough protein = results.",
      "Hit the gym 3-4x a week, eat enough protein (0.8-1g per lb bodyweight), sleep 7-8 hours 💪 That's the formula."]),

    (["how to sleep better", "cant sleep", "can't sleep", "insomnia", "trouble sleeping"],
     ["Same sleep/wake time every day, dark cold room, no screens 1hr before bed, no caffeine after 2pm ☀️ Consistency is the key.",
      "Cut screens before bed, keep your room cool and dark, avoid caffeine late — these genuinely work 😴"]),

    (["how much water should i drink", "how much water", "daily water intake"],
     ["General guideline is about **2-3 litres** of water per day 💧 More if you're exercising or it's hot. Your urine colour is the best indicator — aim for light yellow."]),

    (["what is mental health", "tell me about mental health", "mental health"],
     ["Mental health covers emotional, psychological and social wellbeing 🧠 It affects how you think, feel and act. It's just as important as physical health — take care of your mind like you take care of your body."]),

    (["how to deal with anxiety", "i have anxiety", "anxiety help", "im anxious", "i'm anxious"],
     ["Deep breathing really works — 4 seconds in, hold 4, out 4 🌬️ Also: exercise, limiting caffeine, journalling, and talking to someone you trust all help. Therapy is valid and worth it if anxiety is affecting your life."]),

    # ── Money / Finance ────────────────────────────────────
    (["how to make money", "ways to make money", "earn money online", "make money fast"],
     ["Real talk: freelancing your skills (design, coding, writing), starting a small business, or investing consistently over time are the legit paths 💰 'Fast money' schemes usually end badly.",
      "Best way to make money: get good at a valuable skill, then sell that skill 💡 Design, coding, copywriting, video editing — all pay well."]),

    (["how to save money", "saving money tips", "how to budget"],
     ["50/30/20 rule: 50% needs, 30% wants, 20% savings/investments 💰 Track your spending for a month — you'll be surprised where it goes.",
      "Automate your savings — set up an automatic transfer on payday before you can spend it 💰 You don't miss what you never see."]),

    (["what is investing", "how to invest", "should i invest"],
     ["Investing is putting money to work so it grows over time 📈 Start with index funds (like S&P 500 ETFs) — low fees, diversified, historically strong returns. Time in the market beats timing the market.",
      "Compound interest is the 8th wonder of the world fr 📈 Start investing early even with small amounts — time is the most powerful factor."]),

    # ── School / Study ─────────────────────────────────────
    (["how to study", "study tips", "studying tips", "how to focus while studying"],
     ["Pomodoro technique: 25 min focus, 5 min break 🍅 Active recall and spaced repetition > passive rereading. Test yourself, don't just highlight.",
      "Study in short focused bursts (25-45 min), take proper breaks, eliminate distractions, and test yourself constantly 📚 That's the evidence-backed approach."]),

    (["how to write an essay", "essay tips", "essay writing"],
     ["Clear thesis → structured body paragraphs (claim, evidence, analysis) → strong conclusion 📝 Plan before you write. Every paragraph should connect back to your thesis.",
      "Start with an outline. Know your argument before you write a single sentence 📝 Introduction, 3 body paragraphs, conclusion. Each body paragraph = one point with evidence."]),

    (["i failed", "failed my exam", "failed a test", "failed a class"],
     ["One failure doesn't define you bro 💪 Figure out what went wrong, adjust, and come back stronger. Literally every successful person has a list of failures behind them.",
      "Failure is just data — it tells you what to do differently next time 💡 You've got this."]),

    # ── Relationships ──────────────────────────────────────
    (["relationship advice", "my girlfriend", "my boyfriend", "my partner", "relationship problems"],
     ["Communication is literally the foundation of everything in a relationship 🤙 If something's bothering you, say it. Most issues come from things left unsaid.",
      "Be honest, listen more than you talk, and show up consistently 💙 That's 90% of relationship success."]),

    (["how to get a girlfriend", "how to get a boyfriend", "how to get a partner", "how to find love"],
     ["Work on yourself first — confidence, goals, personality 💪 The rest tends to follow. Also just... talk to people. You can't find anyone staying silent.",
      "Be genuinely interested in people, develop yourself, put yourself in social situations 🤙 Love usually finds you when you stop desperately chasing it."]),

    (["breakup", "going through a breakup", "just broke up", "got broken up with"],
     ["Breakups hit different fr 💙 It's okay to feel it. Let yourself grieve, lean on your people, and remember that time actually does heal. You'll be okay.",
      "That's rough bro 💙 Feel what you need to feel, don't bottle it up. Lean on your friends. It gets better — genuinely."]),

    # ── Discord ────────────────────────────────────────────
    (["what is discord", "tell me about discord", "how does discord work"],
     ["Discord is a communication platform — text, voice, video, communities 🎮 Started as a gaming chat app, now used by basically everyone from gamers to businesses.",
      "Discord is basically the GOAT of community apps 🎮 Servers, channels, bots, voice chats — it has everything."]),

    (["how to make a discord server", "create a discord server"],
     ["Click the + button on the left sidebar in Discord → Create My Own → choose a template or start from scratch 🛠️ Then add channels, roles and bots to bring it to life."]),

    (["how to add a bot to discord", "discord bots", "best discord bots"],
     ["Go to discord.com/application or top.gg to find bots 🤖 Click 'Invite' and authorise it for your server. MEE6, Carl-bot, Dyno are popular choices."]),

    # ── Meme / Gen Z slang ─────────────────────────────────
    (["no cap", "no cap fr", "fr fr", "on god", "lowkey", "highkey", "bussin", "it's giving", "its giving", "slay", "periodt"],
     ["No cap fr fr 💯", "On god bro 💯", "Lowkey I fw that 🤙", "It's giving main character energy fr 💯", "Slay bestie 👑"]),

    (["among us", "sus", "impostor", "sussy", "among us crewmate"],
     ["Red kinda sus ngl 👀", "SUSSY BAKA 💀", "The impostor is... you 👉😳"]),

    (["sigma", "sigma grindset", "alpha", "beta", "gigachad"],
     ["Sigma grindset is basically just discipline with extra steps 💀",
      "Real sigmas don't talk about being sigma — they just move different 😤",
      "Gigachad energy detected in this server 🗿"]),

    (["rizz", "my rizz", "rizz check", "do i have rizz", "w rizz", "l rizz"],
     ["W rizz detected. The streets fear you 👑",
      "Rizz check: **PASSED** with distinction 🏆",
      "Your rizz is on another level fr. People are lucky to know you."]),

    (["aura", "aura check", "my aura", "check my aura", "aura points"],
     ["📊 **Aura Check:** Your aura is radiating at +9999 right now. Certified.",
      "🔮 Your aura? **Immaculate.** People feel it when you walk in.",
      "👑 Your aura is so strong it's affecting people around you without you even knowing."]),

    (["based", "based and redpilled", "that's based", "thats based"],
     ["Based 💯", "W take fr 💯", "Based and correct 🫡"]),

    (["ratio", "get ratioed", "you got ratiod"],
     ["The ratio is a powerful weapon 💀 Use it wisely.",
      "Getting ratioed on Discord... bro it's not that serious 😭"]),

    (["touch grass", "go outside", "skill issue"],
     ["Skill issue 💀", "Touch grass bro 🌿", "Genuine skill issue, no further comment 💀"]),

    # ── Would you rather ───────────────────────────────────
    (["would you rather", "wyr"],
     ["Would you rather have unlimited money but no friends, or be broke with the best people around you? 🤔",
      "Would you rather be able to fly or be invisible?",
      "Would you rather know when you're going to die, or how?",
      "Would you rather lose all your memories or never be able to make new ones?"]),

    # ── Fight / beef ───────────────────────────────────────
    (["fight me", "1v1 me", "square up", "catch me outside", "want to fight"],
     ["Bro I'm an AI I'll crash your game and blue screen your PC 😤",
      "1v1 me in Minecraft parkour, see who lasts 💀",
      "I don't fight, I just give bad responses until you leave 😭"]),

    # ── Roast comebacks ────────────────────────────────────
    (["you're dumb", "ur dumb", "you're stupid", "ur stupid", "you're trash", "ur trash", "you suck", "you're bad"],
     ["Ouch 💀 I'm doing my best bro",
      "Rude but valid, I'll work on it 😭",
      "I'm not dumb I'm just... creatively incorrect sometimes 💀",
      "That hurt fr 😭 But also fair enough 💀"]),

    (["you're smart", "ur smart", "you're intelligent", "you're so smart", "big brain"],
     ["I try my best 🧠💪", "Appreciate it! I'm built different 🧠",
      "I learned from the internet so honestly 50/50 💀"]),

    # ── Random facts ───────────────────────────────────────
    (["tell me a fact", "random fact", "give me a fact", "interesting fact", "fun fact"],
     ["🧠 Honey never expires. They found 3,000 year old honey in Egyptian tombs and it was still good.",
      "🧠 A group of flamingos is called a 'flamboyance'. Makes sense.",
      "🧠 Octopuses have 3 hearts, blue blood, and can edit their own RNA. They're built different.",
      "🧠 Crows can recognise human faces and hold grudges for years. Don't mess with crows.",
      "🧠 Bananas are technically berries but strawberries aren't. Nature is broken.",
      "🧠 A day on Venus is longer than a year on Venus. Space is cooked.",
      "🧠 Humans share 60% of their DNA with bananas 💀",
      "🧠 The Eiffel Tower grows about 15cm taller in summer due to thermal expansion.",
      "🧠 Nintendo was founded in 1889 — they started as a playing card company.",
      "🧠 There are more possible chess games than atoms in the observable universe.",
      "🧠 Sharks are older than trees — they've been around for about 450 million years.",
      "🧠 The moon is slowly drifting away from Earth at about 3.8cm per year.",
      "🧠 If you removed all the empty space from atoms in the human body, all 8 billion humans would fit in a sugar cube.",
      "🧠 Cleopatra lived closer in time to the Moon landing than to the building of the Great Pyramid.",
      "🧠 Wombats produce cube-shaped poo. Scientists only figured out why in 2018."]),

    # ── Time / Date ────────────────────────────────────────
    (["what time is it", "what's the time", "whats the time", "current time", "tell me the time"],
     ["__TIME__"]),

    (["what day is it", "what's the date", "whats the date", "today's date", "what is the date", "current date"],
     ["__DATE__"]),

    # ── Coin / Dice / Number ───────────────────────────────
    (["flip a coin", "coin flip", "heads or tails", "flip coin"],
     ["__COIN__"]),

    (["roll a dice", "roll dice", "roll a die", "dice roll"],
     ["__DICE__"]),

    (["pick a number", "random number", "give me a number", "generate a number"],
     ["__NUMBER__"]),

    # ── Motivation ─────────────────────────────────────────
    (["motivate me", "need motivation", "inspire me", "i give up", "i cant do it", "i can't do it", "feeling like giving up", "want to quit", "should i quit"],
     ["You got this fr. Every expert was once a beginner 💪",
      "Stop doubting yourself — you're built different 🔥",
      "The only way out is through. Keep pushing 💪",
      "Success is just failure that didn't quit. Keep going 🙌",
      "You've made it through 100% of your bad days so far. That's facts 💪",
      "One step at a time. You don't need to have it all figured out today 🤙"]),

    # ── Rate ───────────────────────────────────────────────
    (["rate me", "rate my", "give me a rating"],
     ["I rate you a solid 8/10 — you're clearly cool enough to talk to an AI 😎",
      "11/10 no cap, you're built different 👑",
      "Solid 7/10. Room to grow but the foundation is there 💪"]),
]

# ── Smart response engine ───────────────────────────────────────────────────
def get_ai_response(message: str) -> str:
    msg = message.lower().strip()
    clean = re.sub(r"[^\w\s]", " ", msg)

    # ── Exact math eval (e.g. "what is 5 * 8") ─────────────
    math_match = re.search(r"(\d+)\s*([\+\-\*\/\%\^])\s*(\d+)", msg)
    if math_match:
        try:
            a, op, b = int(math_match.group(1)), math_match.group(2), int(math_match.group(3))
            ops = {"+": a+b, "-": a-b, "*": a*b, "/": round(a/b,4) if b!=0 else "undefined", "%": a%b, "^": a**b}
            result = ops.get(op)
            return f"🧮 **{a} {op} {b} = {result}**" + (" 😎" if result == 69 else " 💀" if result == 0 else "")
        except Exception:
            pass

    # ── Keyword scan ────────────────────────────────────────
    for keywords, responses in TOPIC_MAP:
        for kw in keywords:
            if kw in clean or kw in msg:
                resp = random.choice(responses)
                # Dynamic tokens
                if resp == "__TIME__":
                    return f"🕐 It's **{datetime.utcnow().strftime('%H:%M')} UTC** right now!"
                if resp == "__DATE__":
                    return f"📅 Today is **{datetime.utcnow().strftime('%A, %B %d %Y')}** (UTC)!"
                if resp == "__COIN__":
                    return f"🪙 **{random.choice(['Heads!', 'Tails!'])}**"
                if resp == "__DICE__":
                    return f"🎲 You rolled a **{random.randint(1,6)}**!"
                if resp == "__NUMBER__":
                    return f"🎲 Your number is **{random.randint(1,100)}**!"
                return resp

    # ── Question catch-all ──────────────────────────────────
    question_words = ["what is", "what are", "what was", "what were", "who is", "who was", "who are",
                      "how do", "how does", "how did", "how to", "how can", "why is", "why does",
                      "why did", "why are", "when did", "when was", "where is", "where was",
                      "explain ", "tell me about", "describe ", "define "]
    for qw in question_words:
        if msg.startswith(qw) or f" {qw}" in msg:
            topic = msg
            for qw2 in question_words:
                topic = topic.replace(qw2, "").strip()
            topic = topic.strip("?. ")
            catch_alls = [
                f"Great question! **{topic}** is something I have limited info on — try Googling it for a deep dive, but here's my take: it's definitely worth knowing about 🧠",
                f"Hmm, **{topic}** — I know a bit but not everything. Wikipedia or a quick Google search will give you the full picture 📖",
                f"**{topic}** is actually a solid topic 🧠 I don't have a detailed answer built in, but if you Google it you'll find great info fast.",
                f"Good one! My knowledge on **{topic}** is limited — but the curiosity is W. Go look it up, you'll find it interesting 🧠",
            ]
            return random.choice(catch_alls)

    # ── Absolute fallback ───────────────────────────────────
    fallbacks = [
        "I don't have that one locked in yet 😅 Try asking differently or Google it!",
        "That's outside my current knowledge bro 💀 But ask me something else!",
        "Bro that question broke my brain 😭 Try rephrasing it?",
        "Not gonna lie I have no data on that one 💀 Google's got you though!",
        "My built-in brain doesn't cover that yet 😭 What else you got?",
        "That's a tough one... I'll say: **it depends** 😂 Try asking differently!",
    ]
    return random.choice(fallbacks)

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
