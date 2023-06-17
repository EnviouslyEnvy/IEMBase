from requests_html import HTMLSession
import pandas as pd

session = HTMLSession()
# Use session to get page
r = session.get(r'https://crinacle.com/rankings/iems/') # r meaning response
r.html.render(timeout=120)

# Get table headers
header_row = r.html.find('tr', first=True)
headers = [th.text for th in header_row.find('th')]

# Find all the table rows
rows = r.html.find('tr')  # update the CSS selector if needed

data=[]

# Iterate through rows
for row in rows:
    # Find all table data (td) elements within each table row 'tr'
    tds=row.find('td')
    
    # Extract row data from each td
    row_data=[td.text for td in tds]
    
    data.append(row_data)
    
df = pd.DataFrame(data, columns=headers)
# print(df)

dfreset = df.iloc[2:]
dfreset = dfreset.reset_index()
print(dfreset)
