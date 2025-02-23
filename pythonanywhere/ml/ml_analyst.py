import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns

# Read the CSV file, skipping the first few rows of metadata
df = pd.read_csv('Electric_Gas_Usage_2019.csv', skiprows=5)

# Convert Read Date to datetime
df['Read Date'] = pd.to_datetime(df['Read Date'], format='%m/%d/%y')

# Remove any rows with '#DIV/0!' or empty values
df = df.replace('#DIV/0!', np.nan)
df = df.dropna(subset=['Total Usage (kWh)', 'Total Cost ($)'])

# Convert numeric columns to float, removing any '$' and ',' characters
numeric_columns = ['On-Peak Usage (kWh)', 'On-Peak Demand (kW)', 'On-Peak Cost ($)',
                  'Off-Peak Usage (kWh)', 'Off-Peak Demand (kW)', 'Off-Peak Cost ($)',
                  'Total Usage (kWh)', 'Total Cost ($)', 'Cost/kWh ($)', 'Usage/Day (kWh)']

for col in numeric_columns:
    df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)

# Add some useful derived features
df['Month'] = df['Read Date'].dt.month
df['Year'] = df['Read Date'].dt.year
df['Season'] = pd.cut(df['Month'], 
                     bins=[0,3,6,9,12], 
                     labels=['Winter', 'Spring', 'Summer', 'Fall'])

# Basic statistics
print("\nBasic Statistics:")
print(df[['Total Usage (kWh)', 'Total Cost ($)', 'Cost/kWh ($)']].describe())

# Plot monthly usage trends
plt.figure(figsize=(15,6))
plt.plot(df['Read Date'], df['Total Usage (kWh)'])
plt.title('Monthly Electricity Usage Over Time')
plt.xlabel('Date')
plt.ylabel('Total Usage (kWh)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Seasonal analysis
seasonal_usage = df.groupby('Season')['Total Usage (kWh)'].mean()
print("\nAverage Usage by Season:")
print(seasonal_usage)

# Correlation analysis
correlation_matrix = df[['Total Usage (kWh)', 'On-Peak Demand (kW)', 
                        'Off-Peak Demand (kW)', 'Total Cost ($)']].corr()
plt.figure(figsize=(10,8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.tight_layout()
plt.show()

# Simple linear regression to predict cost based on usage
X = df[['Total Usage (kWh)']]
y = df['Total Cost ($)']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

print("\nLinear Regression Results:")
print(f"R² Score: {model.score(X_test, y_test):.3f}")
print(f"Cost per kWh (from model): ${model.coef_[0]:.4f}")

# Compare usage patterns across years
yearly_comparison = df.pivot_table(
    index='Month',
    columns='Year',
    values='Total Usage (kWh)',
    aggfunc='mean'
)

plt.figure(figsize=(15,6))
yearly_comparison.plot()
plt.title('Monthly Usage Comparison Across Years')
plt.xlabel('Month')
plt.ylabel('Average Usage (kWh)')
plt.legend(title='Year')
plt.grid(True)
plt.show()