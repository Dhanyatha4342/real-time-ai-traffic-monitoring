import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import glob
import warnings

warnings.filterwarnings("ignore")

# ==== CONFIG ====
input_dir = "./data"
X_out_path = "processed/X.csv"
y_out_path = "processed/y.csv"
chunk_size = 10000

# Collect all files
all_files = glob.glob(os.path.join(input_dir, "*.csv"))

# Prepare label encoder
print("🔍 Scanning all labels to fit LabelEncoder...")
all_labels = []
for file in all_files:
    try:
        df = pd.read_csv(file, usecols=['Label'], on_bad_lines='skip', low_memory=False)
        all_labels.extend(df['Label'].dropna().unique())
    except Exception as e:
        print(f"❌ Skipped {file} during label scan: {e}")
le = LabelEncoder()
le.fit(all_labels)
print(f"✅ Fitted LabelEncoder on {len(le.classes_)} labels.")

# Fit imputer on all numeric data to avoid NaNs
print("🔧 Fitting imputer...")
imputer = SimpleImputer(strategy="mean")
for file in all_files:
    try:
        for chunk in pd.read_csv(file, chunksize=chunk_size, on_bad_lines='skip', low_memory=False):
            chunk = chunk.select_dtypes(include=[np.number])
            imputer.partial_fit(chunk.values)
    except Exception as e:
        print(f"❌ Skipped {file} during imputer fit: {e}")

print("🚀 Processing and writing transformed chunks...")

# Create output folders
os.makedirs(os.path.dirname(X_out_path), exist_ok=True)
os.makedirs(os.path.dirname(y_out_path), exist_ok=True)

first_write = True

for file in all_files:
    try:
        for chunk in pd.read_csv(file, chunksize=chunk_size, on_bad_lines='skip', low_memory=False):
            if 'Label' not in chunk.columns:
                continue

            # Drop nulls in label
            chunk = chunk.dropna(subset=['Label'])

            y = le.transform(chunk['Label'].values)
            X = chunk.drop(columns=['Label'])

            # Drop non-numeric cols
            X = X.select_dtypes(include=[np.number])

            # Fill NaNs
            X_imputed = imputer.transform(X)

            # Write
            pd.DataFrame(X_imputed).to_csv(X_out_path, index=False, mode='a', header=first_write)
            pd.DataFrame(y).to_csv(y_out_path, index=False, mode='a', header=first_write)

            if first_write:
                first_write = False

    except Exception as e:
        print(f"❌ Failed processing {file}: {e}")

print("🎉 Preprocessing complete.")
