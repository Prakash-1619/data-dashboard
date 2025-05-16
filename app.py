import streamlit as st
import pandas as pd
import plotly.express as px
import re
import requests
import io

st.set_page_config(page_title="Multi-File Data Dashboard", layout="wide")
st.title("📁 Multi-Source Data Exploration Dashboard")

# === Google Drive File Input ===
st.header("📥 Load File from Google Drive (Public Link Only)")
gdrive_url = st.text_input("Paste a public Google Drive file link")

def load_from_gdrive(link):
    file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', link)
    if not file_id_match:
        st.warning("⚠️ Invalid Drive link. Use format: https://drive.google.com/file/d/<FILE_ID>/view")
        return None

    file_id = file_id_match.group(1)
    direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    try:
        response = requests.get(direct_url)
        if response.status_code != 200:
            st.error("❌ Failed to download file from Google Drive.")
            return None

        content = io.BytesIO(response.content)
        try:
            return pd.read_csv(content)
        except:
            return pd.read_excel(content)

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        return None

if gdrive_url:
    df = load_from_gdrive(gdrive_url)
    if df is not None:
        st.success("✅ File loaded from Google Drive successfully!")
        uploaded_files = [("GoogleDriveFile", df)]
    else:
        uploaded_files = []
else:
    # === File Uploader ===
    uploaded_files_list = st.file_uploader(
        "📤 Upload CSV or Excel files (Max 10 GB each)",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )
    uploaded_files = []
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

# === Main Analysis Loop ===
for idx, (file_name, df) in enumerate(uploaded_files):
    st.markdown(f"## 📄 File: {file_name}")

    # Drop Columns
    st.subheader("🧹 Drop Columns")
    drop_cols = st.multiselect("Select columns to drop", df.columns, key=f"drop_{idx}")
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True)
        st.success(f"Dropped: {', '.join(drop_cols)}")

    # Data Preview
    with st.expander("🔍 Preview Data"):
        st.dataframe(df)

    # Summary Table
    st.subheader("📋 Data Summary")
    summary = pd.DataFrame({
        "Column": df.columns,
        "Data Type": [df[col].dtype for col in df.columns],
        "Null Count": df.isnull().sum(),
        "Null %": df.isnull().mean().round(3) * 100,
        "Unique Values": df.nunique()
    }).reset_index(drop=True)
    st.dataframe(summary)

    st.markdown("---")

    # === Univariate Analysis ===
    st.subheader("📊 Univariate Analysis")
    uni_col = st.selectbox("Select column for univariate analysis", df.columns, key=f"uni_col_{idx}")
    uni_plot = st.radio("Plot type", ["Box Plot", "Histogram", "Line Plot", "Distribution"], horizontal=True, key=f"uni_plot_{idx}")

    if pd.api.types.is_numeric_dtype(df[uni_col]):
        if uni_plot == "Box Plot":
            fig = px.box(df, y=uni_col)
        elif uni_plot == "Histogram":
            fig = px.histogram(df, x=uni_col)
        elif uni_plot == "Line Plot":
            fig = px.line(df, y=uni_col)
        else:
            fig = px.histogram(df, x=uni_col)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Please select a numeric column for this plot.")

    st.markdown("---")

    # === Bivariate Analysis ===
    st.subheader("🔄 Bivariate Analysis")
    numeric_date_cols = df.select_dtypes(include=["number", "datetime64"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    x_col = st.selectbox("X-axis column", df.columns, key=f"xcol_{idx}")
    y_col = st.selectbox("Y-axis column (numeric/date)", numeric_date_cols, key=f"ycol_{idx}")
    legend_col = st.selectbox("Legend (categorical)", categorical_cols, key=f"legend_{idx}", index=0 if categorical_cols else None)

    plot_type = st.radio("Chart type", ["Table", "Box Plot", "Line Plot"], horizontal=True, key=f"bivar_plot_{idx}")

    if plot_type == "Table":
        st.dataframe(df[[x_col, y_col]].dropna())
    elif plot_type == "Box Plot":
        fig = px.box(df, x=x_col, y=y_col, color=legend_col)
        st.plotly_chart(fig, use_container_width=True)
    elif plot_type == "Line Plot":
        fig = px.line(df, x=x_col, y=y_col, color=legend_col)
        st.plotly_chart(fig, use_container_width=True)
