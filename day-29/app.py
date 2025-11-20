import sys
from statistics import linear_regression

import gradio as gr
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os
saved_model_dir=""

scaler=joblib.load(os.path.join(saved_model_dir,"scaler.pkl"))
linear_regression=joblib.load(os.path.join(saved_model_dir,"linear_model.pkl"))
logistic_regression=joblib.load(os.path.join(saved_model_dir,"logistic_model.pkl"))
poly_regression=joblib.load(os.path.join(saved_model_dir,"polynomial_reg_model.pkl"))
rf_classifier=joblib.load(os.path.join(saved_model_dir,"rf_classifier.pkl"))
def pred_air_quality_index(pm25, pm10, no2, co, temp, humidity):
    input_scaled=pd.DataFrame(scaler.fit_transform([[pm25, pm10, no2, co, temp, humidity]]),columns=['PM2.5', 'PM10', 'NO2', 'CO', 'Temperature', 'Humidity'])
    linear_pred=linear_regression.predict(input_scaled)[0]
    poly_pred=poly_regression.predict(input_scaled)[0]

    random_forest_pred=rf_classifier.predict(input_scaled)[0]
    log_pred = logistic_regression.predict(input_scaled)[0]

  # Create performance plot
    models = ["Linear", "Polynomial"]
    predictions = [linear_pred, poly_pred]
    plt.figure(figsize=(8, 4))
    sns.barplot(x=models, y=predictions)
    plt.title("AQI Predictions by Model")
    plt.ylabel("Predicted AQI")
    plt.savefig("aqi_plot.png")
    plt.close()

    output_text = (
        f"Linear Regression AQI: {linear_pred:.2f}\n"
        f"Polynomial Regression AQI: {poly_pred:.2f}\n"
        f"Logistic Classification: {'Safe' if log_pred == 0 else 'Unsafe'}\n"
        f"Random Forest Classification: {'Safe' if random_forest_pred == 0 else 'Unsafe'}"
    )

    return output_text, "aqi_plot.png"
if __name__=='__main__':
    iface = gr.Interface(
        fn=pred_air_quality_index,
        inputs=[
            gr.Slider(0, 200, label="PM2.5(µg/m³)", value=50),
            gr.Slider(0, 300, label="PM10 (µg/m³)", value=80),
            gr.Slider(0, 100, label="NO2 (µg/m³)", value=20),
            gr.Slider(0, 10, label="CO (mg/m³)", value=1),
            gr.Slider(-10, 40, label="Temperature (°C)", value=20),
            gr.Slider(0, 100, label="Humidity (%)", value=50)
        ],
        outputs=[
            gr.Textbox(label="Predictions"),
            gr.Image(label="Model Comparison Plot")
        ],
        title="Air Quality Prediction and Classification",
        description="Enter pollutant levels and weather conditions to predict AQI and classify air quality. Built with multiple machine learning models to address urban air pollution."
    )

    iface.launch()
