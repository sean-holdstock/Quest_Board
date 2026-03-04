import json
import os
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string
from google import genai
from dotenv import load_dotenv

app = Flask(__name__)

# --- CONFIGURATION ---
# Force explicit path to .env (next to app.py)
env_path = Path(__file__).resolve().parent / '.env'

# Load it explicitly
loaded = load_dotenv(dotenv_path=env_path)

# Debug prints to see what's happening
print("DEBUG: Looking for .env at:", env_path)
print("DEBUG: File exists?", env_path.exists())
print("DEBUG: load_dotenv returned:", loaded)
print("DEBUG: GEMINI_API_KEY after load:", os.getenv("GEMINI_API_KEY"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        f"GEMINI_API_KEY not found!\n"
        f"  - Tried loading from: {env_path}\n"
        f"  - File exists? {env_path.exists()}\n"
        f"  - load_dotenv success? {loaded}\n"
        f"  - Please check the file is readable and contains: GEMINI_API_KEY=your-key"
    )

client = genai.Client(api_key=GEMINI_API_KEY)

QUEST_FILE = 'quests.json'
LEVEL_DISTRIBUTION = [1, 1, 2, 2, 3, 3, 4, 5] # 2x Lvl 1, 2x Lvl 2, etc.

# --- DATA TABLES ---
NPCS = [
    # --- DWARVES ---
    {"name": "Grog Iron-Gut", "race": "Dwarf", "vibe": "Grumpy Tavern Keep"},
    {"name": "Helga Stone-Shield", "race": "Dwarf", "vibe": "Retired Guard"},
    {"name": "Bofur Copper-Vein", "race": "Dwarf", "vibe": "Eager Miner"},
    {"name": "Dagna Deep-Delver", "race": "Dwarf", "vibe": "Geologist"},
    {"name": "Thorin Ale-Slosh", "race": "Dwarf", "vibe": "Drunken Reveler"},
    {"name": "Gerta Forge-Fire", "race": "Dwarf", "vibe": "Master Smith"},
    {"name": "Orik Runebinder", "race": "Dwarf", "vibe": "Curious Scholar"},
    {"name": "Snorri Beard-Tangle", "race": "Dwarf", "vibe": "Messy Baker"},
    {"name": "Kili Gem-Eye", "race": "Dwarf", "vibe": "Jeweler"},
    {"name": "Ulfric Anvil-Hammer", "race": "Dwarf", "vibe": "Grizzled Veteran"},
    
    # --- HALFLINGS ---
    {"name": "Thistle Berrywhistle", "race": "Halfling", "vibe": "Panicked Gardener"},
    {"name": "Pippin Tea-Leaf", "race": "Halfling", "vibe": "Gossip Monger"},
    {"name": "Rosie Apple-Cheeks", "race": "Halfling", "vibe": "Cheerful Cook"},
    {"name": "Milo Quick-Step", "race": "Halfling", "vibe": "Nervous Messenger"},
    {"name": "Daisy Dew-Drop", "race": "Halfling", "vibe": "Flower Seller"},
    {"name": "Barnaby Butter-Ball", "race": "Halfling", "vibe": "Dairy Farmer"},
    {"name": "Finnian Fern-Gully", "race": "Halfling", "vibe": "Forest Guide"},
    {"name": "Cora Clover-Field", "race": "Halfling", "vibe": "Lucky Gambler"},
    {"name": "Odo Under-Hill", "race": "Halfling", "vibe": "Homebody"},
    {"name": "Tilly Tumble-Weed", "race": "Halfling", "vibe": "Young Adventurer"},

    # --- ELVES ---
    {"name": "Elara Nightbreeze", "race": "Elf", "vibe": "Aloof Scholar"},
    {"name": "Faelen Star-Gazer", "race": "Elf", "vibe": "Dreamy Astrologer"},
    {"name": "Luthien Silver-Leaf", "race": "Elf", "vibe": "Elegant Weaver"},
    {"name": "Theren Moon-Shadow", "race": "Elf", "vibe": "Quiet Hunter"},
    {"name": "Arwen Sun-Dancer", "race": "Elf", "vibe": "Graceful Performer"},
    {"name": "Legolas Pine-Walker", "race": "Elf", "vibe": "Skeptic Scout"},
    {"name": "Galadriel White-Tree", "race": "Elf", "vibe": "Mysterious Seer"},
    {"name": "Haldir Swift-Arrow", "race": "Elf", "vibe": "Border Patrol"},
    {"name": "Eowen Dew-Misty", "race": "Elf", "vibe": "Healer"},
    {"name": "Celeborn High-Tower", "race": "Elf", "vibe": "Strict Librarian"},

    # --- HUMANS ---
    {"name": "Sister Lumia", "race": "Human", "vibe": "Serene Priestess"},
    {"name": "Captain Silas", "race": "Human", "vibe": "Town Guard Captain"},
    {"name": "Miller Jace", "race": "Human", "vibe": "Tired Laborer"},
    {"name": "Old Man Hobb", "race": "Human", "vibe": "Eccentric Hermit"},
    {"name": "Baroness Elspeth", "race": "Human", "vibe": "Haughty Noble"},
    {"name": "Marcus the Brave", "race": "Human", "vibe": "Boastful Wannabe"},
    {"name": "Elena the Stout", "race": "Human", "vibe": "Blacksmith's Apprentice"},
    {"name": "Thomas the Tall", "race": "Human", "vibe": "Anxious Shepherd"},
    {"name": "Widow Martha", "race": "Human", "vibe": "Strict Landlady"},
    {"name": "Little Timmy", "race": "Human", "vibe": "Hopeful Orphan"},
    {"name": "Arthur Pen-Dragon", "race": "Human", "vibe": "Literary Critic"},
    {"name": "Gwen the Weaver", "race": "Human", "vibe": "Textile Expert"},
    {"name": "Farmer Giles", "race": "Human", "vibe": "Sturdy Orchardist"},
    {"name": "Merchant Flynn", "race": "Human", "vibe": "Persuasive Salesman"},
    {"name": "Robin the Red", "race": "Human", "vibe": "Local Minstrel"},
    {"name": "Sarah Saw-Dust", "race": "Human", "vibe": "Carpenter"},
    {"name": "Victor Vane", "race": "Human", "vibe": "Corrupt Politician"},
    {"name": "Mother Hubbard", "race": "Human", "vibe": "Kind Grandmother"},
    {"name": "Jack o' the Green", "race": "Human", "vibe": "Vagabond"},
    {"name": "Jill Water-Bearer", "race": "Human", "vibe": "Well Keeper"},

    # --- GNOMES ---
    {"name": "Krix Zapple", "race": "Gnome", "vibe": "Eccentric Inventor"},
    {"name": "Fizzle Bang-Pop", "race": "Gnome", "vibe": "Alchemist"},
    {"name": "Wizzle Widget", "race": "Gnome", "vibe": "Clockmaker"},
    {"name": "Zook Spark-Dust", "race": "Gnome", "vibe": "Pyrotechnician"},
    {"name": "Boddynock Glimmer", "race": "Gnome", "vibe": "Gemcutter"},
    {"name": "Nissa Nimble-Fingers", "race": "Gnome", "vibe": "Pickpocket"},
    {"name": "Tana Tinker-Toy", "race": "Gnome", "vibe": "Toymaker"},
    {"name": "Gimble Gold-Tooth", "race": "Gnome", "vibe": "Tax Collector"},
    {"name": "Puddles Mud-Skipper", "race": "Gnome", "vibe": "Frog Expert"},
    {"name": "Zinnia Zap-Sprocket", "race": "Gnome", "vibe": "Chaos Scientist"},

    # --- HALF-ORCS ---
    {"name": "Morgra Stone-Eye", "race": "Half-Orc", "vibe": "Retired Mercenary"},
    {"name": "Grog-Mash Heavy-Hand", "race": "Half-Orc", "vibe": "Bouncer"},
    {"name": "Ruk Iron-Hide", "race": "Half-Orc", "vibe": "Arena Fighter"},
    {"name": "Vola Bone-Cracker", "race": "Half-Orc", "vibe": "Street Surgeon"},
    {"name": "Zoka the Silent", "race": "Half-Orc", "vibe": "Monastic Monk"},
    {"name": "Throk Thunder-Voice", "race": "Half-Orc", "vibe": "Crier"},
    {"name": "Brak Blood-Moon", "race": "Half-Orc", "vibe": "Tracker"},
    {"name": "Gara Great-Axe", "race": "Half-Orc", "vibe": "Woodcutter"},
    {"name": "Mog Meat-Cleaver", "race": "Half-Orc", "vibe": "Butcher"},
    {"name": "Ursh Under-Steward", "race": "Half-Orc", "vibe": "Janitor"},

    # --- TIEFLINGS ---
    {"name": "Valen Holloway", "race": "Tiefling", "vibe": "Information Broker"},
    {"name": "Desiree Dark-Heart", "race": "Tiefling", "vibe": "Fortune Teller"},
    {"name": "Malakai Mourn", "race": "Tiefling", "vibe": "Undertaker"},
    {"name": "Skye Blue-Skin", "race": "Tiefling", "vibe": "Exotic Dancer"},
    {"name": "Raze Red-Horn", "race": "Tiefling", "vibe": "Ex-Pirate"},
    {"name": "Hope High-Spirits", "race": "Tiefling", "vibe": "Optimistic Rogue"},
    {"name": "Faith Fell-Wind", "race": "Tiefling", "vibe": "Warlock Acolyte"},
    {"name": "Charity Cold-Snap", "race": "Tiefling", "vibe": "Ice Merchant"},
    {"name": "Prudence Pale-Hoof", "race": "Tiefling", "vibe": "Strict Teacher"},
    {"name": "Verity Venom-Tongue", "race": "Tiefling", "vibe": "Poisoner"},

    # --- DRAGONBORN ---
    {"name": "Kriv Golden-Scale", "race": "Dragonborn", "vibe": "Proud Paladin"},
    {"name": "Balaak Blue-Flame", "race": "Dragonborn", "vibe": "Glassblower"},
    {"name": "Donaar Bronze-Shield", "race": "Dragonborn", "vibe": "Bodyguard"},
    {"name": "Mehen Red-Fury", "race": "Dragonborn", "vibe": "Hot-headed Guard"},
    {"name": "Patrin Silver-Soul", "race": "Dragonborn", "vibe": "Philosopher"},
    {"name": "Rhogar Copper-Spark", "race": "Dragonborn", "vibe": "Electrician"},
    {"name": "Shedinn White-Breath", "race": "Dragonborn", "vibe": "Fishmonger"},
    {"name": "Tarhun Black-Claw", "race": "Dragonborn", "vibe": "Assassin"},
    {"name": "Zoraid Green-Leaf", "race": "Dragonborn", "vibe": "Druid"},
    {"name": "Nadarr Iron-Skin", "race": "Dragonborn", "vibe": "Armorer"},

    # --- TABAXI (Cat Folk) ---
    {"name": "Cloud On-Mountain", "race": "Tabaxi", "vibe": "Wandering Minstrel"},
    {"name": "River At-Dawn", "race": "Tabaxi", "vibe": "Expert Fisherman"},
    {"name": "Shadow In-Mist", "race": "Tabaxi", "vibe": "Professional Thief"},
    {"name": "Five-Claw Scratch", "race": "Tabaxi", "vibe": "Impulsive Gambler"},
    {"name": "Swift Tail-Wag", "race": "Tabaxi", "vibe": "Curious Tourist"},
    {"name": "Quiet Paws", "race": "Tabaxi", "vibe": "Spy"},
    {"name": "Bright Eye", "race": "Tabaxi", "vibe": "Cartographer"},
    {"name": "Wild Fire", "race": "Tabaxi", "vibe": "Pyromaniac"},
    {"name": "Jade Serpent", "race": "Tabaxi", "vibe": "Contortionist"},
    {"name": "Golden Sun", "race": "Tabaxi", "vibe": "Sunny Optimist"}
]



TYPES = ["Extermination", "Gathering", "Locating", "Escort", "Sabotage"]

def generate_daily_quests():
    import random
    import json
    from datetime import datetime
    
    DEBUG_MODE = True
    api_online = False
    final_quests = []
    comedic_note = ""

    # --- COMEDIC BACKUP POOL ---
    GRIEVANCES = [
        "DERICK: Stop adding lute lessons to the board!",
        "The 'Free Dragon' at the gate is just a large dog. STOP.",
        "Found: One left boot. Smells of swamp. Claim at bar.",
        "Laundry lists are NOT bounties. Use the other board!",
        "To the person who stole the tavern's 'Good Ladle': Return it.",
        "STOP using the board to find dates. You are all lonely.",
        "The mimic in the cellar has been fed. Do not enter.",
        "Losing your pants at the festival is not an 'Epic Quest'.",
        "Whoever is drawing mustaches on the posters: I will find you.",
        "The well is for WATER, not copper coins and wishes!",
        "Will the person who brought the 'Emotional Support Bear' leave?",
        "NOTICE: The town wizard is currently a frog. Be patient.",
        "Derick: Your 'Lute Solo' request was burnt for fuel.",
        "Looking for: My dignity. Lost after the third ale.",
        "The bridge troll is on strike. Use the ferry.",
        "Stop reporting the 'floating eye'. It's just a balloon.",
        "To whoever pinned a dead fish here: Why?",
        "The 'Invisibility Potion' for sale was just water. Scammer!",
        "No, I will not trade ale for 'Magic Beans'.",
        "WANTED: Someone to tell my wife I'm at the tavern."
    ]
    # 1. THE DYNAMIC POOLS (Your 100 Quest Templates - Backup & Vibe Guide)
    POOLS = {
        1: [
            "needs the cellar rats cleared before they spoil the winter grain.",
            "is looking for five bundles of kingsfoil from the forest floor.",
            "says their prize goat has wandered into the eastern woods.",
            "needs a volunteer to watch the south bridge for stray goblins tonight.",
            "needs a runner to take a letter to the neighboring hamlet.",
            "is offering a reward to anyone who can catch that stray blink-dog.",
            "needs four glowing mushrooms from the damp cellar for a stew.",
            "needs help investigating a 'thumping' sound in their shop walls.",
            "dropped a signet ring near the magpie nests in the town square.",
            "needs a strong back to help move iron pig-ingots to the forge.",
            "needs someone to fetch fresh spring water for their stall.",
            "is looking for a lost cow, Bessie, last seen near the creek.",
            "needs a guide for a group of berry-pickers today.",
            "needs the weeds cleared from a family member's grave.",
            "says their child lost a wooden sword in the tall grass.",
            "needs someone to untangle a massive shipment of wool.",
            "needs help shucking the corn before the sun sets.",
            "needs a hand fixing a broken wagon wheel.",
            "needs the town well bucket retrieved from the bottom.",
            "needs a few surface stones carried to the jeweler for inspection."
        ],
        2: [
            "says a nest of stirges has taken over the old bell tower.",
            "reports bandits stole a holy tome from the chapel. Recover it.",
            "needs a guard for a spice caravan traveling to the next town.",
            "wants the giant spiders nesting beneath the south bridge culled.",
            "says an heirloom locket was snatched by a pickpocket. Find them.",
            "needs three vials of frost-moss from the northern caves.",
            "says a 'shadow man' is painting symbols on the tavern walls.",
            "is looking for a missing shipment of iron on the mountain trail.",
            "says the sewers are overrun with filth-drakes again.",
            "needs help fending off a group of aggressive scarecrows.",
            "needs an escort to the edge of the old stone quarry.",
            "is looking for a specific blue-inked mushroom in the caves.",
            "needs someone to guard their fresh pies from a local thief.",
            "wants to find the 'hidden cave' they saw in a dream.",
            "needs an escort through the woods to deliver a local tax.",
            "needs a barrel of 'special' water from the high mountain spring.",
            "is looking for a retired guard-dog that went missing.",
            "needs help finding their misplaced boots after a long night.",
            "needs a rare garnet retrieved from the nearby riverbank.",
            "needs a message delivered quickly to the captain of the guard."
        ],
        3: [
            "says wolves are getting bolder near the sheep pens at night.",
            "needs an escort to the mountain shrine for their yearly prayers.",
            "reports the old ruins are crawling with restless skeletons.",
            "needs silk harvested from the giant spiders deep in the forest.",
            "needs someone to retrieve a 'singing sword' from the drakes.",
            "is worried about the statues moving in the local library.",
            "needs the essence of a minor fire spirit to warm their cottage.",
            "says a 'small dragon' (likely a wyvern) stole a prize ham.",
            "needs help recovering lost map fragments from a goblin camp.",
            "needs extra security for the town square during the festival.",
            "needs a rare moon-flower that only blooms at midnight.",
            "needs a scout to help track a displaced bear in the orchard.",
            "is seeing portents of an owl-bear nesting in the grove.",
            "needs someone to check the northern border outposts for activity.",
            "needs venom from a giant wasp to make a life-saving antidote.",
            "needs help reorganizing the 'restricted' section of the archives.",
            "needs a volunteer to investigate the 'ghost' at the old mill.",
            "says a family of harpies is nesting in the grain silo.",
            "needs help clearing a patch of 'screaming' mandrake roots.",
            "needs a discreet escort through the Whispering Woods."
        ],
        4: [
            "says a manticore is harassing travelers on the bluffs.",
            "needs a discreet escort for a messenger through the serpent marsh.",
            "needs a specific relic retrieved from the Sunken Temple ruins.",
            "says a coven of hags is blighting the northern crops.",
            "needs a heart-stone harvested from a rogue Earth Elemental.",
            "is putting a bounty on the local bandit leader, 'Black-Heart'.",
            "needs someone to check the ancient runes on the Western Spire.",
            "wants someone to 'misplace' a shipment of rival iron weapons.",
            "is looking for 10 scales from the hydra living in the lake.",
            "needs a guard for their workshop during a dangerous experiment.",
            "needs someone to 'help' them slay a giant (you do the work).",
            "needs dragon-fire to heat a forge for a masterwork blade.",
            "says a griffon is picking off the best rams in the hills.",
            "needs someone to clear the 'haunted' attic of the boarding house.",
            "wants to find the 'treasure' guarded by the old willow tree.",
            "needs help recovering a lost manuscript from a harpy nest.",
            "needs silk from a Phase Spider for a magical garment.",
            "needs a guard for a shipment of 'unstable' alchemical potions.",
            "needs someone to find a lost lute in the goblin warrens.",
            "needs help clearing wood-wiles from the local timber yard."
        ],
        5: [
            "says a Young Red Dragon has taken residence in the watchtower.",
            "found a dangerous breach into the Underdark in the deep mines.",
            "needs an escort for a visiting Archmage across the high pass.",
            "needs a 'Soul-Shard' from a local crypt to save a dying friend.",
            "has a contract for an orc warlord threatening the outskirts.",
            "says the old king's crown is being held by a local hill giant.",
            "says a rogue necromancer is raising the town's ancestors.",
            "needs the Labyrinth cleared of a particularly nasty minotaur.",
            "is looking for a feather from a legendary Phoenix.",
            "is looking for a challenger to face the 'Blood-Arena' champion.",
            "says the dead are refusing to stay in the ground tonight.",
            "needs someone to recover their 'enchanted' dance slippers.",
            "is looking for a lost treasure chest buried in the marsh.",
            "needs help 'borrowing' a relic from the high temple.",
            "is looking for a volunteer for a 'mostly safe' magic ritual.",
            "needs someone to harvest ice from the heart of a frost giant.",
            "needs a rare book retrieved from the ruins of the Old Library.",
            "needs venom from a Basilisk for a highly potent tonic.",
            "needs a squire to help them purge a nest of vampires nearby.",
            "needs 'Breath of a Blue Dragon' to fire their finest glass-work."
        ]
    }

    # 2. THE WIZARD'S ATTEMPT (AI Generation)
# 2. THE WIZARD'S ATTEMPT (AI Generation)
    try:
        if DEBUG_MODE: print("--- DEBUG: Wizard is writing quests... ---")
        todays_npcs = random.sample(NPCS, 8)
        # We create the context list for the AI
        npc_context = "\n".join([f"- {n['name']} ({n['race']}, {n['vibe']})" for n in todays_npcs])

        # 1. FIXED THE F-STRING: Use double {{ }} around {Race} so Python doesn't think it's a variable
        prompt = f"""
                    You are a Quest-Master creating 8 daily quests for a fantasy adventurers' board. 
                    NPCs today:
                    {npc_context}

                    CRITICAL: Generate quests IN STRICT ORDER OF INCREASING DIFFICULTY.
                    Distribution: [1, 1, 2, 2, 3, 3, 4, 5] 
                    - Lvl 1: Simple errands.
                    - Lvl 2: Minor threats.
                    - Lvl 3: Moderate peril.
                    - Lvl 4: Serious danger.
                    - Lvl 5: Epic/Legendary threats (No mundane tasks).

                    Rules:
                    1. Exactly 8 lines, ONE QUEST PER LINE: [TYPE] | [Quest text]
                    2. TYPES: Bounty, Extermination, Gathering, Locating, Escort, Sabotage
                    3. Text Format: "[Name] ({{Race}}): [First-person request text]"
                    4. Voice: Use FIRST PERSON (I/me/my). Match vocabulary to NPC vibe.
                    5. Constraint: Total text must be 70-115 characters.
                    6. NO gold, NO levels in the text.

                    Examples:
                    Bounty | Rosie Apple-Cheeks (Halfling): My prize pig has bolted. Find the fat lug before he eats the neighbor's roses!
                    Extermination | Kriv Golden-Scale (Dragonborn): A young red dragon mocks my honor. Slay the beast and bring me its heart.
                """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        if response.text:
            lines = response.text.strip().split('\n')
            for line in lines:
                if "|" in line and len(final_quests) < 8:
                    parts = line.split("|", 1)
                    if len(parts) == 2:
                        raw_type, raw_text = parts
                        
                        q_type = raw_type.strip().title()
                        valid_types = {"Extermination", "Gathering", "Locating", "Escort", "Sabotage", "Bounty"}
                        if q_type not in valid_types:
                            q_type = "Bounty"

                        lvl = LEVEL_DISTRIBUTION[len(final_quests)]
                        # Match the NPC used in this line
                        match = next((n for n in todays_npcs if n['name'] in raw_text), todays_npcs[len(final_quests)])

                        # 2. FIXED THE PREFIX LOGIC: 
                        # We no longer force "Name the Race" because the AI is already providing "Name (Race):"
                        q_text = raw_text.strip()

                        final_quests.append({
                            "level": "*" * lvl,
                            "type": q_type,
                            "text": q_text[:135], # Safety clip
                            "signature": match['name'],
                            "gold": f"{random.randint(lvl*10, lvl*80)} GP"
                        })
            
            if len(final_quests) == 8:
                api_online = True

    except Exception as e:
        if DEBUG_MODE: print(f"--- DEBUG: AI Failed: {e} ---")
        api_online = False
        
 # 3. BACKUP LOGIC (If AI failed or was throttled)
    # This checks if 'final_quests' is empty. If it is, we fill it from your POOLS.
    if not final_quests:
        if DEBUG_MODE: print("--- DEBUG: Falling back to local quest pools. ---")
        for lvl in LEVEL_DISTRIBUTION:
            pool = POOLS[lvl]
            template = random.choice(pool)
            npc = random.choice(NPCS)
            
            full_text = f"{npc['name']} the {npc['race']} {template}"
            
            # Local keyword logic to determine quest type
            low_text = template.lower()
            if any(word in low_text for word in ["clear", "cull", "slay", "hunt", "defeat", "purge"]):
                q_type = "EXTERMINATION"
            elif any(word in low_text for word in ["find", "recover", "search", "retrieve", "locate", "fetch"]):
                q_type = "LOCATING"
            elif any(word in low_text for word in ["need", "bring", "collect", "harvest", "gather"]):
                q_type = "GATHERING"
            elif any(word in low_text for word in ["escort", "guard", "protect"]):
                q_type = "ESCORT"
            else:
                q_type = "BOUNTY"

            final_quests.append({
                "level": "*" * lvl,
                "type": q_type,
                "text": full_text,
                "signature": npc['name'],
                "gold": f"{random.randint(lvl*5, lvl*80)} GP"
            })

    # 3b. GRIEVANCE BACKUP
    # If the AI didn't provide a joke, grab one from your local list
    if not comedic_note:
        comedic_note = random.choice(GRIEVANCES)

    # 4. SAVE DATA (Indented once, so it's inside the function)
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"), 
        "quests": final_quests,
        "comedic_note": comedic_note,
        "api_online": api_online
    }
    
    with open(QUEST_FILE, 'w') as f:
        json.dump(data, f, indent=4)
        
    return data
# --- UPDATE GET_QUESTS: To return the full data object ---
def get_quests():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(QUEST_FILE):
        with open(QUEST_FILE, 'r') as f:
            data = json.load(f)
            if data.get("date") == today:
                return data # Return the whole dict so index() can see api_online
    
    # If file doesn't exist or date is old, generate new ones
    return generate_daily_quests()


# --- WEB ROUTE ---
# Move the HTML string OUTSIDE the function so it doesn't clutter your logic
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
<style>
    @import url('https://fonts.googleapis.com/css2?family=Architects+Daughter&family=MedievalSharp&family=Great+Vibes&family=Homemade+Apple&family=Cedarville+Cursive&family=Reenie+Beanie&display=swap');
    
    * { box-sizing: border-box; }

    :root {
        --wood-dark: #2a1a12;
        --wood-medium: #3a251e;
        --parchment: #f5e8c7;
        --ink: #0f0b07;
        --gold-bright: #d4af37;
    }

    body {
        background: 
            radial-gradient(circle at center, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.7) 100%),
            url("https://www.transparenttextures.com/patterns/stone-wall.png"),
            #1e0f09;
        background-blend-mode: multiply;
        background-attachment: fixed;
        color: var(--ink);
        margin: 0;
        padding: 20px 20px; 
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: 'Architects Daughter', cursive;
    }

    /* --- FOCUS MODE OVERLAY --- */
    #board-overlay {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(5px);
        opacity: 0; visibility: hidden;
        transition: opacity 0.4s ease;
        z-index: 1500;
    }
    #board-overlay.active { opacity: 1; visibility: visible; }

    /* 1. THE WIZARD ALERT */
    #wizard-alert {
        position: fixed;
        top: 20px;
        background: linear-gradient(145deg, #2a1a12, #1a0f0d);
        border: 2px solid var(--gold-bright);
        color: #f4e4bc;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 15px rgba(212, 175, 55, 0.3);
        z-index: 2000;
        display: flex;
        align-items: center; gap: 15px;
        transform: translateY(-150%);
        transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    #wizard-alert.show { transform: translateY(0); }

    /* --- THE BOARD --- */
    .board {
        position: relative;
        width: min(1400px, 98vw); 
        background-color: #3d2b1f; 
        background-image: 
            repeating-linear-gradient(90deg, transparent, transparent 118px, rgba(0, 0, 0, 0.3) 118px, rgba(0, 0, 0, 0.3) 120px),
            linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.4) 100%);
        border: 30px solid #1a0f0d;
        padding: 30px 40px 40px; 
        box-shadow: inset 0 0 100px #000, 0 30px 80px rgba(0,0,0,0.8);
        display: grid;
        grid-template-columns: repeat(4, 1fr); 
        gap: 25px 20px; 
        justify-content: center;
        align-items: start;
    }

    .scrawl-note {
        position: absolute;
        top: -12px; right: 10px; 
        width: 180px;
        background: #fff9c4;
        color: #b71c1c;
        padding: 12px;
        font-size: 0.9em;
        font-weight: bold;
        transform: rotate(8deg);
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
        z-index: 500;
        text-align: center;
        border: 1px solid #f0e68c;
    }

    h1 {
        font-family: 'MedievalSharp', cursive;
        color: #f4e4bc;
        text-shadow: 2px 2px 0px #000, -1px -1px 0px var(--gold-bright);
        font-size: clamp(1.8em, 4vw, 2.8em); 
        margin: 0 0 15px; 
        text-align: center;
        background: linear-gradient(to bottom, #2a1a12, #14080a);
        padding: 10px 60px; 
        border-radius: 4px;
        border: 4px solid var(--gold-bright);
        box-shadow: 0 10px 20px rgba(0,0,0,0.5), inset 0 0 15px rgba(212, 175, 55, 0.2);
        grid-column: 1 / -1;
    }

    .quest-wrapper {
        display: flex; flex-direction: column; align-items: center;
        position: relative; cursor: pointer;
        transform-origin: top center; 
    }

    .quest-wrapper::before {
        content: '';
        width: 24px; height: 24px;
        background: radial-gradient(circle at 30% 30%, #555, #111);
        border: 3px solid #000;
        border-radius: 50%;
        box-shadow: inset 2px 2px 0px #777, 0 4px 6px rgba(0,0,0,0.8);
        position: relative; top: 35px;
        z-index: 1000; margin-bottom: -24px;
        transition: opacity 0.2s ease;
    }

    .quest-wrapper.focused::before { opacity: 0; }

    .note {
        width: 100%; max-width: 380px; min-height: 480px;
        padding: 85px 45px;
        background: url("{{ url_for('static', filename='weathered-scroll-transparent.png') }}") center / 100% 100% no-repeat;
        position: relative;
        display: flex; flex-direction: column;
        filter: drop-shadow(12px 12px 0px rgba(0,0,0,0.4));
        opacity: 0;
        animation: fadeInUp 0.6s ease-out forwards;
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    /* --- DESKTOP FOCUS LOGIC (Corrected) --- */
    .quest-wrapper.focused { 
        z-index: 1600; 
    }
    
    .quest-wrapper.focused .note {
         position: fixed; 
         top: 50%; 
         left: 50%;
         transform: translate(-50%, -50%) scale(1.1) rotate(0deg) !important;
         width: 95vw; max-width: 500px; 
         height: auto; max-height: 80vh; 
         padding: 90px 50px; 
    }
    
    .quest-wrapper.focused .gold-plate {
        position: fixed;
        top: calc(50% + 220px); 
        left: 50%;
        transform: translateX(-50%);
        z-index: 1601; 
        width: 220px;
        margin-top: 0;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px) rotate(-3deg); }
        to { opacity: 1; transform: translateY(0) rotate(var(--rotation, 0deg)); }
    }

    .note-header {
        text-align: center; display: flex; flex-direction: column-reverse; 
        border-bottom: 4px double rgba(0,0,0,0.1);
        margin-bottom: 15px; padding-bottom: 5px;
    }

    .wanted-text {
        font-family: 'MedievalSharp', serif;
        font-weight: bold; font-size: 0.9em;
        color: #b8860b; text-transform: uppercase;
    }

    .stars { font-size: 1.4em; color: #b8860b; }

    .note-text {
        font-family: 'Architects Daughter', cursive;
        font-size: 1.1em; line-height: 1.4;
        color: var(--ink); display: flex; flex-direction: column;
        justify-content: space-between; flex-grow: 1;
    }

    .signature {
        text-align: right; margin-top: auto; padding-top: 15px;
        font-family: 'Great Vibes', cursive; font-size: 1.8em;
        color: #3a1f12;
    }

    .gold-plate {
        width: 75%; margin-top: -18px;
        background: linear-gradient(145deg, #e6c253, #aa8a2e);
        color: #1a0f0d; font-family: 'MedievalSharp', serif;
        font-weight: bold; font-size: 1.2em; text-align: center;
        padding: 10px; border: 2px solid #5c430d; border-top: none;
        box-shadow: 0 6px 12px rgba(0,0,0,0.6); border-radius: 0 0 10px 10px;
        position: relative; z-index: 5; transition: all 0.4s ease;
    }

    .timer-container {
        grid-column: 1 / -1; width: 100%; max-width: 700px;
        margin: 0 auto 10px; 
        background: rgba(0,0,0,0.8);
        padding: 10px 20px; 
        border-radius: 8px;
        border: 2px solid var(--gold-bright);
        display: flex; flex-direction: column; gap: 5px;
    }

    .hourglass-label {
        font-family: 'MedievalSharp', serif;
        color: var(--gold-bright); font-size: 1.1em;
        text-transform: uppercase; text-align: center;
    }

    .timer-bar-outer {
        width: 100%; height: 14px; background: #1a0f0d;
        border: 1px solid var(--gold-bright); border-radius: 10px;
        overflow: hidden;
    }

    .timer-bar-inner {
        height: 100%; background: linear-gradient(90deg, #8b4513, var(--gold-bright), #8b4513);
        background-size: 200% 100%; animation: flowing-sand 5s linear infinite;
        width: {{ 100 - day_progress }}%;
    }

    @keyframes flowing-sand {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }

    /* --- RANDOMIZED TILTS --- */
    .quest-wrapper:nth-child(odd) { transform: rotate(-1.5deg); }
    .quest-wrapper:nth-child(even) { transform: rotate(1.2deg); }
    .quest-wrapper:nth-child(3n) { transform: rotate(1.8deg); }
    .quest-wrapper:nth-child(4n) { transform: rotate(-2.1deg); }

    .quest-wrapper.focused { transform: rotate(0deg) !important; }

    /* --- RANDOMIZED SIGNATURES & INK --- */
    .quest-wrapper:nth-child(2n) .signature {
        font-family: 'Cedarville Cursive', cursive;
        font-size: 1.5em;
    }

    .quest-wrapper:nth-child(3n) .signature {
        font-family: 'Homemade Apple', cursive;
        font-size: 1.3em;
    }

    .quest-wrapper:nth-child(4n) .signature {
        font-family: 'Reenie Beanie', cursive;
        font-size: 2.2em;
    }

    .quest-wrapper:nth-child(odd) .signature {
        color: #2a1a12; /* Charcoal ink */
    }
    
    .quest-wrapper:nth-child(even) .signature {
        color: #4b3621; /* Dried blood / Rusty ink */
    }

    /* --- RESPONSIVE ADJUSTMENTS --- */
    @media (max-width: 1100px) {
        .board { grid-template-columns: repeat(2, 1fr); }
    }

    @media screen and (max-width: 600px) {
        .board { 
            grid-template-columns: 1fr; 
            padding: 80px 10px 30px !important;
            border-width: 15px !important;
        }

        .scrawl-note {
            width: 220px !important;
            font-size: 1.15rem !important;
            top: -25px !important;
            left: 50% !important;
            transform: translateX(-50%) rotate(3deg) !important;
            padding: 10px !important;
        }

        .hourglass-label {
            font-size: 1.4rem !important;
            letter-spacing: 0.5px !important;
        }

        .timer-bar-outer { height: 24px !important; }

        h1 {
            font-size: 1.6rem !important;
            padding: 12px 10px !important;
            margin-bottom: 25px !important;
        }

        /* --- MOBILE-ONLY FIX: Wrapper becomes the fixed container --- */
        .quest-wrapper.focused {
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            width: 90vw !important;
            height: auto !important;
            transform: translate(-50%, -50%) !important;
            z-index: 1700 !important;
        }

        .quest-wrapper.focused .note {
            position: relative !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            max-height: 70vh !important; 
            padding: 70px 30px 100px !important;
            transform: none !important;
        }

        .quest-wrapper.focused .gold-plate {
            position: absolute !important; 
            top: auto !important;
            bottom: -15px !important; 
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 180px !important;
            z-index: 1701 !important;
            margin: 0 !important;
        }
    }
</style>
</head>
<body>
    <div id="board-overlay"></div>

    <div id="wizard-alert" {% if api_failed %}class="show"{% endif %}>
        <span>😴</span>
        <div>
            <strong style="color: #d4af37; display: block;">Notice from the Spire:</strong>
            The Wizard has gone to sleep. Using archived scrolls for today's bounties.
        </div>
    </div>

    <div class="board">
        <div class="scrawl-note">{{ comedic_note }}</div>
        <h1>ADVENTURERS WANTED</h1>

        <div class="timer-container">
            <div class="hourglass-label">{{ hours_left_text }}</div>
            <div class="timer-bar-outer">
                <div class="timer-bar-inner"></div>
            </div>
        </div>

        {% for q in quests %}
        <div class="quest-wrapper" onclick="focusQuest(this)"> 
            <div class="note note-{{ loop.index }}">
                <div class="note-header">
                    <span class="stars">{{ q.level }}</span>
                    <div class="wanted-text">{{ q.type }} WANTED</div>
                </div>
                <div class="note-text">
                    {{ q.text }}
                    <div class="signature">{{ q.signature }}</div>
                </div>
            </div>
            <div class="gold-plate">{{ q.gold }}</div>
        </div>
        {% endfor %}
    </div>

    <script>
        const overlay = document.getElementById('board-overlay');

        function focusQuest(element) {
            if (element.classList.contains('focused')) {
                closeAllQuests();
                return;
            }
            closeAllQuests();
            element.classList.add('focused');
            overlay.classList.add('active');
        }

        function closeAllQuests() {
            document.querySelectorAll('.quest-wrapper').forEach(q => q.classList.remove('focused'));
            overlay.classList.remove('active');
        }

        overlay.addEventListener('click', closeAllQuests);
    </script>
<footer style="margin-top: 40px text-align: center; color: #8b6f47; font-szie: 0.9em; opacity: 0.8;">
    Created By  <a href="https://github.com/sean-holdstock/" style="color: #d4af37; text-decoration: none;"> Sean Holdstock </a> 2026
</body>
</html>
"""


@app.route('/')
def index():
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    data = None
    
    # Try to load existing file first
    if os.path.exists(QUEST_FILE):
        try:
            with open(QUEST_FILE, 'r') as f:
                data = json.load(f)
            print(f"DEBUG: Loaded quests.json successfully - {len(data.get('quests', []))} quests")
            
            # Only regenerate if date is wrong or quests are missing/empty
            if data.get("date") != today_str or not data.get("quests"):
                print("DEBUG: Date mismatch or empty quests → regenerating")
                data = generate_daily_quests()
            else:
                print("DEBUG: Using valid cached quests for today")
                
        except json.JSONDecodeError as e:
            print(f"DEBUG: quests.json is corrupted/invalid JSON: {e} → regenerating")
            data = generate_daily_quests()
        except Exception as e:
            print(f"DEBUG: Error loading quests.json: {type(e).__name__} - {e} → regenerating")
            data = generate_daily_quests()
    
    # If no file or load failed completely
    if data is None:
        print("DEBUG: No valid data loaded → generating fresh quests")
        data = generate_daily_quests()

    quests = data.get("quests", [])
    api_failed = not data.get("api_online", True)

    # Timer logic
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    day_percentage = (seconds_since_midnight / 86400) * 100
    hours_left_val = 24 - now.hour
    hours_label = "bells" if hours_left_val != 1 else "bell"
    time_text = f"The ink fades in approximately {hours_left_val} {hours_label}..."

    print(f"DEBUG: Final render - {len(quests)} quests will be shown")

    return render_template_string(
        html,
        quests=quests,
        comedic_note=data.get('comedic_note', 'No notes today.'),
        day_progress=day_percentage,
        hours_left_text=time_text,
        api_failed=api_failed
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
