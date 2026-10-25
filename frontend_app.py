import streamlit as st
import requests
import pandas as pd
import json

# Configure Streamlit page layout and title
st.set_page_config(page_title="SuperKart Sales Forecaster", layout="wide")

st.title("🛒 SuperKart Store Sales Forecasting Solution")
st.write("""
Welcome to the SuperKart Sales Forecasting Application. 
Use the sidebar or the interactive fields below to estimate the quarterly sales of a product in a given store.
""")

# Sidebar config for backend API URL
st.sidebar.header("⚙️ Connection Settings")
backend_url = st.sidebar.text_input(
    "Flask API URL", 
    value="http://backend:7860", 
    help="Provide the URL of the running Flask microservice."
)

# Tabs for Single Online Prediction and Batch Prediction
tab1, tab2 = st.tabs(["🔮 Single Product Prediction", "📂 Batch CSV Prediction"])

with tab1:
    st.subheader("Enter Product & Store Attributes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        product_mrp = st.number_input("Product MRP ($)", min_value=1.0, max_value=500.0, value=147.0, step=0.1)
        product_weight = st.number_input("Product Weight (g)", min_value=1.0, max_value=50.0, value=12.5, step=0.1)
        product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        
    with col2:
        allocated_area = st.number_input("Allocated Display Area Ratio", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
        store_size = st.selectbox("Store Size", ["Medium", "High", "Small"])
        store_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
        
    with col3:
        store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
        product_char = st.selectbox("Product Type Code Prefix", ["FD", "NC", "DR"])
        store_age = st.slider("Store Age (Years)", min_value=1, max_value=50, value=15)
        product_category = st.selectbox("Product Perishability Category", ["Perishables", "Non Perishables"])

    # JSON Payload creation
    payload = {
        "Product_Weight": float(product_weight),
        "Product_Sugar_Content": product_sugar,
        "Product_Allocated_Area": float(allocated_area),
        "Product_MRP": float(product_mrp),
        "Store_Size": store_size,
        "Store_Location_City_Type": store_city_type,
        "Store_Type": store_type,
        "Product_Id_char": product_char,
        "Store_Age_Years": int(store_age),
        "Product_Type_Category": product_category
    }
    
    if st.button("🔮 Forecast Product Store Sales", type="primary"):
        try:
            with st.spinner("Querying predictive microservice..."):
                response = requests.post(f"{backend_url}/v1/predict", json=payload, timeout=10)
                
            if response.status_code == 200:
                result = response.json()
                predicted_sales = result.get("prediction", 0.0)
                st.success(f"### 🎉 Predicted Store Sales Total: **${predicted_sales:,.2f}**")
            else:
                st.error(f"Backend API Error: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend microservice at {backend_url}. Error: {str(e)}")

with tab2:
    st.subheader("Bulk Forecasting via CSV Upload")
    st.write("Upload a CSV file containing your product records to generate predictions.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("🔍 **Uploaded Data Preview:**", df.head())
        
        if st.button("⚡ Generate Bulk Forecasts", type="primary"):
            try:
                # Rewind file to start for transmission
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.read(), "text/csv")}
                
                with st.spinner("Sending bulk request to API..."):
                    response = requests.post(f"{backend_url}/v1/predictbatch", files=files, timeout=30)
                
                if response.status_code == 200:
                    predictions_dict = response.json()
                    # Map predictions back to the original DataFrame
                    df["Predicted_Product_Store_Sales_Total"] = df.index.map(lambda x: predictions_dict.get(str(x)))
                    
                    st.success("### ✅ Bulk Predictions Completed Successfully!")
                    st.dataframe(df)
                    
                    # Download option for completed dataframe
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Predicted Sales CSV",
                        data=csv_data,
                        file_name="SuperKart_Sales_Predictions.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"Backend API Error: {response.text}")
            except Exception as e:
                st.error(f"Could not reach backend microservice. Error: {str(e)}")
