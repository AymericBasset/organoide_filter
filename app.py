import streamlit as st
import pandas as pd
import numpy as np

# Title of the Streamlit app
st.title('Organoïde Analysis App')

# File uploader allows the user to upload their excel file
uploaded_file = st.file_uploader("Choose a file")

# Slider for the threshold value
threshold_value = st.slider('Threshold value', 0, 500, 250)

# Function to process data


def process_data(uploaded_file, threshold_value):
    df = pd.read_excel(uploaded_file)

    # Calculate the mean of the 'Feret (µm)' column
    mean_feret = df['Feret (µm)'].mean()

    # Filter rows where the absolute difference from the mean is less than threshold_value
    df_kept = df[np.abs(df['Feret (µm)'] - mean_feret) < threshold_value][['Organoïde', 'Area', 'Feret (µm)',
                                                                           'FeretX', 'FeretY', 'FeretAngle', 'MinFeret']]
    df_drop = df[~df.index.isin(df_kept.index)][['Organoïde', 'Area', 'Feret (µm)',
                                                 'FeretX', 'FeretY', 'FeretAngle', 'MinFeret']]
    df_stats = pd.DataFrame()

    columns_to_analyze = [
        'Area', 'Feret (µm)', 'FeretX', 'FeretY', 'FeretAngle', 'MinFeret']
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
    return df_kept, df_drop, df_stats


# Placeholder for the process button
if 'data_processed' not in st.session_state or not st.session_state['data_processed']:
    process_button_placeholder = st.empty()
    if process_button_placeholder.button('Process'):
        if uploaded_file is not None:
            df_kept, df_drop, df_stats = process_data(
                uploaded_file, threshold_value)
            st.session_state['df_kept'] = df_kept
            st.session_state['df_drop'] = df_drop
            st.session_state['df_stats'] = df_stats
            st.session_state['data_processed'] = True
            process_button_placeholder.empty()
        else:
            st.error('Please upload a file to process.')

if 'data_processed' in st.session_state and st.session_state['data_processed']:
    # Display the stats DataFrame as a preview
    st.dataframe(st.session_state['df_stats'])

    # Use columns to align download buttons on the same line
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(label="Kept Data", data=st.session_state['df_kept'].to_csv(
        ).encode('utf-8'), file_name='kept_data.csv', mime='text/csv')
    with col2:
        st.download_button(label="Dropped Data", data=st.session_state['df_drop'].to_csv(
        ).encode('utf-8'), file_name='dropped_data.csv', mime='text/csv')
    with col3:
        st.download_button(label="Stats Data", data=st.session_state['df_stats'].to_csv(
        ).encode('utf-8'), file_name='stats_data.csv', mime='text/csv')

    st.success('Processing complete. Download the files below.')
