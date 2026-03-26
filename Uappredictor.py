# --- Load Data From Local CSV File ---
@st.cache_data
def load_local_nuforc_dataset(filepath="nuforc_reports.csv"):
    """
    Loads the full NUFORC dataset from a local CSV file.
    You must download this file and place it in the same directory as your script.
    A good source is the data.world dataset by Tim Renner.
    """
    try:
        df = pd.read_csv(filepath)
        # --- Data Cleaning (similar to before) ---
        df.columns = df.columns.str.strip()
        # Handle potential variations in column names
        if 'date_time' in df.columns:
            df['Event Date'] = pd.to_datetime(df['date_time'], errors='coerce')
        elif 'Date / Time' in df.columns:
             df['Event Date'] = pd.to_datetime(df['Date / Time'].str.split(' ').str[0], errors='coerce')
        else:
            st.error("Dataset must contain a 'date_time' or 'Date / Time' column.")
            return None

        df.dropna(subset=['Event Date', 'city', 'state'], inplace=True)
        df['location'] = df['city'].str.strip() + ", " + df['state'].str.strip()
        return df
    except FileNotFoundError:
        st.error(f"Fatal Error: The data file '{filepath}' was not found.")
        st.info("Please download the NUFORC CSV dataset and place it in the same directory as this script. A recommended source is the NUFORC UFO Reports dataset on data.world or Kaggle.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the dataset: {e}")
        return None

# In the main part of your script, replace the old function call:
# nuforc_df = load_stable_nuforc_dataset()
#...with the new one:
# nuforc_df = load_local_nuforc_dataset()
