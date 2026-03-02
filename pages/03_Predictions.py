from predictive.engine import train_demo_model, features_from_harmonics, _mags_to_harmonics_df
import pandas as pd

df = st.session_state.get("quakes")
# build X, y …
train_demo_model(pd.DataFrame(X), pd.Series(y))
