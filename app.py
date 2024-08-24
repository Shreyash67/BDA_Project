from flask import Flask, request, render_template, jsonify
import numpy as np
import pickle
from pymongo.mongo_client import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)

# Update the path to your saved model
model_path = 'H:\\BDA_Project\\best_model\\RandomForestClassifier.pkl'
model = pickle.load(open(model_path, 'rb'))

uri = "mongodb+srv://waralkarshayu:shreyash12345@cluster0.etki8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except ServerSelectionTimeoutError as e:
    print(f"Failed to connect to MongoDB: {e}")

db = client["mydatabase"]   
collection = db["New_database"]

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == "GET":
        return render_template("index.html")
    else:
        try:
            features = [int(x) for x in request.form.values()]

            # Re-arranging the list as per dataset
            feature_list = [features[4]] + features[:4] + features[5:11][::-1] + features[11:17][::-1] + features[17:][::-1]
            features_arr = [np.array(feature_list)]

            prediction = model.predict(features_arr)

            print(features_arr)
            # Prepare data for MongoDB
            New_database = {
                'Gender': features[0],
                'Education': features[1],
                'Marital Status': features[2],
                'Age': features[3],
                'Limit Balance': features[4],
                'PAY_0': features[5],
                'PAY_2': features[6],
                'PAY_3': features[7],
                'PAY_4': features[8],
                'PAY_5': features[9],
                'PAY_6': features[10],
                'BILL_AMT1': features[11],
                'BILL_AMT2': features[12],
                'BILL_AMT3': features[13],
                'BILL_AMT4': features[14],
                'BILL_AMT5': features[15],
                'BILL_AMT6': features[16],
                'PAY_AMT1': features[17],
                'PAY_AMT2': features[18],
                'PAY_AMT3': features[19],
                'PAY_AMT4': features[20],
                'PAY_AMT5': features[21],
                'PAY_AMT6': features[22],
                'Prediction': prediction[0]
            }
            collection.insert_one(New_database)

            print("Prediction value: ", prediction)

            result = ""
            if prediction[0] == 1:
                result = "The credit card holder will be a defaulter in the next month."
            else:
                result = "The credit card holder will not be a defaulter in the next month."

            return render_template('index.html', prediction_text=result)
        except Exception as e:
            print(f"Error during prediction: {e}")
            return render_template('index.html', prediction_text="An error occurred during prediction.")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
