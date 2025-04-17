# MediDiagnosAI

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103.1-green)

**MediDiagnosAI** là hệ thống chẩn đoán y tế thông minh sử dụng AI kết hợp với cơ sở dữ liệu triệu chứng-bệnh. Dự án này giúp phân tích triệu chứng người dùng nhập vào và đưa ra chẩn đoán sơ bộ dựa trên dữ liệu y học.

## 📋 Tính năng chính

- **Chẩn đoán bệnh từ triệu chứng**: Phân tích các triệu chứng người dùng nhập và đề xuất chẩn đoán có thể
- **Tích hợp AI**: Sử dụng Gemini API để phân tích y khoa chuyên sâu
- **Tìm kiếm thông minh**: Hỗ trợ fuzzy search để tìm triệu chứng tương tự
- **Tư vấn y tế**: Đề xuất xét nghiệm cần thực hiện và khuyến nghị y tế
- **Độ khớp chẩn đoán**: Hiển thị phần trăm khớp giữa triệu chứng và bệnh từ cơ sở dữ liệu

## 🛠️ Công nghệ sử dụng

- **Backend**: FastAPI
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **AI/ML**: Google Gemini API, Scikit-learn
- **Xử lý dữ liệu**: Pandas, NumPy
- **Tìm kiếm tương đồng**: TF-IDF, Fuzzy matching

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống

- Python 3.8+
- MySQL 5.7+
- Gemini API key

### Bước 1: Clone repository

```bash
git clone https://github.com/your-username/MediDiagnosAI.git
cd MediDiagnosAI
```

### Bước 2: Tạo môi trường ảo

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Bước 3: Cài đặt các thư viện

```bash
pip install -r requirements.txt
```

### Bước 4: Thiết lập cơ sở dữ liệu

1. Tạo cơ sở dữ liệu MySQL:

```sql
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Tạo file .env chứa thông tin kết nối:

```
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DATABASE=mydb
DB_HOST=127.0.0.1
DB_PORT=3306
API_KEY=your_gemini_api_key
```

3. Chạy script tạo cấu trúc cơ sở dữ liệu:

```bash
python setup_database.py
```

4. Import dữ liệu mẫu:

```bash
python import_data.py
```

### Bước 5: Chạy ứng dụng

```bash
uvicorn main:app --reload
```

Ứng dụng sẽ chạy tại địa chỉ: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 📊 Cấu trúc dự án

```
MediDiagnosAI/
├── data/                   # Dữ liệu mẫu
│   ├── table_disease.json
│   ├── table_symptom.json
│   └── table_disease_symptom.json
├── main.py                 # Entry point của ứng dụng FastAPI
├── database.py             # Cài đặt kết nối database và models
├── gemini_api.py           # Tương tác với Google Gemini API
├── vectorizer.py           # Chuyển đổi triệu chứng thành vector
├── prepare_data.py         # Xử lý và chuẩn bị dữ liệu
├── find_frequent_itemsets.py # Tìm tập phổ biến (cho phân tích)
├── setup_database.py       # Tạo cấu trúc cơ sở dữ liệu
├── import_data.py          # Import dữ liệu mẫu
├── requirements.txt        # Danh sách các thư viện cần thiết
├── .env                    # File biến môi trường (không push lên git)
└── README.md               # Tài liệu dự án
```

## 🔄 API Endpoints

### Chẩn đoán bệnh từ triệu chứng

```
POST /predict
```

**Request Body:**
```json
{
  "symptoms": ["headache", "fever", "cough"]
}
```

**Response:** Thông tin chẩn đoán bệnh, phần trăm khớp, và phân tích y khoa

### Thông tin chi tiết về bệnh

```
GET /disease/{disease_id}
```

**Response:** Thông tin chi tiết về bệnh và các triệu chứng liên quan

## 📄 Cấu trúc cơ sở dữ liệu

### Bảng `diseases`
- `disease_id`: ID bệnh
- `name_en`: Tên bệnh tiếng Anh
- `name_vn`: Tên bệnh tiếng Việt
- `des_en`: Mô tả bệnh tiếng Anh
- `des_vn`: Mô tả bệnh tiếng Việt
- `specialization`: Chuyên khoa

### Bảng `symptoms`
- `symptom_id`: ID triệu chứng
- `name_en`: Tên triệu chứng tiếng Anh
- `name_vn`: Tên triệu chứng tiếng Việt
- `synonym`: Từ đồng nghĩa
- `frequency`: Tần suất xuất hiện

### Bảng `disease_symptoms`
- `disease_id`: ID bệnh
- `symptom_id`: ID triệu chứng
- `weight`: Trọng số quan hệ

## 📝 Tệp requirements.txt

Dưới đây là nội dung file `requirements.txt` để cài đặt các thư viện cần thiết:

```
fastapi==0.103.1
uvicorn==0.23.2
sqlalchemy==2.0.20
pymysql==1.1.0
python-dotenv==1.0.0
pandas==2.1.0
numpy==1.25.2
scikit-learn==1.3.0
requests==2.31.0
cryptography==41.0.3
python-multipart==0.0.6
```

## 📋 Tệp import_data.py

Để nhập dữ liệu vào cơ sở dữ liệu, hãy tạo tệp `import_data.py` như sau:

```python
import json
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, Disease, Symptom, DiseaseSymptom

def import_data():
    print("Bắt đầu nhập dữ liệu...")
    db = SessionLocal()
    
    try:
        # Nhập dữ liệu bệnh
        with open('data/table_disease.json', 'r', encoding='utf-8') as f:
            diseases_data = json.load(f)
        
        for disease in diseases_data:
            db_disease = Disease(
                disease_id=disease.get('disease_id'),
                name_en=disease.get('name_en'),
                name_vn=disease.get('name_vn'),
                des_en=disease.get('des_en'),
                des_vn=disease.get('des_vn'),
                specialization=disease.get('specialization')
            )
            db.add(db_disease)
        
        # Nhập dữ liệu triệu chứng
        with open('data/table_symptom.json', 'r', encoding='utf-8') as f:
            symptoms_data = json.load(f)
        
        for symptom in symptoms_data:
            db_symptom = Symptom(
                symptom_id=symptom.get('symptom_id'),
                name_en=symptom.get('name_en'),
                name_vn=symptom.get('name_vn'),
                des_en=symptom.get('des_en'),
                des_vn=symptom.get('des_vn'),
                synonym=symptom.get('synonym')
            )
            db.add(db_symptom)
        
        # Nhập dữ liệu quan hệ bệnh-triệu chứng
        with open('data/table_disease_symptom.json', 'r', encoding='utf-8') as f:
            relations_data = json.load(f)
        
        for relation in relations_data:
            db_relation = DiseaseSymptom(
                disease_id=relation.get('disease_id'),
                symptom_id=relation.get('symptom_id'),
                weight=relation.get('weight')
            )
            db.add(db_relation)
        
        db.commit()
        print("Nhập dữ liệu thành công!")
    
    except Exception as e:
        db.rollback()
        print(f"Lỗi khi nhập dữ liệu: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    import_data()
```

## 📋 Tệp setup_database.py

Tạo tệp `setup_database.py` để thiết lập cơ sở dữ liệu:

```python
from database import Base, engine

def create_tables():
    print("Tạo các bảng trong cơ sở dữ liệu...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tạo bảng thành công!")
    except Exception as e:
        print(f"Lỗi khi tạo bảng: {str(e)}")

if __name__ == "__main__":
    create_tables()
```

## 🔒 Bảo mật

- File .env chứa thông tin nhạy cảm nên được thêm vào .gitignore
- Sử dụng biến môi trường thay vì hardcode các thông tin nhạy cảm
- Không lưu trữ API key trong code nguồn

## 🤝 Đóng góp

Đóng góp cho dự án luôn được chào đón. Để đóng góp:

1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit thay đổi (`git commit -m 'Add some amazing feature'`)
4. Push lên branch của bạn (`git push origin feature/amazing-feature`)
5. Mở Pull Request

## 📜 Giấy phép

Dự án được phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.

## 📞 Liên hệ

Nếu có bất kỳ câu hỏi hoặc phản hồi nào, vui lòng liên hệ qua GitHub hoặc email.

---

**Lưu ý:** Hệ thống này chỉ cung cấp thông tin tham khảo và không thay thế cho lời khuyên, chẩn đoán hoặc điều trị từ các chuyên gia y tế có trình độ. Luôn tham khảo ý kiến bác sĩ về mọi vấn đề sức khỏe.