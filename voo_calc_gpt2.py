import pandas as pd
import yfinance as yf

# Load deposit data
df = pd.read_csv("deposits.csv", thousands=",", parse_dates=["Date"])
df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize("US/Eastern")

# Fetch VOO historical data
voo = yf.Ticker("VOO")
voo_history = voo.history(start=df['Date'].min(), end="2024-03-31", auto_adjust=True)
voo_history.index = voo_history.index.tz_convert("US/Eastern")

# Calculate shares purchased
def get_shares(row):
    try:
        price = voo_history.loc[row['Date']]['Close']
        return row['Amount'] / price
    except KeyError:
        return 0

# Apply share calculation
df['Price on Date'] = df['Date'].apply(lambda date: voo_history.asof(date)['Close'])
df['Initial Shares'] = df.apply(get_shares, axis=1)
df['Reinvested Shares'] = 0

dividends = voo.dividends.loc[df['Date'].min():pd.Timestamp("2024-03-31", tz="US/Eastern")]
dividends.index = dividends.index.tz_convert("US/Eastern")
total_shares = df['Initial Shares'].sum()

qualified_pct = 0.95
qualified_tax_rate = 0.15
non_qualified_tax_rate = 0.24

def net_dividend(dividend):
    qualified = dividend * qualified_pct * (1 - qualified_tax_rate)
    non_qualified = dividend * (1 - qualified_pct) * (1 - non_qualified_tax_rate)
    return qualified + non_qualified

total_tax_paid = 0
reinvestments = []

for date, dividend in dividends.items():
    price = voo_history.asof(date)['Close']
    gross_dividend = dividend * total_shares
    tax_paid = gross_dividend - net_dividend(gross_dividend)
    total_tax_paid += tax_paid
    reinvested_shares = net_dividend(gross_dividend) / price
    total_shares += reinvested_shares
    reinvestments.append({
        'Date': date,
        'Amount': gross_dividend - tax_paid,
        'Price on Date': price,
        'Initial Shares': 0,
        'Reinvested Shares': reinvested_shares,
        'Total Shares': total_shares
    })

# Append reinvestments to the dataframe
df = pd.concat([df, pd.DataFrame(reinvestments)], ignore_index=True)

# Sort by Date
df = df.sort_values(by="Date")

# Fill Total Shares column
df['Total Shares'] = df['Initial Shares'].cumsum() + df['Reinvested Shares'].cumsum()

# Final portfolio value
final_price = voo_history.asof(pd.Timestamp("2024-03-31", tz="US/Eastern"))["Close"]
total_value = total_shares * final_price

print(f"Total Value as of 2024-03-31: ${total_value:.2f}")
print(f"Total Taxes Paid on Dividends: ${total_tax_paid:.2f}")

# Save results
df.to_csv("voo_portfolio_summary.csv", index=False)
