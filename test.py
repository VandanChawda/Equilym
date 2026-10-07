from analysis import load_data, validate_data


file_path = "data/healthcare_data.csv"

df = load_data(file_path)

print("\n FIRST 5 ROWS")
print(df.head())

print("\nDATASET INFORMATION")
print(df.info())

print("\n MISSING VALUES ")
print(df.isnull().sum())

print("\n VALIDATION ")

errors = validate_data(df)

if errors:
    for error in errors:
        print("❌", error)
else:
    print("✅ Dataset validation successful!")