import yfinance as yf
import pandas as pd
from datetime import datetime

# Load your CSV file, handling thousand separators
csv_file = "deposits.csv"
df = pd.read_csv(csv_file, thousands=',')

# Convert Date column to tz-aware datetime
df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize("US/Eastern")

# Convert Amount column to float
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

# Check for invalid Amount values
if df["Amount"].isnull().any():
    print("Warning: Some Amount values couldn't be converted to numbers. Check your CSV for invalid entries:")
    print(df[df["Amount"].isnull()])
    raise ValueError("Invalid Amount values found in CSV")

# Define the end date (March 31, 2024)
end_date = "2024-03-31"

# Fetch VOO data from Yahoo Finance
voo = yf.Ticker("VOO")
history = voo.history(start=df["Date"].min(), end=end_date)
dividends = voo.dividends  # Fetch dividend history

# Get unadjusted close prices (we'll manually reinvest dividends)
close_prices = history["Close"]

# Calculate initial shares
df["Price on Date"] = df["Date"].apply(
    lambda x: close_prices.loc[x] if x in close_prices.index else close_prices.asof(x)
)
df["Initial Shares"] = df["Amount"] / df["Price on Date"]

# Track reinvested shares separately
df["Reinvested Shares"] = 0.0  # Initialize column for shares from dividends

# For each deposit, calculate additional shares from dividends
for deposit_idx, deposit in df.iterrows():
    deposit_date = deposit["Date"]
    shares = deposit["Initial Shares"]
    reinvested_shares = 0.0
    
    # Find dividends paid after the deposit date
    relevant_dividends = dividends[dividends.index > deposit_date]
    relevant_dividends = relevant_dividends[relevant_dividends.index <= end_date]
    
    for div_date, div_amount in relevant_dividends.items():
        # Calculate dividend payment for these shares
        div_payment = shares * div_amount
        # Get the unadjusted price on the dividend date to reinvest
        div_price = close_prices.loc[div_date] if div_date in close_prices.index else close_prices.asof(div_date)
        # Buy additional shares with the dividend
        new_shares = div_payment / div_price
        reinvested_shares += new_shares
        shares += new_shares  # Update total shares for next dividend
    
    # Update reinvested shares for this deposit
    df.at[deposit_idx, "Reinvested Shares"] = reinvested_shares

# Calculate total shares
df["Total Shares"] = df["Initial Shares"] + df["Reinvested Shares"]

# Total shares and current value as of March 31, 2024
total_shares = df["Total Shares"].sum()
current_price = close_prices.loc[end_date] if end_date in close_prices.index else close_prices[-1]
total_value = total_shares * current_price

# Add total value as a new column
df["Total Value as of " + end_date] = total_value

# Print results
print("\nDeposit Breakdown:")
print(df.to_string(index=False))
print(f"\nTotal Shares Owned: {total_shares:.4f}")
print(f"Current Price (as of {end_date}): ${current_price:.2f}")
print(f"Total Value: ${total_value:.2f}")

# Save updated CSV
df.to_csv("deposits_with_results.csv", index=False)