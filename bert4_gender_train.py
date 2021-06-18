import os
import re
from sklearn.model_selection import train_test_split
import pickle
import time

with open('train_data_gendered.pkl', 'rb') as f:
    user_msgs, user_roles = pickle.load(f)


# just a little more preprocessing
# balance the data
x_vals, y_vals = [], []
for k in user_msgs:
    # x_vals.append(v)
    y_vals.append(user_roles[k])
roles_of_interest = set(y_vals)
min_count = min([y_vals.count(role) for role in roles_of_interest]) * 1

x_vals, y_vals = [], []
role_count = {k:0 for k in roles_of_interest}
for k, v in user_msgs.items():
    role = user_roles[k]
    if role_count[role] < min_count:
        role_count[role] += 1
        x_vals.append(v)
        y_vals.append(role)



X_train, X_test, y_train, y_test = train_test_split(x_vals, y_vals, test_size=0.1, random_state=42, shuffle=True)
print(f'training on {len(X_train)} items')
# training stuffs
import pandas as pd
import numpy as np

import ktrain
from ktrain import text

# set up ML tools
class_names = list(roles_of_interest)
(x_train,  y_train), (x_test, y_test), preproc = text.texts_from_array(x_train=X_train, y_train=y_train,
                                                                       x_test=X_test, y_test=y_test,
                                                                       class_names=class_names,
                                                                       preprocess_mode='bert',
                                                                       maxlen=512)


model = text.text_classifier('bert', train_data=(x_train, y_train), preproc=preproc)
learner = ktrain.get_learner(model, train_data=(x_train, y_train),
                             val_data=(x_test, y_test),
                             batch_size=6)

# learner.lr_find(max_epochs=100, suggest=True, show_plot=True)
# learner.lr_plot()

# Two possible suggestions for LR from plot:
# 	Min numerical gradient: 3.36E-07
# 	Min loss divided by 10: 2.09E-06
# do the training
learner.fit_onecycle(1e-5, 3)
# learner.fit_onecycle(5e-6, 8)
# learner.autofit(lr=2.09E-06)

# show accuracy
val_results = learner.validate(val_data=(x_test, y_test), class_names=class_names)

predictor = ktrain.get_predictor(learner.model, preproc)
# let's save the predictor for later use

# get the accuracy as an int
avg = lambda x: sum(x)/len(x)
acc_estimate = avg([x[i]/sum(x) for i, x in enumerate(val_results)]) * 100

predictor.save(f"models/bert_gender_try1_model_{int(time.time())}_{round(acc_estimate, 2)}")

