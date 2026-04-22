import streamlit as st
import pandas as pd
import os

data_folder = 'data'
cleaned_file = os.path.join(data_folder, 'cleaned_balance_sheet.csv')

df = pd.read_csv(cleaned_file)
df['endDate'] = pd.to_datetime(df['endDate'])

st.title("Interactive Corporate Leverage & Financial Health Comparator")
st.markdown("Compare company debt levels, asset-liability ratio and debt-to-equity using historical balance sheet data (2012-2020)")

st.sidebar.header("Filters")
stocks = sorted(df['stock'].unique())
selected_stocks = st.sidebar.multiselect("Select 2-6 companies", stocks, default=["IVC", "CSLT"])

years = sorted(df['endDate'].dt.year.unique(), reverse=True)
selected_year = st.sidebar.selectbox("Select Year", years, index=0)

filtered_df = df[(df['stock'].isin(selected_stocks)) & (df['endDate'].dt.year == selected_year)]

st.subheader(f"Financial Health Comparison - {selected_year}")

if len(selected_stocks) == 0:
    st.warning("Please select at least one company from the sidebar.")
elif filtered_df.empty:
    st.warning(f"No data found for the selected companies in {selected_year}.")
    available_years = sorted(df[df['stock'].isin(selected_stocks)]['endDate'].dt.year.unique())
    st.info(f"Try a different year. Available years for these companies: {available_years}")
else:
    display_cols = ['stock', 'totalAssets', 'totalLiab', 'totalStockholderEquity', 
                    'asset_liability_ratio', 'debt_to_equity_ratio']
    st.dataframe(filtered_df[display_cols].set_index('stock'), use_container_width=True)
    
    st.subheader("Asset Liability Ratio (%)")
    st.bar_chart(filtered_df.set_index('stock')['asset_liability_ratio'])
    
    st.subheader("Debt to Equity Ratio")
    st.bar_chart(filtered_df.set_index('stock')['debt_to_equity_ratio'])

    st.subheader("Simple Analysis Summary (for regular investors)")
    analysis = ""
    for stock in selected_stocks:
        row = filtered_df[filtered_df['stock'] == stock].iloc[0]
        alr = row['asset_liability_ratio']
        der = row['debt_to_equity_ratio']
        
        if alr > 70:
            status = "high debt burden and higher risk"
        elif alr > 50:
            status = "normal debt level"
        else:
            status = "healthy financial structure"
            
        analysis += f"**{stock}**: Asset-liability ratio {alr}% ({status}), debt-to-equity ratio {der}. "
    st.markdown(analysis)

    st.subheader("Historical Trend - Asset Liability Ratio (%)")
    historical = df[df['stock'].isin(selected_stocks)].copy()
    historical['Year'] = historical['endDate'].dt.year
    trend_data = historical.pivot_table(index='Year', columns='stock', values='asset_liability_ratio')
    st.line_chart(trend_data)

    st.download_button("Download comparison as CSV", 
                       filtered_df[display_cols].to_csv(index=False), 
                       "financial_comparison.csv", 
                       "text/csv")

st.caption("Data source: Kaggle - Financial data of 4400+ public companies")