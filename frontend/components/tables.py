"""Reusable table components."""

import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any


def data_table(
    df: pd.DataFrame,
    key: str = "table",
    width: str = "stretch"
) -> None:
    """Create a simple data table.

    Args:
        df: DataFrame to display
        key: Unique key for the table
        width: Width of the table ('stretch' or 'content')
    """
    st.dataframe(df, width=width, key=key)
