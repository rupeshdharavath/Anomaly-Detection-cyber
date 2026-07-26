import pandas as pd
import os

# Load the cybersecurity dataset
csv_path = os.path.join('d:/Anomaly-Detection/data/raw/cybersecurity_dataset.csv')
df = pd.read_csv(csv_path)

print("Dataset shape:", df.shape)
print("\nColumn names:", list(df.columns))
print("\nFirst few rows:")
print(df.head())

print("\nTimestamp column sample:")
print(df['timestamp'].head() if 'timestamp' in df.columns else "No timestamp column")

print("\nData types:")
print(df.dtypes)

print("\nTrying to parse timestamps:")
try:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.floor('H')
    print("✅ Timestamp parsing successful")
    
    # Try grouping
    time_series = df.groupby('hour').size().reset_index(name='count')
    print(f"\n✅ Grouping successful, got {len(time_series)} hour groups")
    print("\nFirst few time-series points:")
    print(time_series.head())
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
