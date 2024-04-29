import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import os

# Function to convert multiple DataFrames to an Excel file in memory


def to_excel(df_kept, df_drop, df_stats):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_kept.to_excel(writer, index=False, sheet_name='Kept')
        df_drop.to_excel(writer, index=False, sheet_name='Dropped')
        df_stats.to_excel(writer, index=False, sheet_name='Stats')
    return output.getvalue()


# Title of the Streamlit app
st.title('Organoïde Analysis App')

# File uploader allows the user to upload their excel file
uploaded_file = st.file_uploader("Choose a file", key="file_uploader")

# Slider for the threshold value
threshold_value = st.slider('Threshold value', 0, 500, 250)

# Function to process data


def process_data(uploaded_file, threshold_value):
    df = pd.read_excel(uploaded_file)

    columns_to_analyze = ['Area', 'Perim.', 'Feret',
                          'FeretX', 'FeretY', 'FeretAngle', 'MinFeret']
    df = df[columns_to_analyze]
    # Calculate the mean of the 'Feret' column
    mean_feret = df['Feret'].mean()

    # Filter rows
    df_kept = df[np.abs(df['Feret'] - mean_feret) < threshold_value]
    df_drop = df[~df.index.isin(df_kept.index)]
    df_stats = pd.DataFrame()

    for column in columns_to_analyze:
        df_stats[column] = {
            'Min': df_kept[column].min(),
            'Max': df_kept[column].max(),
            'Mean': df_kept[column].mean(),
            'Sample Standard Deviation': df_kept[column].std(ddof=1),
            'Standard Error of the Mean': df_kept[column].sem(),
            'N_values': df_kept[column].count()
        }

    df_stats = pd.DataFrame(df_stats).transpose()
    df_stats.reset_index(inplace=True)
    return df_kept, df_drop, df_stats


# Process button
if st.button('Process'):
    if uploaded_file is not None:
        df_kept, df_drop, df_stats = process_data(
            uploaded_file, threshold_value)
        st.session_state['df_kept'] = df_kept
        st.session_state['df_drop'] = df_drop
        st.session_state['df_stats'] = df_stats
        st.session_state['data_processed'] = True
    else:
        st.error('Please upload a file to process.')

if 'data_processed' in st.session_state and st.session_state['data_processed']:
    # Display the stats DataFrame as a preview
    st.dataframe(st.session_state['df_stats'])
    base_name, extension = os.path.splitext(uploaded_file.name)
    new_file_name = f"{base_name}_analysis.xlsx"
    # Button for downloading all DataFrames in one Excel file
    st.download_button(
        label="Download Result Excel File",
        data=to_excel(
            st.session_state['df_kept'], st.session_state['df_drop'], st.session_state['df_stats']),
        file_name=new_file_name,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
