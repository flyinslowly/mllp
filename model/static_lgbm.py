import lightgbm as lgbm
import pickle
import json
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from feature_extraction import loan_struct_reader

ROOT = os.path.dirname(os.getcwd())
FILES_DIR = os.path.join(ROOT, "json_augmented")
MARKUPFILE = os.path.join(FILES_DIR, r"markupdict0-2000.pckl")


X, y = [], []
for file in os.listdir(FILES_DIR):
    if file.find("markupdict") != -1:
        with open(os.path.join(FILES_DIR, file), 'rb') as f:
            markupdict = pickle.load(f)
    else:
        _, options = loan_struct_reader.LoanStructReader().Read(os.path.join(FILES_DIR, file), returnOptions=True)
        X.append(options['irOptions_curve'])
        y.append(markupdict[file])
X = np.array(X)
y = np.array(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

model = lgbm.LGBMRegressor()
model.fit(X_train, y_train)

y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)
print("MAE On train:", mean_absolute_error(y_pred_train, y_train))
print("MAE On test:", mean_absolute_error(y_pred_test, y_test))
