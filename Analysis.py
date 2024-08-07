import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

@st.cache_data
def load_data():
    purchase_df = pd.read_csv('Purchase.csv', parse_dates=['Entry Date'], dayfirst=True)
    sales_df = pd.read_csv('Sales.csv', parse_dates=['Entry Date'], dayfirst=True)
    stock_df = pd.read_csv('Stock.csv')
    
    purchase_df['Entry Date'] = purchase_df['Entry Date'].dt.strftime('%m/%d/%Y')
    sales_df['Entry Date'] = sales_df['Entry Date'].dt.strftime('%m/%d/%Y')
    
    stock_df = pd.merge(stock_df, purchase_df[['Entry No.', 'Entry Date']], left_on='NameToDisplay', right_on='Entry No.', how='left')
    
    return purchase_df, sales_df, stock_df

purchase_df, sales_df, stock_df = load_data()
st.title('Inventory Management Dashboard')

st.sidebar.title('Navigation')
options = st.sidebar.radio('Select Page:', ['Overview', 'Best-Selling Items', 'Non-Moving Products', 
                                            'Rejected Goods and Returns', 
                                            'Online Sales Prioritization', 'Unique Products', 
                                            'Top 20% Products'])

if options == 'Overview':
    st.header('Overview')

    total_stock = stock_df['Stock(Unit1)'].sum()
    total_sales = sales_df['Qty(Unit1)'].sum()
    sold_percentage = (total_sales / total_stock) * 100

    st.metric("Total Stock", total_stock)
    st.metric("Total Sales", total_sales)
    st.metric("Sold Percentage", f"{sold_percentage:.2f}%")

    stock_df['Sold Percentage'] = (total_sales - stock_df['Stock(Unit1)']) / total_sales * 100
    stock_df['Days to Sell Out'] = stock_df['Stock(Unit1)'] / sales_df.groupby('Brand')['Qty(Unit1)'].mean()
    threshold_df_75 = stock_df[(stock_df['Sold Percentage'] >= 75)]
    threshold_df_50 = stock_df[(stock_df['Sold Percentage'] >= 50) & (stock_df['Sold Percentage'] < 75)]

    st.subheader('Items Reaching 75% Sold')
    st.table(threshold_df_75[['NameToDisplay', 'Size', 'Stock(Unit1)', 'Sold Percentage', 'Days to Sell Out']])
    st.subheader('Items Reaching 50% Sold')
    st.table(threshold_df_50[['NameToDisplay', 'Size', 'Stock(Unit1)', 'Sold Percentage', 'Days to Sell Out']])

if options == 'Best-Selling Items':
    st.header('Best-Selling Items')

    sales_df['Entry Date'] = pd.to_datetime(sales_df['Entry Date'])
    sales_df['Week'] = sales_df['Entry Date'].dt.isocalendar().week
    sales_df['Month'] = sales_df['Entry Date'].dt.month
    sales_df['Quarter'] = sales_df['Entry Date'].dt.quarter
    time_period = st.selectbox('Select Time Period:', ['Weekly', 'Monthly', 'Quarterly'])

    if time_period == 'Weekly':
        best_selling_weekly = sales_df.groupby('Week')['Qty(Unit1)'].sum().sort_values(ascending=False)
        st.bar_chart(best_selling_weekly)
    elif time_period == 'Monthly':
        best_selling_monthly = sales_df.groupby('Month')['Qty(Unit1)'].sum().sort_values(ascending=False)
        st.bar_chart(best_selling_monthly)
    elif time_period == 'Quarterly':
        best_selling_quarterly = sales_df.groupby('Quarter')['Qty(Unit1)'].sum().sort_values(ascending=False)
        st.bar_chart(best_selling_quarterly)

if options == 'Non-Moving Products':
    st.header('Non-Moving Products')

    non_moving_products = stock_df[~stock_df['NameToDisplay'].isin(sales_df['Brand'])]
    non_moving_products['Entry Date'] = pd.to_datetime(non_moving_products['Entry Date'], format='%m/%d/%Y')
    non_moving_products['Age'] = (datetime.datetime.now() - non_moving_products['Entry Date']).dt.days

    st.table(non_moving_products[['NameToDisplay', 'Size', 'Stock(Unit1)', 'Age']])

if options == 'Exchanges and Returns':
    st.header('Exchanges and Returns')

    returns_df = purchase_df[purchase_df['SALE QTY'] < 0]  # Assuming negative sales quantities indicate returns
    returns_df['Turnaround Time'] = (returns_df['Entry Date'] - returns_df['Entry Date']).dt.days

    avg_turnaround_time = returns_df['Turnaround Time'].mean()
    st.metric("Average Turnaround Time (Days)", avg_turnaround_time)
    st.table(returns_df)

if options == 'Rejected Goods and Returns':
    st.header('Rejected Goods and Returns')
    rejected_goods = purchase_df[purchase_df['Amount'] == 0]  # Assuming zero amount indicates rejected goods
    rejected_goods_by_vendor = rejected_goods.groupby('Vendor')['Qty(Unit1)'].sum().reset_index()

    st.table(rejected_goods_by_vendor)

if options == 'Online Sales Prioritization':
    st.header('Online Sales Prioritization')

    high_demand_products = stock_df[stock_df['Stock(Unit1)'] > stock_df['Stock(Unit1)'].quantile(0.75)]
    st.table(high_demand_products)

if options == 'Unique Products':
    st.header('Unique Products')

    unique_products = stock_df[~stock_df['NameToDisplay'].isin(sales_df['Brand'])]
    st.table(unique_products)

if options == 'Top 20% Products':
    st.header('Top 20% Products')

    sales_by_product = sales_df.groupby('Brand')['Qty(Unit1)'].sum()
    top_20_percent = sales_by_product[sales_by_product.cumsum() / sales_by_product.sum() <= 0.20]

    st.table(top_20_percent)
