import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
# import tensorflow as tf
from datetime import timedelta
from datetime import datetime as dt
# from tensorflow.keras.models import load_model


# Load model (Change working directory to correct path pls)
# model = load_model("C:/Users/Wesse/PycharmProjects/BEP/src/graphs/LSTM_Mag2.h5")

# Function to create time sequences
def split_sequence(sequence, n_steps):
    X, y = list(), list()
    for i in range(len(sequence)):
        end_ix = i + n_steps
        if end_ix > len(sequence)-1:
            break
        seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)

def prediction_graph(data, option, min_mag, n_clusters, colorscale, location):
    if option is None:
        return {}

    if option == "Line":
        # Load data and prepare for model
        df = pd.DataFrame()
        df['long'] = [item['geometry']['coordinates'][0] for item in data]
        df['lat'] = [item['geometry']['coordinates'][1] for item in data]
        df['mag'] = [item['properties']['mag'] for item in data]
        df['time'] = [dt.fromtimestamp(item['properties']['time'] / 1000) for item in data]

        df.set_index(df['time'], inplace=True)
        df_agg = df.set_index("time").groupby(pd.Grouper(freq="4h")).mean()
        df_mag = df_agg['mag'].to_frame().dropna()
        x_array = df_mag.to_numpy()

        # Create the data for model
        X_test, y_test = split_sequence(x_array, 42)

        # Model predictions
        #model = load_model("LSTM_Mag2.h5")
        yhat = model.predict(X_test)

        # add None values to yhat to match seq lengths
        while len(yhat) < len(df_agg):
            yhat = np.insert(yhat, 0, None, axis=0)

        # Add predictions to dataframe
        df_agg['pred'] = yhat


        # Predict 1 full day ahead (6 time blocks of 4h = 24h)
        predictions = []
        for i in range(6):
            # Making room for predictions in df
            df_agg = df_agg.append(pd.Series(name=df_agg.index[-1] + timedelta(hours=4)))
            y_next = model.predict(X_test[-1].reshape(1, 42, 1))
            predictions.append(y_next)
            X_test_new = X_test[-1][1:]
            X_test[-1] = np.r_[X_test_new, y_next]

        mag_list = df_agg['pred'].to_numpy()
        mag_list = np.append(mag_list[0:-6], predictions)

        df_agg['pred'] = mag_list

        # Build figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_agg.index, y=df_agg['mag'],
                                 mode='lines',
                                 name='Real magnitude'))
        fig.add_trace(go.Scatter(x=df_agg.index, y=df_agg['pred'],
                                 mode='lines',
                                 name='Predicted magnitude'))

        fig.update_layout(legend=dict(x=0.5, y=1))
        fig.update_layout(yaxis_title='Magnitude (M)',
                          xaxis_title='Timeline')

        return fig
    return {}