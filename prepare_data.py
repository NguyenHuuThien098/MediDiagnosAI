import pandas as pd

# Đọc dữ liệu từ các tệp JSON
table_symptom = pd.read_json('data/table_symptom.json')
table_disease = pd.read_json('data/table_disease.json')
table_disease_symptom = pd.read_json('data/table_disease_symptom.json')

# Hiển thị dữ liệu để kiểm tra
print("Table Symptom:")
print(table_symptom.head())

print("\nTable Disease:")
print(table_disease.head())

print("\nTable Disease-Symptom:")
print(table_disease_symptom.head())

# Tạo danh sách các triệu chứng và bệnh
symptoms = table_symptom['name_en'].dropna().tolist()  # Loại bỏ giá trị NaN nếu có
diseases = table_disease['name_en'].dropna().tolist()  # Loại bỏ giá trị NaN nếu có

# Tạo DataFrame rỗng với các bệnh là hàng và triệu chứng là cột
data = pd.DataFrame(0, index=diseases, columns=symptoms)

# Điền dữ liệu vào DataFrame
for _, row in table_disease_symptom.iterrows():
    # Lấy tên bệnh từ `table_disease` dựa trên `disease_id`
    disease_row = table_disease.loc[table_disease['disease_id'] == row['disease_id']]
    if not disease_row.empty:
        disease = disease_row['name_en'].values[0]
    else:
        continue  # Bỏ qua nếu không tìm thấy bệnh

    # Lấy tên triệu chứng từ `table_symptom` dựa trên `symptom_id`
    symptom_row = table_symptom.loc[table_symptom['symptom_id'] == row['symptom_id']]
    if not symptom_row.empty:
        symptom = symptom_row['name_en'].values[0]
    else:
        continue  # Bỏ qua nếu không tìm thấy triệu chứng

    # Đánh dấu mối quan hệ giữa bệnh và triệu chứng
    if disease in data.index and symptom in data.columns:
        data.loc[disease, symptom] = 1

# Hiển thị DataFrame kết quả
print("\nDataFrame sau khi chuyển đổi:")
print(data.head())

# Lưu DataFrame vào file CSV (nếu cần)
data.to_csv('data/processed_data.csv', index=True)