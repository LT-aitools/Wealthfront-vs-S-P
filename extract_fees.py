import os
import re
import pandas as pd
import pdfplumber

# Path to your PDFs
statements_dir = "/Users/charlottelau/Documents/LTAIT/WealthfrontStatements/Statement PDFs"
print("Files in directory:", os.listdir(statements_dir))

data = []
# Regex for fees (date + "Wealthfront Advisory Fee" + amount)
fee_pattern = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4})\s+Wealthfront Advisory Fee.*?\$([\d,.]+)", re.IGNORECASE)

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

                in_fees = False
                lines = content.split("\n")
                fee_lines = 0

                for line in lines:
                    line = line.strip()
                    # Section detection
                    if "FEES" in line.upper():
                        in_fees = True
                        print(f"Found FEES section in {filename}")
                        continue
                    elif any(x in line.upper() for x in ["TRADES", "DIVIDENDS", "HOLDINGS", "DEPOSITS", "WITHDRAWALS"]):
                        in_fees = False
                        continue

                    # Extract fees
                    if in_fees and "TOTAL" not in line.upper():
                        match = fee_pattern.search(line)
                        if match:
                            date = match.group(1)
                            amount = match.group(2)
                            print(f"Fee match in {filename}: {date}, Fee, ${amount}")
                            data.append({"Date": date, "Type": "Fee", "Amount": amount, "File": filename})
                            fee_lines += 1
                        else:
                            print(f"No fee match in {filename} for line: '{line}'")

                print(f"Summary for {filename}: {fee_lines} fees extracted")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

print(f"\nTotal PDFs processed: {pdf_count}")
if data:
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="coerce")
    df = df.sort_values("Date")
    df.to_csv("wealthfront_fees.csv", index=False)
    print("\nData extracted and saved to 'wealthfront_fees.csv'")
    print(f"Total fees extracted: {len(df)}")
    print(df)
else:
    print("No fee data found in the PDFs.")