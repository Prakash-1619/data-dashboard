import streamlit as st
import pandas as pd
import plotly.express as px
import re
import requests
import io

st.set_page_config(page_title="Multi-File Data Dashboard", layout="wide")
st.title("📁 Multi-Source Data Exploration Dashboard")

# --- Function to load from Google Drive shared link ---
def load_from_gdrive_shared_link(link):
    # Extract file ID from link formats
    match = re.search(r'd/([a-zA-Z0-9_-]+)', link)
    if not match:
        match = re.search(r'id=([a-zA-Z0-9_-]+)', link)
    if not match:
        st.warning("⚠️ Invalid Google Drive link.")
        return None, None

    file_id = match.group(1)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    try:
        response = requests.get(download_url)
        if response.status_code != 200:
            st.error("❌ Failed to fetch file from Google Drive.")
            return None, None

        file_bytes = io.BytesIO(response.content)

        # Try reading CSV first
        try:
            df = pd.read_csv(file_bytes)
            file_type = "csv"
        except Exception:
            file_bytes.seek(0)
            df = pd.read_excel(file_bytes)
            file_type = "excel"

        return df, file_type

    except Exception as e:
        st.error(f"❌ Error reading file from Google Drive: {e}")
        return None, None


# --- Google Drive Input ---
st.header("📥 Load File from Google Drive (Public Link Only)")
gdrive_url = st.text_input("Paste a Google Drive shared file link here:")

uploaded_files = []

if gdrive_url:
    df, filetype = load_from_gdrive_shared_link(gdrive_url)
    if df is not None:
        st.success(f"✅ File loaded from Google Drive successfully ({filetype.upper()})!")
        uploaded_files = [("GoogleDriveFile", df)]

# --- File Uploader (multiple) ---
if not uploaded_files:
    uploaded_files_list = st.file_uploader(
        "📤 Upload CSV or Excel files (Max 10 GB each)",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )
    if uploaded_files_list:
        for uploaded_file in uploaded_files_list:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                uploaded_files.append((uploaded_file.name, df))
            except Exception as e:
                st.error(f"❌ Error loading {uploaded_file.name}: {e}")

# --- For each uploaded file do analysis ---
for idx, (file_name, df) in enumerate(uploaded_files):
    st.markdown(f"## 📄 File: {file_name}")

    # Drop columns option
    st.subheader("🧹 Drop Columns")
    drop_cols = st.multiselect("Select columns to drop", df.columns, key=f"drop_{idx}")
    if drop_cols:
        df = df.drop(columns=drop_cols)
        st.success(f"Dropped columns: {', '.join(drop_cols)}")

    # Preview data
    with st.expander("🔍 Preview Data"):
        st.dataframe(df)

    # Summary table
    st.subheader("📋 Data Summary")
    summary = pd.DataFrame({
        "Column": df.columns,
        "Data Type": [str(df[col].dtype) for col in df.columns],
        "Null Count": df.isnull().sum().values,
        "Null %": (df.isnull().mean().values * 100).round(2),
        "Unique Values": df.nunique().values
    })
    st.dataframe(summary)

    st.markdown("---")

    # Univariate Analysis
    st.subheader("📊 Univariate Analysis")
    uni_col = st.selectbox("Select column for univariate analysis", df.columns, key=f"uni_col_{idx}")
    uni_plot = st.radio("Plot type", ["Box Plot", "Histogram", "Line Plot", "Distribution"], horizontal=True, key=f"uni_plot_{idx}")

    if pd.api.types.is_numeric_dtype(df[uni_col]) or pd.api.types.is_datetime64_any_dtype(df[uni_col]):
        if uni_plot == "Box Plot":
            fig = px.box(df, y=uni_col)
        elif uni_plot == "Histogram" or uni_plot == "Distribution":
            fig = px.histogram(df, x=uni_col)
        elif uni_plot == "Line Plot":
            fig = px.line(df, y=uni_col)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Select a numeric or datetime column for this plot.")

    st.markdown("---")

    # Bivariate Analysis
    st.subheader("🔄 Bivariate Analysis")
    numeric_date_cols = df.select_dtypes(include=["number", "datetime64"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    x_col = st.selectbox("X-axis column (any type)", df.columns, key=f"xcol_{idx}")
    if numeric_date_cols:
        y_col = st.selectbox("Y-axis column (numeric/date only)", numeric_date_cols, key=f"ycol_{idx}")
    else:
        y_col = None

    legend_col = None
    if categorical_cols:
        legend_col = st.selectbox("Legend (categorical columns)", [None] + categorical_cols, key=f"legend_{idx}")

    plot_type = st.radio("Chart type", ["Table", "Box Plot", "Line Plot"], horizontal=True, key=f"bivar_plot_{idx}")

    if plot_type == "Table":
        cols = [c for c in [x_col, y_col] if c is not None]
        st.dataframe(df[cols].dropna())
    elif plot_type == "Box Plot":
        if y_col is not None:
            fig = px.box(df, x=x_col, y=y_col, color=legend_col)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Y-axis column is required for Box Plot.")
    elif plot_type == "Line Plot":
        if y_col is not None:
            fig = px.line(df, x=x_col, y=y_col, color=legend_col)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Y-axis column is required for Line Plot.")
