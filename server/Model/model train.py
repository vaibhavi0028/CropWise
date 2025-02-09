import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
import requests
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Concatenate
from tensorflow.keras.optimizers import Adam

# Load the CSV file
data = pd.read_csv("/content/Final.csv").fillna(method='ffill')

columns = [
    'soil_moisture', 'N', 'P', 'K', 'soil_pH', 'temperature', 'humidity',
    'rainfall', 'sunlight_hours', 'last_crop', 'land_size', 'location',
    'crop', 'optimal_N', 'optimal_P', 'optimal_K', 'optimal_pH_min',
    'optimal_pH_max', 'expected_yield'
]

features = [
    'soil_moisture', 'N', 'P', 'K', 'soil_pH', 'temperature',
    'humidity', 'rainfall', 'sunlight_hours', 'last_crop', 'land_size'
]
X = pd.get_dummies(data[features], columns=['last_crop'])
y = data['crop']

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Standardize numerical features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# Hybrid Model Architecture
def create_hybrid_model(input_shape, num_classes):
    ann_input = Input(shape=(input_shape,))
    ann = Dense(256, activation='relu')(ann_input)
    ann = Dense(128, activation='relu')(ann)

    xgb_input = Input(shape=(input_shape,))

    combined = Concatenate()([ann, xgb_input])
    output = Dense(num_classes, activation='softmax')(combined)

    model = Model(inputs=[ann_input, xgb_input], outputs=output)
    model.compile(optimizer=Adam(0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# Train models
xgb_model = xgb.XGBClassifier(objective='multi:softprob', n_estimators=150)
xgb_model.fit(X_train, y_train)

hybrid_model = create_hybrid_model(X_train.shape[1], len(le.classes_))
hybrid_model.fit([X_train, X_train], y_train, validation_data=([X_test, X_test], y_test), epochs=30, batch_size=64, verbose=0)
import joblib
import pickle
import tensorflow as tf

# Save XGBoost model
joblib.dump(xgb_model, "xgb_model.pkl")

# Save Label Encoder for later decoding
joblib.dump(le, "label_encoder.pkl")

# Save Standard Scaler for preprocessing new inputs
joblib.dump(scaler, "scaler.pkl")

# Save Hybrid ANN-XGBoost model
hybrid_model.save("hybrid_model.h5")

y_pred = np.argmax(hybrid_model.predict([X_test, X_test]), axis=1)
print(f"\nModel Accuracy: {accuracy_score(y_test, y_pred):.2f}")