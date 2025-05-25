import os
import pandas as pd

DATA_FOLDER = 'data'

def validate_excel_files(folder):
    valid_files = []
    invalid_files = []

    for file in os.listdir(folder):
        if file.endswith(('.xls', '.xlsx')):
            path = os.path.join(folder, file)
            try:
                df = pd.read_excel(path)
                df.columns = df.columns.str.lower()
                if 'title' in df.columns:
                    valid_files.append(file)
                else:
                    invalid_files.append((file, list(df.columns)))
            except Exception as e:
                invalid_files.append((file, f"Error: {str(e)}"))

    return valid_files, invalid_files

valid, invalid = validate_excel_files(DATA_FOLDER)

print("✅ Valid files:")
for f in valid:
    print(" -", f)

print("\n❌ Invalid or missing 'title' column:")
for f, reason in invalid:
    print(f" - {f} (Issue: {reason})")
