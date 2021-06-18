import ktrain
from ktrain import text
import json
import re

def read_msg(msg, user_msgs):
    author_id = msg['author']['name'] + '#' + msg['author']['discriminator']
    if author_id not in user_msgs:user_msgs[author_id] = []

    # ignore bot commands and messages without txt
    if not re.match('\w', msg['content']):
        return

    # user_num_msgs[author_id] += 1
    # bert only allows for 512 tokens max so we dont want really long pieces of sample data
    if len(user_msgs[author_id]) > 800:
        return
    user_msgs[author_id].append(msg['content'])


predictor = ktrain.load_predictor('bert_gender_model')
filepath = 'The Crew.json'

msgs = json.load(open(filepath, 'r', encoding='utf-8'))['messages']
user_msgs = {}
for msg in msgs:read_msg(msg, user_msgs)
MIN_MSGS = 100


user_num_msgs = {k: len(v) for k, v in user_msgs.items()}
for user, count in user_num_msgs.items():
    if count < MIN_MSGS:
        del user_msgs[user]

user_msgs = {k: v[5:] for k, v in user_msgs.items()}
user_msgs = {k: '\n'.join(v[-500:]) for k, v in user_msgs.items()}

print(f'got {len(user_msgs)} users')

for user, users_msgs in user_msgs.items():
    prediction = predictor.predict(users_msgs, return_proba=True)
    prediction_class = predictor.get_classes()[prediction.argmax()]
    prediction_certainty = '{:.0f}%'.format(prediction[prediction.argmax()] * 100)
    print(user, prediction_class, prediction_certainty)
