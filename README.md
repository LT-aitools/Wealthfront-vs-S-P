# Wealthfront-vs-S-P
Scrapes deposits data from Wealthfront statements, and does a "what if" scenario against just investing in VOO (Vanguard S&amp;P 500 ETF)

##Assumptions and Limitations
- This model assumes you only made deposits during the period of the what if analysis (and no withdrawals). You could prob adjust the python code to handle withdrawals though.
- This model assumes a fixed range of dates. To simplify things, I "stopped" the model when I began withdrawing from my investment accounts (to move/close them down). You can find this. You'll have to adjust it (just find/replace "2024-03-31" in the models).
- This model also assumed automatic reinvestment of all dividends. 
- TAXES (for those in the US): (1) Wealthfront (and other robo-advisors) also market "tax-loss harvesting" where, by circumventing the wash-sell clause, they create a "loss" in your taxes, which can be rolled forward indefinitely. This effectively creates a $3000 deduction, so take that into consideration too. (2) Any gains would be subject to tax, so remember that if VOO outperformed Wealthfront by $5000, this would be subject to taxes, so it wouldn't be a full $5000 more. This is kinda complicated to model out though, so I didn't do it. 
  
##Steps
1. Create a folder called "Statement PDFs" and add all Wealthfront PDFs in there.
2. Run `checkdirectory.py` --> this imports the needed libraries and checks it can find the PDFs.
3. Run `extract_wealthfront.py` --> This will extract data and save to a file called `investment_activity.csv`
4. Edit CSV and save to a new file called `deposits.csv` with two columns (Date, Amount). Decide on an end date for your model (maybe when you started withdrawing?)
6. Run one (or both?) of the finalized what-if models: 'voo_calc_gpt2` (prints a final result & outputs intermediate data to voo_portfolio_summary.csv`) and 'voo_calc_grok2` (prints a final result & outputs to `deposits_with_results.csv`).
7. Run `extract_fees.py` --> This will scrape the statement PDFs and sum all the fees over the time period, so you can also consider the fees.

##Difference in models 
The Grok and GPT models generate slightly different numbers, due to different approaches to reinvestment. AFAIK:
- Grok calculates on a per-deposit basis --> For this deposit, if it kept getting reinvested on the set reinvestment dates (quarterly for VOO), how many shares would there be at the end and how much would those be worth; vs
- GPT calculates on a per-reinvestment schedule basis --> On each quarterly reinvestment date, how many shares of VOO do I have, and how many dividends would they have generated to be reinvested.

I'm not a financial advisor/modeler, but the Grok approach seems "cleaner" to me, but I also don't really understand why the results differ, as the math should be the same. Anyway, for me at least, both were directionally consistent, ie. both said VOO would have been a stronger choice (and also why I moved off Wealthfront). 

###Older models
I've also elected to include previous/older versions of each of the models (`voo_calc_gpt.py` and `voo_calc_grok.py`). In these versions, the code just printed the final number, so to try to understand the "black box" calc, for v2, I asked them to create intermediary CSVs where I could inspect how the math worked out. This resulted in the bots changing their approaches slightly, so the final numbers also changed.

##Vibe code alert
- All code was developed by ChatGPT and Grok.
- I scoped (and put together) the project rather piecemeal, so likely a bunch of the python code snippets could be combined more efficiently.
