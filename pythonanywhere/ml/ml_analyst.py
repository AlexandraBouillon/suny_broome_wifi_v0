import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
import warnings
from sklearn.model_selection import GridSearchCV
from sklearn.inspection import partial_dependence
warnings.filterwarnings('ignore')

# Function to analyze dataset and return metrics
def analyze_dataset(file_path, dataset_name):
    print(f"\n=== Analyzing {dataset_name} ===")
    
    # Read and process data
    df = pd.read_csv(file_path, skiprows=5)
    
    # Apply all the same preprocessing steps as before
    df = df[~df['Read'].isin(['Date', 'TOTAL'])]
    df['Read'] = pd.to_datetime(df['Read'], format='mixed', errors='coerce')
    df = df.dropna(subset=['Read'])
    df = df.replace('#DIV/0!', np.nan)
    df = df.dropna(subset=['Total Usage', 'Total Cost'])
    
    # Convert numeric columns
    numeric_columns = ['On-Peak', 'On-Peak.1', 'On-Peak.2',
                      'Off-Peak', 'Off-Peak.1', 'Off-Peak.2',
                      'Total Usage', 'Total Cost', 'Cost/kWh', 'Usage/Day']
    
    for col in numeric_columns:
        df[col] = df[col].replace(r'[\$,]', '', regex=True).astype(float)
    
    # Create features
    df['Month'] = df['Read'].dt.month
    df['Year'] = df['Read'].dt.year
    df['Month_Sin'] = np.sin(2 * np.pi * df['Month']/12)
    df['Month_Cos'] = np.cos(2 * np.pi * df['Month']/12)
    
    # Prepare features for cost prediction
    X = df[['Total Usage', 'On-Peak.1', 'Off-Peak.1',
            'Month_Sin', 'Month_Cos']]
    y = df['Total Cost']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest model
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = rf_model.predict(X_test)
    
    # Calculate metrics
    metrics = {
        'dataset_name': dataset_name,
        'data_points': len(df),
        'date_range': f"{df['Read'].min().strftime('%Y-%m')} to {df['Read'].max().strftime('%Y-%m')}",
        'r2_train': rf_model.score(X_train, y_train),
        'r2_test': rf_model.score(X_test, y_test),
        'mse': mean_squared_error(y_test, y_pred),
        'cv_score_mean': np.mean(cross_val_score(rf_model, X, y, cv=5)),
        'cv_score_std': np.std(cross_val_score(rf_model, X, y, cv=5)),
        'feature_importance': dict(zip(X.columns, rf_model.feature_importances_))
    }
    
    return metrics

# Analyze both datasets
datasets = [
    ('Electric_Gas_Usage_2019.csv', '2019 Dataset'),
    ('Electric_Gas_Usage_1998_2021.csv', '1998-2021 Dataset')
]

results = []
for file_path, name in datasets:
    metrics = analyze_dataset(file_path, name)
    results.append(metrics)

# Compare results
print("\n=== Dataset Comparison ===")
for metric in results:
    print(f"\nDataset: {metric['dataset_name']}")
    print(f"Data points: {metric['data_points']}")
    print(f"Date range: {metric['date_range']}")
    print(f"R² Score (Training): {metric['r2_train']:.3f}")
    print(f"R² Score (Testing): {metric['r2_test']:.3f}")
    print(f"Mean Squared Error: {metric['mse']:.2f}")
    print(f"Cross-validation Score: {metric['cv_score_mean']:.3f} (+/- {metric['cv_score_std']:.3f})")
    print("\nFeature Importance:")
    for feature, importance in sorted(metric['feature_importance'].items(), 
                                    key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {importance:.3f}")

# Read the CSV file, skipping the first few rows of metadata
# df = pd.read_csv('Electric_Gas_Usage_2019.csv', skiprows=5) # First data set
df = pd.read_csv('Electric_Gas_Usage_1998_2021.csv', skiprows=5) # Second Data set 

# Remove rows where 'Read' contains 'Date' or 'TOTAL'
df = df[~df['Read'].isin(['Date', 'TOTAL'])]

# Print the unique values in the Read column to see what we're dealing with
print("Unique values in Read column:", df['Read'].unique())

# Convert Read column to datetime with flexible parsing and error handling
df['Read'] = pd.to_datetime(df['Read'], format='mixed', errors='coerce')

# Remove any rows where the date conversion failed (resulted in NaT)
df = df.dropna(subset=['Read'])

# Remove any rows with '#DIV/0!' or empty values
df = df.replace('#DIV/0!', np.nan)
df = df.dropna(subset=['Total Usage', 'Total Cost'])

# Convert numeric columns to float, removing any '$' and ',' characters
numeric_columns = ['On-Peak', 'On-Peak.1', 'On-Peak.2',
                  'Off-Peak', 'Off-Peak.1', 'Off-Peak.2',
                  'Total Usage', 'Total Cost', 'Cost/kWh', 'Usage/Day']

for col in numeric_columns:
    df[col] = df[col].replace(r'[\$,]', '', regex=True).astype(float)

# Add some useful derived features
df['Month'] = df['Read'].dt.month
df['Year'] = df['Read'].dt.year
df['Season'] = pd.cut(df['Month'], 
                     bins=[0,3,6,9,12], 
                     labels=['Winter', 'Spring', 'Summer', 'Fall'])

# Basic statistics
print("\nBasic Statistics:")
print(df[['Total Usage', 'Total Cost', 'Cost/kWh']].describe())

# Monthly usage trends
plt.figure(figsize=(15,6))
plt.plot(df['Read'], df['Total Usage'])
plt.title('Monthly Electricity Usage Over Time')
plt.xlabel('Date')
plt.ylabel('Total Usage')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('monthly_usage_trends.png')
plt.close()

# Seasonal analysis
seasonal_usage = df.groupby('Season')['Total Usage'].mean()
print("\nAverage Usage by Season:")
print(seasonal_usage)

# Correlation analysis
correlation_matrix = df[['Total Usage', 'On-Peak.1', 
                        'Off-Peak.1', 'Total Cost']].corr()
plt.figure(figsize=(10,8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig('correlation_matrix.png')
plt.close()

# Time Series Analysis
print("\n=== Time Series Analysis ===")
# Resample to monthly frequency and decompose
monthly_usage = df.set_index('Read')['Total Usage'].resample('M').mean()
# Fill any missing values using forward fill method
monthly_usage = monthly_usage.fillna(method='ffill')

# Now perform the decomposition on the clean data
decomposition = seasonal_decompose(monthly_usage, period=12, extrapolate_trend='freq')

# Time series decomposition
plt.figure(figsize=(15, 10))
plt.subplot(411)
plt.plot(monthly_usage)
plt.title('Original Time Series')
plt.subplot(412)
plt.plot(decomposition.trend)
plt.title('Trend')
plt.subplot(413)
plt.plot(decomposition.seasonal)
plt.title('Seasonal')
plt.subplot(414)
plt.plot(decomposition.resid)
plt.title('Residual')
plt.tight_layout()
plt.savefig('time_series_decomposition.png')
plt.close()

# Peak Demand Analysis
print("\n=== Peak Demand Analysis ===")
plt.figure(figsize=(15,6))
plt.plot(df['Read'], df['On-Peak.1'], label='On-Peak')
plt.plot(df['Read'], df['Off-Peak.1'], label='Off-Peak')
plt.title('Peak Demand Patterns')
plt.xlabel('Date')
plt.ylabel('Demand (kW)')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('peak_demand_patterns.png')
plt.close()

# Calculate peak demand statistics by season
peak_demand_stats = df.groupby('Season')[['On-Peak.1', 'Off-Peak.1']].agg(['mean', 'max'])
print("\nPeak Demand Statistics by Season:")
print(peak_demand_stats)

# 3. Cost Analysis with Enhanced ML Monitoring
print("\n=== Cost Analysis with ML ===")
# Create more features for cost prediction
df['Month_Sin'] = np.sin(2 * np.pi * df['Month']/12)
df['Month_Cos'] = np.cos(2 * np.pi * df['Month']/12)

# Prepare features for cost prediction
X = df[['Total Usage', 'On-Peak.1', 'Off-Peak.1',
        'Month_Sin', 'Month_Cos']]
y = df['Total Cost']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Make predictions
y_pred = rf_model.predict(X_test)

# Evaluate model performance
print("\nModel Performance Metrics:")
print(f"R² Score (Training): {rf_model.score(X_train, y_train):.3f}")
print(f"R² Score (Testing): {rf_model.score(X_test, y_test):.3f}")
print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred):.2f}")

# Cross-validation scores
cv_scores = cross_val_score(rf_model, X, y, cv=5)
print("\nCross-validation scores:", cv_scores)
print(f"Average CV Score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)
print("\nFeature Importance for Cost Prediction:")
print(feature_importance)

# Visualization updates
plt.figure(figsize=(10, 6))
feature_importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

sns.barplot(x='importance', y='feature', data=feature_importance_df)
plt.title('Feature Importance in Random Forest Model')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('feature_importance.png')
plt.close()

# 2. Partial Dependence Plots for top features
def plot_partial_dependence(model, X, feature_name, feature_idx):
    plt.figure(figsize=(8, 6))
    
    # Calculate partial dependence manually
    feature_values = np.linspace(X.iloc[:, feature_idx].min(), 
                               X.iloc[:, feature_idx].max(), 
                               num=50)
    
    # Create a copy of X for predictions
    pdp_values = []
    for value in feature_values:
        X_temp = X.copy()
        X_temp.iloc[:, feature_idx] = value
        predictions = model.predict(X_temp)
        pdp_values.append(predictions.mean())
    
    plt.plot(feature_values, pdp_values)
    plt.xlabel(feature_name)
    plt.ylabel('Partial dependence')
    plt.title(f'Partial Dependence Plot for {feature_name}')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'partial_dependence_{feature_name}.png'.replace(' ', '_'))
    plt.close()

# Plot partial dependence for top 3 features
top_features = feature_importance_df['feature'].head(3)
for idx, feature in enumerate(top_features):
    feature_idx = list(X.columns).index(feature)
    plot_partial_dependence(rf_model, X, feature, feature_idx)

# 3. Decision Path Visualization for a Sample
def visualize_decision_path(model, sample, feature_names):
    # Get the decision path for the sample
    decision_path = model.estimators_[0].decision_path(sample.reshape(1, -1))
    
    # Get the node feature, threshold and sample value at each step
    node_indicator = decision_path.indices
    node_index = decision_path.indptr
    
    # Print the decision path
    print("\nDecision Path for First Tree:")
    for node_id in node_indicator[node_index[0]:node_index[1]]:
        if model.estimators_[0].tree_.children_left[node_id] == -1:  # leaf
            print(f"Leaf node reached. Prediction value = "
                  f"{model.estimators_[0].tree_.value[node_id][0][0]:.2f}")
        else:
            feature = model.estimators_[0].tree_.feature[node_id]
            threshold = model.estimators_[0].tree_.threshold[node_id]
            print(f"Decision node {node_id}: {feature_names[feature]} "
                  f"<= {threshold:.2f} ? "
                  f"(actual value: {sample[feature]:.2f})")

# Visualize decision path for a sample
sample_instance = X_test.iloc[0].values
visualize_decision_path(rf_model, sample_instance, X.columns)

# Actual vs predicted values
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Cost ($)')
plt.ylabel('Predicted Cost ($)')
plt.title('Actual vs Predicted Costs')
plt.tight_layout()
plt.savefig('actual_vs_predicted.png')
plt.close()

# Prediction errors
errors = y_test - y_pred
plt.figure(figsize=(10, 6))
plt.hist(errors, bins=30)
plt.xlabel('Prediction Error ($)')
plt.ylabel('Count')
plt.title('Distribution of Prediction Errors')
plt.tight_layout()
plt.savefig('prediction_errors.png')
plt.close()

# Make a sample prediction
print("\nSample Prediction:")
sample_data = X_test.iloc[0]
actual_cost = y_test.iloc[0]
predicted_cost = rf_model.predict([sample_data])[0]
print(f"Input features:\n{sample_data}")
print(f"Actual cost: ${actual_cost:.2f}")
print(f"Predicted cost: ${predicted_cost:.2f}")
print(f"Error: ${abs(actual_cost - predicted_cost):.2f}")

# 4. Efficiency Analysis
print("\n=== Efficiency Analysis ===")
# Calculate days between readings
df['Days'] = (df['Read'] - df['Read'].shift(1)).dt.days

# Fill the first row's days (which will be NaN) with the median
df['Days'] = df['Days'].fillna(df['Days'].median())

# Calculate efficiency metrics
df['Usage_per_Day'] = df['Total Usage'] / df['Days']
df['Cost_per_Day'] = df['Total Cost'] / df['Days']

# Create efficiency visualization
plt.figure(figsize=(15,6))
plt.subplot(1,2,1)
sns.boxplot(x='Season', y='Usage_per_Day', data=df)
plt.title('Daily Usage by Season')
plt.xticks(rotation=45)

plt.subplot(1,2,2)
sns.boxplot(x='Season', y='Cost_per_Day', data=df)
plt.title('Daily Cost by Season')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('efficiency_analysis.png')
plt.close()

# 5. Year-over-Year Analysis
print("\n=== Year-over-Year Analysis ===")
yearly_comparison = df.pivot_table(
    index='Month',
    columns='Year',
    values='Total Usage',
    aggfunc='mean'
)

plt.figure(figsize=(15,6))
yearly_comparison.plot()
plt.title('Monthly Usage Comparison Across Years')
plt.xlabel('Month')
plt.ylabel('Average Usage')
plt.legend(title='Year')
plt.grid(True)
plt.savefig('yearly_comparison.png')
plt.close()

# 6. Weather Impact Analysis
print("\n=== Weather Impact Analysis ===")
print("Note: Weather analysis requires external weather data. Consider adding temperature data for more insights.")

# 7. Anomaly Detection
print("\n=== Anomaly Detection ===")
# Detect unusual usage patterns
isolation_forest = IsolationForest(contamination=0.1, random_state=42)
df['anomaly'] = isolation_forest.fit_predict(df[['Total Usage', 'Total Cost']])

# Plot anomalies
plt.figure(figsize=(15,6))
plt.scatter(df['Read'], df['Total Usage'], 
           c=df['anomaly'], cmap='viridis')
plt.title('Usage Anomalies')
plt.xlabel('Date')
plt.ylabel('Total Usage')
plt.colorbar(label='Anomaly Score')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('anomaly_detection.png')
plt.close()

# Print summary statistics
print("\n=== Summary Statistics ===")
print(f"Average daily usage: {df['Usage_per_Day'].mean():.2f} kWh")
print(f"Average daily cost: ${df['Cost_per_Day'].mean():.2f}")
print(f"Highest usage month: {df.loc[df['Total Usage'].idxmax(), 'Read'].strftime('%Y-%m')}")
print(f"Lowest usage month: {df.loc[df['Total Usage'].idxmin(), 'Read'].strftime('%Y-%m')}")
print(f"Number of anomalies detected: {sum(df['anomaly'] == -1)}")

# Define parameter grid
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10]
}

# Perform grid search
grid_search = GridSearchCV(RandomForestRegressor(), param_grid, cv=5)
grid_search.fit(X_train, y_train)

print("Best parameters:", grid_search.best_params_)
print("Best score:", grid_search.best_score_)