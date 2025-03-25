import os
import re
import pandas as pd
import pdfplumber

statements_dir = "/Users/charlottelau/Documents/LTAIT/WealthfrontStatements/Statement PDFs"
print("Files in directory:", os.listdir(statements_dir))  # Check if PDFs are listed

data = []
line_pattern = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})\s+.*?\s+\$([\d,.]+)")

for filename in os.listdir(statements_dir):
    if filename.endswith(".pdf"):
        filepath = os.path.join(statements_dir, filename)
        print(f"Processing: {filename}")  # Confirm each file is being processed