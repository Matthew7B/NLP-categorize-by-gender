import json
import os
import pickle
import re

BASEDIR = 'D:\Scratch\discord_files'
mf = ['♂', '♀']
gender_synonyms = ['male', 'female', 'he/him', 'she/her', 'man', 'woman', 'boy', 'girl']
debug = 0


def msg_to_txt(msg):
    msg_txt = msg['content'] + '\n' + '\n'.join([y['description'] for y in msg['embeds'] if 'description' in y])
    for role_id, role_name in role_id_name:
        role_tag = f'<@&{role_id}>'
        msg_txt = msg_txt.replace(role_tag, role_name)
    return msg_txt


def check_role_name(name):
    weird_chars = 'FΣMΛLΣ'
    if any([x for x in weird_chars if x in name]):
        weird_chars_replacement = 'female'
        for char, replacement in zip(weird_chars, weird_chars_replacement):
            name = name.replace(char, replacement)
        name = name.replace(' ', '')

    if name in mf:
        return True
    if re.search(f'([^\w]|^)(?:{"|".join(gender_synonyms)})([^\w]|$)', name.lower()):
        return True
    return False


def get_user_roles(guild_json_dict):
    # mbti_types = ['ISTJ', 'ISTP', 'ISFJ', 'ISFP', 'INFJ', 'INFP', 'INTJ', 'INTP', 'ESTP', 'ESTJ', 'ESFP', 'ESFJ', 'ENFP', 'ENFJ', 'ENTP', 'ENTJ']
    # roles_of_interest = [x['name'] for x in guild_json_dict['roles'] if any([y for y in mbti_types if y == x['name']])]
    roles_of_interest = [x['name'] for x in guild_json_dict['roles'] if check_role_name(x['name']) ]
    if not roles_of_interest:
        return
    global role_id_name
    role_id_name = [ (role['id'], role['name']) for role in guild_json_dict['roles'] if role['name'] in roles_of_interest]

    role_users = {}
    role_channel_ids = [x['id'] for x in guild_json_dict['textChannels'] if 'role' in x['name'].lower()]
    # I should throw this into a loop so it reads all role channels
    # read channel
    # role_channel_id = 667877151894142990
    if debug:
        print(f'role channels: {role_channel_ids}')
    for role_channel_id in role_channel_ids:
        try:channel_filename = [x for x in os.listdir(subdir_fullpath) if str(x).startswith(f'channel_{role_channel_id}')][0]
        except IndexError:
            print(f'channel file for {role_channel_id} doesnt exist')
            continue
        channel_filepath = os.path.join(subdir_fullpath, channel_filename)
        with open(channel_filepath, 'r') as f:json_dict = json.load(f)

        # read msgs
        msgs = json_dict['messages']
        # msgs_of_interest = [x for x in msgs if roles_of_interest[0] in x['content'] or roles_of_interest[0] in '\n'.join([y['description'] for y in x['embeds']])]
        msgs_of_interest = [x for x in msgs if roles_of_interest[0] in msg_to_txt(x) or re.search(f'(:?(:?[^\w]|^)(?:{"|".join(gender_synonyms)})|gender|pronouns)([^\w]|$)', msg_to_txt(x), flags=re.IGNORECASE)]
        # msgs_of_interest = msgs

        if not msgs_of_interest:
            continue

        # read reactions
        # msgs = msgs_of_interest
        # msg = msgs_of_interest[0]
        # print('msg of interest: ', msg_to_txt(msg))
        # if str(guild_json_dict['id']).endswith('3312'):print(msg)
        try:
            if debug:print(f'reactions:', [x['emoji']['name'].strip('️') for x in msg['reactions']])
        except:pass
        print(f'from {guild_json_dict["name"]}')
        for msg in msgs:

            # find the msg of interest, and find the reaction related to each gender role
            # sometimes it may also be necessary to find the text connecting the reaction and the gender role
            for reaction in msg['reactions']:
                male, female = False, False
                # reaction = msg['reactions'][0]
                # 1 reaction at a time
                try:
                    # if it's a custom emote 'name' can be none
                    # in which case we'll set reaction_emote to the emote id instead
                    if reaction['emoji']['name']:
                        reaction_emote = reaction['emoji']['name'].strip('️')

                        # number emotes are common so we'll do handle them
                        numbers_emotes = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
                        numbers_strings = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
                        if reaction_emote in numbers_emotes:
                            reaction_emote = f':{numbers_strings[numbers_emotes.index(reaction_emote)]}:'
                    else:
                        reaction_emote = reaction['emoji']['id']
                except:
                    print(reaction)
                    continue

                # print(f'checking reaction {reaction_emote}')
                # simplify the code to work with genders
                if reaction_emote in mf:
                    male = reaction_emote == mf[0]
                    female = reaction_emote == mf[1]
                    associated_emote = reaction_emote
                elif [True for x in msg_to_txt(msg).splitlines() if f'{reaction_emote}' in x and re.search(f'([^\w]|^)(?:{"|".join(gender_synonyms)})([^\w]|$)', x, flags=re.IGNORECASE)]:
                    if [True for x in msg_to_txt(msg).splitlines() if f'{reaction_emote}' in x and re.search(f'([^\w]|^)(?:{"|".join(gender_synonyms[1::2])})([^\w]|$)', x, flags=re.IGNORECASE)]:
                        female=True
                    else:
                        male=True
                    # make it work with custom reactions too, such as <a:br_heart1:792727176050900992>
                    # where br_heart1 is the name and the number is the emote id, and <a: denotes a custom emote
                '''associated_role_name = [x for x in roles_of_interest if [y for y in re.split(r'[\n-]', msg_txt) if reaction_emote in y and x in y]]
                if associated_role_name:
                    associated_role_name=associated_role_name[0]
                else:
                    continue'''
                # get ids where id is a string
                if 'users' in reaction and (male or female):
                    print('from msg: ', msg_to_txt(msg))
                    if len(reaction['users']) > 10:  # if it has too few reactions it's worthless
                        print(f'reaction {reaction_emote} is {mf[0 if male else 1]}')
                        role_users[mf[0 if male else 1]] = {x['id'] for x in reaction['users']}

    # ignore users that have roles from more than 1 category
    # ignore_users = role_users['Female'].intersection(role_users['Male'])
    user_count = {}
    for role in role_users:
        for user in role_users[role]:
            if user not in user_count:
                user_count[user] = 0
            user_count[user] += 1

    ignore_users = {k for k,v in user_count.items() if v > 1}
    del user_count

    # users are the key, roles are the value
    user_roles = {}
    for role in role_users:
        for user in role_users[role]:
            user_roles[user] = role
    return user_roles


def read_guild(guild_filepath):

    # read guild
    with open(guild_filepath, 'r') as f:guild_json_dict = json.load(f)
    print(f'reading file {guild_filepath}: {guild_json_dict["name"]}')

    if not guild_json_dict["locale"].startswith("en"):  # only use english guilds
        return None

    guild_channel_ids = [x['id'] for x in guild_json_dict['textChannels']]
    guild_channel_filenames = [x for x in os.listdir(subdir_fullpath) if any([y for y in guild_channel_ids if str(x).startswith(f'channel_{y}')])]
    # if we dont have any of the channels then exit early
    if not guild_channel_filenames:
        print('we dont have the channels from that guild')
        return None

    user_roles = get_user_roles(guild_json_dict)
    if not user_roles:return None
    print(f'got stuff from {guild_filename}')

    # read guild messages and populate user_msgs
    user_msgs = {k: [] for k in user_roles.keys()}
    MIN_MSGS = 200
    # user_num_msgs = {k:0 for k in user_roles.keys()}
    for channel_filename in guild_channel_filenames:
        if debug:print(f'reading channel file {channel_filename}')
        with open(os.path.join(subdir_fullpath, channel_filename), 'r') as f:
            json_dict = json.load(f)
        if not re.search('bot(?:$|[^\w])', json_dict['channel']['name']):
            for msg in json_dict['messages']:
                read_msg(msg, user_roles, user_msgs)

    user_num_msgs = {k: len(v) for k, v in user_msgs.items()}
    for user, count in user_num_msgs.items():
        if count < MIN_MSGS:
            del user_msgs[user]

    # skip the first 5 msgs cause they might be intros and not provide valuable training data
    user_msgs = {k: v[5:] for k, v in user_msgs.items()}
    user_msgs = {k: '\n'.join(v[-500:]) for k, v in user_msgs.items()}

    print(f'got {len(user_msgs)} users')
    # remove the empty items
    return user_msgs, user_roles



def read_msg(msg, user_roles, user_msgs):
    author_id = msg['author']['id']
    if author_id not in user_roles:
        return

    # ignore bot commands and messages without txt
    if not re.match('\w', msg['content']):
        return

    # user_num_msgs[author_id] += 1
    # bert only allows for 512 tokens max so we dont want really long pieces of sample data
    if len(user_msgs[author_id]) > 800:
        return

    # we dont want msgs with only 1 or 2 words
    # if len(word_tokenize(msg['content'])) < 3:
    #     return
    user_msgs[author_id].append(msg['content'])


with open('guilds_gendered_org.json', 'r') as f:
    guilds_of_interest = list(json.load(f).keys())
print(f'got {len(guilds_of_interest)} guilds')

filenames = os.listdir(BASEDIR)
blacklisted_guild_filenames = ['guild_[303893525680881665].json']
# guild_filenames = [x for x in filenames if x.startswith('guild_') and 'members' not in x and x not in blacklisted_guild_filenames]

# limit it to reading from these guilds
# good_guilds = ['763124398046969897', '123315443208421377', '185735119657500673', '210510758105186304', '213856835369828355', '681133121655013426', '765620153853280307', '774148396575096832', '782670688904937483', '800036293039882280', '802997803361501204', '805184389997920287', '807684894847270913', '113555415446413312', '145365721398902784', '105753365916422144', '114211522384756737', '122905555386892290', '149167686159564800', '105766921034534912', '112180548834693120', '143843414171975680', '378599231583289346', '140878389312618496', '510987107087679508', '401524750922416130', '242328997063557122', '536053736246607897', '126127540350877696', '439884619383439360', '368233883193573377', '537333214293917697', '327260688860971009', '138241888439238656']
good_guilds = guilds_of_interest

# guild_filenames = [x for x in guild_filenames if '667870530698870804' in x]

user_msgs_final = {}
user_roles_cumulative = {}
num_guild_read = 0

for subdir in filenames:
    if subdir not in good_guilds:continue
    subdir_fullpath = os.path.join(BASEDIR, subdir)
    guild_filenames = [x for x in os.listdir(subdir_fullpath) if
                       x.startswith('guild_') and 'members' not in x and x not in blacklisted_guild_filenames]
    try:guild_filename = guild_filenames[0]
    except IndexError:
        print(f'guild {subdir} is missing the guild json')
        continue

    guild_filepath = os.path.join(subdir_fullpath, guild_filename)

    r = read_guild(guild_filepath)
    if r is None:continue
    user_msgs, user_roles = r
    if not user_msgs:continue  # we can get an empty response
    num_guild_read += 1

    # balance the data just a bit
    y_vals = []
    user_msgs_balanced = {}
    for k in user_msgs:
        # x_vals.append(v)
        y_vals.append(user_roles[k])
    roles_of_interest = set(y_vals)
    min_count = min([y_vals.count(role) for role in roles_of_interest]) * 2  # we can have 3 x as many of one gender as the other
    role_count = {k: 0 for k in roles_of_interest}
    for k, v in user_msgs.items():
        role = user_roles[k]
        if role_count[role] < min_count:
            role_count[role] += 1
            user_msgs_balanced[k] = v
    user_msgs = user_msgs_balanced
    # done balancing data

    for user, msgs in user_msgs.items():
        user_msgs_final[user] = msgs
    for user, roles in user_roles.items():
        user_roles_cumulative[user] = roles


print(f'read {num_guild_read} guilds')
print(f'got {len(user_msgs_final)} sample users')
with open('train_data_gendered.pkl', 'wb') as f:
    pickle.dump((user_msgs_final, user_roles_cumulative), f)
