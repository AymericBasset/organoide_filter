import streamlit as st
import pandas as pd
import numpy as np

# Title of the Streamlit app
st.title('Organoïde Analysis App')

# File uploader allows the user to upload their excel file
uploaded_file = st.file_uploader("Choose a file")

# Slider for the threshold value
threshold_value = st.slider('Threshold value', 0, 500, 250)

# Placeholder for the process button
process_button_placeholder = st.empty()

# Process button inside the placeholder
if process_button_placeholder.button('Process'):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        # Calculate the mean of the 'Feret (µm)' column
        mean_feret = df['Feret (µm)'].mean()

        # Filter rows where the absolute difference from the mean is less than threshold_value
        df_kept = df[np.abs(df['Feret (µm)'] - mean_feret) < threshold_value][['Organoïde', 'Area', 'Feret (µm)',
                                                                               'FeretX', 'FeretY', 'FeretAngle', 'MinFeret']]

        # Identify rows to drop (those not kept)
        df_drop = df[~df.index.isin(df_kept.index)][['Organoïde', 'Area', 'Feret (µm)',
                                                     'FeretX', 'FeretY', 'FeretAngle', 'MinFeret']]

        # Initialize an empty DataFrame to store statistics
        df_stats = pd.DataFrame()

        # Calculate statistics for specified columns
        columns_to_analyze = ['Area', 'Feret (µm)',
                              'FeretX', 'FeretY', 'FeretAngle', 'MinFeret']

        for column in columns_to_analyze:
            df_stats[column] = {
                'Min': df_kept[column].min(),
                'Max': df_kept[column].max(),
                'Mean': df_kept[column].mean(),
                'Sample Standard Deviation': df_kept['data_column'].std(ddof=1),
                'Standard Error of the Mean': df_kept[column].sem(),
                'N_values': df_kept[column].count()
            }

        # Convert dictionary to DataFrame for better readability
        df_stats = pd.DataFrame(df_stats).transpose()

        # Display the stats DataFrame as a preview
        st.dataframe(df_stats)
        # Remove the process button upon successful processing
        process_button_placeholder.empty()

        # Use columns to align download buttons on the same line
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(label="Kept Data", data=df_kept.to_csv().encode(
                'utf-8'), file_name='kept_data.csv', mime='text/csv')
        with col2:
            st.download_button(label="Dropped Data", data=df_drop.to_csv().encode(
                'utf-8'), file_name='dropped_data.csv', mime='text/csv')
        with col3:
            st.download_button(label="Stats Data", data=df_stats.to_csv().encode(
                'utf-8'), file_name='stats_data.csv', mime='text/csv')

        st.success('Processing complete. Download the files below.')
    else:
        st.error('Please upload a file to process.')
