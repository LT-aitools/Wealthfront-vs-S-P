import os
import re
import pandas as pd
import pdfplumber

# Path to your PDFs (corrected folder)
statements_dir = "/Users/charlottelau/Documents/LTAIT/WealthfrontStatements/Statement PDFs"
print("Files in directory:", os.listdir(statements_dir))

data = []
# Relaxed regex to catch more variations (e.g., extra spaces, different date formats)
line_pattern = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4})\s+.*?\$([\d,.]+)", re.IGNORECASE)

# Counter for total PDFs processed
pdf_count = 0

for filename in os.listdir(statements_dir):
    if filename.endswith(".pdf"):
        pdf_count += 1
        filepath = os.path.join(statements_dir, filename)
        print(f"\nProcessing PDF {pdf_count}: {filename}")
        try:
            with pdfplumber.open(filepath) as pdf:
                content = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
                    else:
                        print(f"No text extracted from {filename} on page {page.page_number}")

                if not content:
                    print(f"Warning: No content extracted from {filename}")
                    continue

                in_deposits = False
                in_withdrawals = False
                lines = content.split("\n")
                deposit_lines = 0
                withdrawal_lines = 0

                for line in lines:
                    line = line.strip()
                    # Case-insensitive section detection
                    if "DEPOSITS" in line.upper():
                        in_deposits = True
                        in_withdrawals = False
                        print(f"Found DEPOSITS section in {filename}")
                        continue
                    elif "WITHDRAWALS" in line.upper():
                        in_deposits = False
                        in_withdrawals = True
                        print(f"Found WITHDRAWALS section in {filename}")
                        continue
                    elif any(x in line.upper() for x in ["TRADES", "DIVIDENDS", "FEES"]):
                        in_deposits = False
                        in_withdrawals = False
                        continue

                    if (in_deposits or in_withdrawals) and "TOTAL" not in line.upper():
                        match = line_pattern.search(line)
                        if match and ".." not in line:
                            date = match.group(1)
                            amount = match.group(2)
                            type_ = "Deposit" if in_deposits else "Withdrawal"
                            print(f"Match in {filename}: {date}, {type_}, ${amount}")
                            data.append({"Date": date, "Type": type_, "Amount": amount, "File": filename})
                            if in_deposits:
                                deposit_lines += 1
                            else:
                                withdrawal_lines += 1
                        else:
                            print(f"No match in {filename} for line: '{line}'")

                print(f"Summary for {filename}: {deposit_lines} deposits, {withdrawal_lines} withdrawals")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

print(f"\nTotal PDFs processed: {pdf_count}")
if data:
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="coerce")
    df = df.sort_values("Date")
    df.to_csv("investment_activity.csv", index=False)
    print("\nData extracted and saved to 'investment_activity.csv'")
    print(f"Total rows extracted: {len(df)}")
    print(df)
else:
    print("No deposit or withdrawal data found in the PDFs.")