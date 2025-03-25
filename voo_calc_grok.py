import yfinance as yf
import pandas as pd
from datetime import datetime

# Load your CSV file, handling thousand separators
csv_file = "deposits.csv"  # Adjust path if needed
df = pd.read_csv(csv_file, thousands=',')  # Tell pandas to treat commas as thousand separators

# Debugging: Print the raw CSV data to see what we're working with
print("Raw CSV Data:")
print(df)
print("\nColumn Names:", df.columns.tolist())

# Identify the Amount column (case-insensitive or common variations)
amount_col = None
for col in df.columns:
    if col.lower() in ["amount", "deposit", "value"]:
        amount_col = col
        break

if amount_col is None:
    raise ValueError("Could not find an 'Amount' column. Available columns: " + str(df.columns.tolist()))

# Rename the column to "Amount" for consistency
df = df.rename(columns={amount_col: "Amount"})

# Convert Date column to tz-aware datetime
df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize("US/Eastern")

# Convert Amount column to float (should already be numeric, but let's ensure)
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

# Check for invalid Amount values
if df["Amount"].isnull().any():
    print("Warning: Some Amount values couldn't be converted to numbers. Check your CSV for invalid entries:")
    print(df[df["Amount"].isnull()])
    raise ValueError("Invalid Amount values found in CSV")

# Define the end date 
end_date = "2024-03-31"

# Fetch VOO data from Yahoo Finance
voo = yf.Ticker("VOO")
history = voo.history(start=df["Date"].min(), end=end_date)

# Get adjusted close prices (includes reinvested dividends)
adj_close = history["Close"]

# Calculate shares and prices for each deposit
df["Price on Date"] = df["Date"].apply(
    lambda x: adj_close.loc[x] if x in adj_close.index else adj_close.asof(x)
)
df["Shares Bought"] = df["Amount"] / df["Price on Date"]

# Total shares and current value
total_shares = df["Shares Bought"].sum()
current_price = adj_close.loc[end_date] if end_date in adj_close.index else adj_close[-1]  # Last available
total_value = total_shares * current_price

# Add total value as a new column
df["Total Value as of " + end_date] = total_value

# Print results
print("\nDeposit Breakdown:")
print(df.to_string(index=False))
print(f"\nTotal Shares Owned: {total_shares:.4f}")
print(f"Current Price (as of {end_date}): ${current_price:.2f}")
print(f"Total Value: ${total_value:.2f}")

# Save updated CSV to a new file
df.to_csv("deposits_with_results.csv", index=False)