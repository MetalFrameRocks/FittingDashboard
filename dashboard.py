# import streamlit as st
# from google.cloud import firestore
# from google.oauth2 import service_account
# import pandas as pd
# import plotly.express as px
# import pytz
# import base64
# import json

# # Load credentials from Streamlit secrets
# firebase_b64 = st.secrets["FIREBASE_KEY_B64"]
# firebase_dict = json.loads(base64.b64decode(firebase_b64).decode("utf-8"))

# # Create credentials object from the decoded Firebase key
# cred = service_account.Credentials.from_service_account_info(firebase_dict)
# db = firestore.Client(credentials=cred, project="metal-frame-fitting-fbef7")

# st.set_page_config(page_title="Fitting Dashboard", layout="wide")

# # Center the title using HTML
# st.markdown("<h1 style='text-align: center;'>📦 Fitting Dashboard</h1>", unsafe_allow_html=True)

# # Load data from Firestore
# docs = db.collection("submissions").stream()
# data = []
# for doc in docs:
#     d = doc.to_dict()
#     if "timestamp" in d and d["timestamp"] is not None:
#         d["timestamp"] = pd.to_datetime(d["timestamp"].isoformat())
#     data.append(d)

# if data:
#     df = pd.DataFrame(data)

#     # Drop rows without timestamp
#     df = df.dropna(subset=["timestamp"])

#     # Convert UTC to IST
#     df["timestamp"] = df["timestamp"].dt.tz_convert("Asia/Kolkata")
#     df["date"] = df["timestamp"].dt.date  # Date-only for filters

#     # --- 📅 Top KPI and Date Range Selector ---
#     st.markdown("### 🧾 Summary")

#     # Date range limits
#     min_date = df["timestamp"].min().date()
#     max_date = df["timestamp"].max().date()

#     # Two equal-width columns with aligned headings
#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown("### Summary")

#     with col2:
#         st.markdown("### Slicers")
#         selected_date_range = st.date_input(
#             label="",
#             value=(min_date, max_date),
#             min_value=min_date,
#             max_value=max_date,
#             key="top_date_range"
#         )

#         selected_model = st.multiselect(
#             label="",
#             options=["All Models"] + df['model'].unique().tolist(),
#             default=["All Models"],
#             key="model_filter"
#         )

#     # --- 🔍 Filter the Data ---
#     filtered_df = df[
#         (df["date"] >= selected_date_range[0]) &
#         (df["date"] <= selected_date_range[1])
#     ]
#     if "All Models" not in selected_model:
#         filtered_df = filtered_df[filtered_df['model'].isin(selected_model)]

#     # --- 🧮 KPI: Total Quantity ---
#     total_qty = filtered_df["quantity"].sum()
#     with col1:
#         st.markdown(f"""
#         <div style='
#             border: 1px solid #e1e1e1;
#             border-radius: 10px;
#             padding: 20px;
#             box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
#             background-color: rgba(14,17,23,0.7);
#             text-align: center;
#             margin-top: 10px;
#         '>
#             <h1 style='font-weight: bold; margin-bottom: 5px;'>{int(total_qty)}</h1>
#             <p style='font-size: 18px;'>📦 Total Quantity</p>
#         </div>
#         """, unsafe_allow_html=True)

#     st.divider()

#     # --- 📊 Unique Models Count per Day ---
#     st.subheader("📊 Count of Unique Models Per Day")
#     unique_models_df = filtered_df.groupby(filtered_df["timestamp"].dt.date)["model"].nunique().reset_index()
#     unique_models_df.columns = ["Date", "Unique Models"]

#     unique_models_chart = px.bar(
#         unique_models_df,
#         x="Date",
#         y="Unique Models",
#         title="Unique Models Count Per Day",
#         text="Unique Models"
#     )
#     unique_models_chart.update_layout(xaxis_title="Date", yaxis_title="Model Count")
#     st.plotly_chart(unique_models_chart, use_container_width=True)

#     st.divider()

#     # --- 📊 Quantity Over Time (Hourly Bar Chart) ---
#     st.subheader("📊 Quantity Over Time (Hourly)")
#     hourly_df = filtered_df.copy()
#     hourly_df['hour'] = hourly_df['timestamp'].dt.floor("H")
#     hourly_summary = hourly_df.groupby('hour', as_index=False)['quantity'].sum().sort_values('hour')

#     hourly_bar = px.bar(
#         hourly_summary,
#         x='hour',
#         y='quantity',
#         text ='quantity',
#         title="Quantity Over Time (Hourly)"
#     )
#     hourly_bar.update_layout(xaxis_title="Hour", yaxis_title="Quantity")
#     hourly_bar.update_xaxes(tickformat='%d-%b\n%H:%M', tickangle=0)
#     st.plotly_chart(hourly_bar, use_container_width=True)

#     st.divider()

#     # --- 📦 Total Quantity per Model (Time Filtered) ---
#     st.subheader("📦 Total Quantity per Model")
#     model_sum = filtered_df.groupby('model')['quantity'].sum().reset_index().sort_values("quantity", ascending=False)

#     model_bar = px.bar(
#         model_sum,
#         x='model',
#         y='quantity',
#         color='model',
#         title="Model-wise Total Quantity",
#         text='quantity'
#     )
#     model_bar.update_layout(xaxis_title="Model", yaxis_title="Quantity")
#     st.plotly_chart(model_bar, use_container_width=True)

#     st.divider()

#     # --- 📋 Full Data Table (Filtered) ---
#     st.subheader("📋 Full Data Dump")

#     # Create working copy and ensure IST timezone
#     full_data = filtered_df.sort_values("timestamp", ascending=False).copy()
#     full_data['timestamp'] = full_data['timestamp'].dt.tz_convert('Asia/Kolkata')

#     # Format timestamp as HH:MM for display
#     full_data_display = full_data.copy()
#     full_data_display['timestamp'] = full_data_display['timestamp'].dt.strftime('%H:%M')

#     # Drop serial_number if exists
#     if 'serial_number' in full_data_display.columns:
#         full_data_display = full_data_display.drop(columns=['serial_number'])

#     # Display table
#     st.dataframe(full_data_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True)

#     # Prepare data for export - ensure HH:MM format in IST
#     @st.cache_data
#     def prepare_export_data(df):
#         export_df = df.copy()
#         # Convert to IST and format as HH:MM
#         export_df['timestamp'] = pd.to_datetime(export_df['timestamp']).dt.tz_convert('Asia/Kolkata').dt.strftime('%H:%M')
#         if 'serial_number' in export_df.columns:
#             export_df = export_df.drop(columns=['serial_number'])
#         return export_df

#     # Create and download CSV
#     export_data = prepare_export_data(full_data)
#     csv = export_data.to_csv(index=False).encode('utf-8')

#     st.download_button(
#         label="📥 Download Data as CSV",
#         data=csv,
#         file_name='fitting_data.csv',
#         mime='text/csv',
#         help="Download will contain timestamps in HH:MM format (IST timezone)"
#     )

#     # --- Footer ---
#     st.markdown("""
#     <style>
#     .footer {
#         position: fixed;
#         left: 20px;
#         bottom: 20px;
#         background-color: rgba(0,0,0,0.9);
#         color: white;
#         padding: 10px 15px;
#         border-radius: 10px;
#         font-size: 14px;
#         font-family: 'Arial', sans-serif;
#         text-align: center;        
#         font-weight: bold;                              
#         z-index: 100;
#         box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
#     }
#     </style>
#     <div class="footer">Made with ❤️ by Govind & Deepanshu</div>
#     """, unsafe_allow_html=True)

# else:
#     st.warning("No data found yet.")
