import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Advanced Data Dashboard", layout="wide")
st.title("📊 Advanced Data Exploration Dashboard")

uploaded_file = st.file_uploader("📤 Upload CSV or Excel file", type=["csv", "xlsx"])

def get_dtype_dropdown(col, dtype):
    options = ['object', 'int64', 'float64', 'bool', 'datetime64[ns]']
    return st.selectbox(f"Data type for {col}", options, index=options.index(str(dtype)), key=col)

if uploaded_file:
    try:
        # Load data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded!")

        st.subheader("📋 Data Summary")
        summary = pd.DataFrame({
            "Column": df.columns,
            "Data Type": [df[col].dtype for col in df.columns],
            "Null Count": df.isnull().sum(),
            "Null %": df.isnull().mean().round(3) * 100,
            "Unique Values": df.nunique()
        }).reset_index(drop=True)

        st.dataframe(summary)

        st.markdown("### ✏️ Modify Data Types")
        with st.expander("Change Column Data Types"):
            for col in df.columns:
                new_dtype = get_dtype_dropdown(col, df[col].dtype)
                try:
                    df[col] = df[col].astype(new_dtype)
                except Exception:
                    st.warning(f"Could not convert {col} to {new_dtype}")

        st.markdown("---")

        # Univariate Analysis
        st.subheader("📈 Univariate Analysis")
        uni_col = st.selectbox("Select column", df.columns)
        uni_plot = st.radio("Plot Type", ["Box", "Line", "Distribution"], horizontal=True)

        if uni_plot == "Box":
            fig = px.box(df, y=uni_col)
        elif uni_plot == "Line":
            fig = px.line(df, y=uni_col)
        else:
            fig = px.histogram(df, x=uni_col)

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Bivariate Analysis
        st.subheader("🔄 Bivariate Analysis")

        all_cols = df.columns.tolist()
        num_date_cols = df.select_dtypes(include=['number', 'datetime']).columns.tolist()
        cat_cols = df.select_dtypes(exclude=['number', 'datetime']).columns.tolist()

        x_axis = st.selectbox("X-axis column", all_cols)
        y_axis = st.selectbox("Y-axis column (numeric/date only)", num_date_cols)
        legend_col = st.selectbox("Legend (categorical)", cat_cols + [None], index=0)

        bi_plot = st.radio("Chart Type", ["Table", "Box", "Line"], horizontal=True)

        if bi_plot == "Table":
            st.dataframe(df[[x_axis, y_axis]].describe())
        elif bi_plot == "Box":
            fig = px.box(df, x=x_axis, y=y_axis, color=legend_col if legend_col else None)
        else:
            fig = px.line(df, x=x_axis, y=y_axis, color=legend_col if legend_col else None)

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("📥 Upload a file to begin analysis.")
