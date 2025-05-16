import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Dashboard", layout="wide")

st.title("📊 Data Exploration Dashboard")

# Upload file
uploaded_file = st.file_uploader(
    "📤 Upload your CSV or Excel file (Max: 5 GB)",
    type=["csv", "xlsx"]
)

if uploaded_file:
    try:
        # Load data
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded and loaded successfully!")

        # Show preview
        with st.expander("🔍 Preview Data"):
            st.dataframe(df)

        # Column types
        with st.expander("📌 Column Data Types"):
            st.dataframe(
                df.dtypes.reset_index()
                  .rename(columns={"index": "Column", 0: "Data Type"})
            )

        # Missing values
        with st.expander("⚠️ Missing Values Count"):
            st.dataframe(
                df.isnull().sum().reset_index()
                  .rename(columns={"index": "Column", 0: "Missing Values"})
            )

        # Unique values
        with st.expander("🔢 Unique Value Count"):
            st.dataframe(
                df.nunique().reset_index()
                  .rename(columns={"index": "Column", 0: "Unique Values"})
            )

        st.markdown("---")

        # 📊 Univariate
        st.subheader("📈 Univariate Analysis")
        selected_uni_col = st.selectbox("Select column for univariate analysis", df.columns)
        uni_plot_type = st.radio("Plot type", ["Box Plot", "Histogram"], horizontal=True)

        if uni_plot_type == "Box Plot":
            fig_uni = px.box(df, y=selected_uni_col)
        else:
            fig_uni = px.histogram(df, x=selected_uni_col)

        st.plotly_chart(fig_uni, use_container_width=True)

        st.markdown("---")

        # 🔁 Bivariate
        st.subheader("🔄 Bivariate Analysis")
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("Select X-axis column", df.columns, key="x")
        with col2:
            y_col = st.selectbox("Select Y-axis column", df.columns, key="y")

        bivar_type = st.radio("Choose chart type", ["Table", "Box Plot", "Distribution"], horizontal=True)

        if bivar_type == "Table":
            st.dataframe(df[[x_col, y_col]])
        elif bivar_type == "Box Plot":
            fig_bi = px.box(df, x=x_col, y=y_col)
            st.plotly_chart(fig_bi, use_container_width=True)
        else:  # Distribution
            fig_bi = px.histogram(df, x=x_col, color=y_col)
            st.plotly_chart(fig_bi, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error reading the file: {e}")
else:
    st.info("📝 Upload a CSV or Excel file to start analysis.")
