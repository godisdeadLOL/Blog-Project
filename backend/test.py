import random
import requests

from models import User

usernames = [
    "skyWalker42",
    "akira_blaze",
    "NeoSamurai",
    "cheshire_cat99",
    "MysticNavi",
    "titan_fury",
    "NinjaScroll",
    "GoKuVortex",
    "shadow.link",
    "AstroRanger67",
    "mecha@maverick",
    "starAlchemist",
    "yoshiRoar",
    "falconJin",
    "Ruby_Hawkeye",
    "JetBender",
    "spideySensei08",
    "Ember-Fox",
    "sonicZ94",
    "ironGuts",
    "jediPulse",
    "neon_gundam",
    "PikachuStorm",
    "cyber_Sakura",
    "thunderZELDA",
    "wolf.packZ",
    "PixelNinja",
    "spiritTrekker",
    "phoenix_zelda",
    "SonicEclipse",
    "Ranger_Leviathan",
    "windRogue",
    "SamuraiSpartan",
    "vortex_vigil",
    "NimbusMage",
    "blazingKorra",
    "Rogue_Cipher",
    "aura_titan",
    "bladeSaber",
    "VulpixVolt",
    "cyber-Hunter",
    "samuraiFusion",
    "stardustRider",
    "DragonZen",
    "kryptoKnight",
    "aurora.ryu",
    "KnightShade",
    "phase_blaster",
    "CosmicF@ng",
    "Cloud-Stinger",
    "shogunPulse",
    "atomic_Ronin",
    "HyperLynx",
    "archerNova",
    "ArcaneRaptor",
    "Chrono$hifter",
    "AzureFalcon",
    "GalaxyNinja",
    "shadowVortex",
    "NeoTengu88",
    "astral_Rogue",
    "SolarJinx",
    "phoenix.blaze",
    "novaSpectre",
    "sapphireEdge",
    "emerald_Rift",
    "AetherStrider",
    "TitanSage",
    "stormRanger",
    "orion_voyager",
    "turboKitsune",
    "BlazingRider",
    "lunar.knight",
    "RadiantZeke",
    "cyberV@lkyrie",
    "CrimsonRook",
    "stellarFox",
    "frostSaber",
    "quantum_rebel",
    "ThunderNinja",
    "saberFalcon",
    "ZeroZenith",
    "Luna_Harbinger",
    "galaxyReaver",
    "EchoNightingale",
    "arcFlare",
    "spira_soul",
    "TitanWave",
    "midnightScribe",
    "TurboChocobo",
    "blazeWolf",
    "infinityKaze",
    "IRONPhoenix",
    "astraZen",
    "phoenix_soul",
    "HoloSpecter",
    "cyber_Astral",
    "QuantumZ",
    "mysticDynamo",
    "EquinoxBlade",
]

base_url = "http://127.0.0.1:5000"

# create users
user_amount = 24

users_data = []

for i in range(user_amount):
    user_data = {"username": str.lower(usernames[i]), "password": ""}
    user_data["password"] = user_data["username"] + "_password"

    # register
    requests.post(f"{base_url}/auth/temp_register", json=user_data)

    print("created user:", user_data)
    users_data.append(user_data)

    # login
    response = requests.post(f"{base_url}/auth/login", data=users_data[i])
    users_data[i]["access_token"] = response.json()["access_token"]
    users_data[i]["headers"] = {"Authorization": f"Bearer {users_data[i]['access_token']}"}

# create boards and posts
boards_amount = 4

# owner, admin, moderator, creator
admins_per_board = 1
moderators_per_board = 2
creators_per_board = 2

posts_per_board_per_user = 2

current_user = 0
for i in range(boards_amount):
    user_data = users_data[current_user]

    # create board
    response = requests.post(
        f"{base_url}/board/",
        headers=user_data["headers"],
        json={"name": f"{user_data['username']}'s board"},
    )

    board_data = response.json()

    print("Created board:", board_data["name"])

    current_user += 1

    for j in range(admins_per_board + moderators_per_board + creators_per_board):
        sub_user_data = users_data[current_user]

        if j < admins_per_board:
            level = 3
        elif j < admins_per_board + moderators_per_board:
            level = 2
        else:
            level = 1

        # set role
        response = requests.post(
            f"{base_url}/role/",
            headers=user_data["headers"],
            json={"user_id": current_user+1, "board_id": board_data["id"], "level": level},
        )
        
        if response.status_code == 307 :
            print(response.headers)

        # create posts
        for k in range(posts_per_board_per_user):
            response = requests.post(
                f"{base_url}/post/",
                headers=sub_user_data["headers"],
                json={
                    "board_id": board_data["id"],
                    "title": f"Post number {k+1} at {board_data['name']} by {sub_user_data['username']}",
                    "content": f"This content is written by {sub_user_data['username']}",
                },
            )

        current_user += 1


# random comments
comments_per_user = 5

for user_data in users_data:

    for i in range(comments_per_user):
        post_id = random.randint(
            1,
            posts_per_board_per_user
            * (admins_per_board + moderators_per_board + creators_per_board)
            * boards_amount,
        )

        response = requests.post(
            f"{base_url}/comment/",
            headers=user_data["headers"],
            json={
                "post_id": post_id,
                "content": f"This is {i}th comment is written by {user_data['username']}",
            },
        )
