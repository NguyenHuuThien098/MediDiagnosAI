from sqlalchemy import create_engine, Column, String, Text, Enum, ForeignKey, JSON, Integer, TIMESTAMP
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
import os
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy thông tin kết nối cơ sở dữ liệu từ biến môi trường
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Tạo chuỗi kết nối database
DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

# In ra URL kết nối để debug
logger.info(f"DATABASE_URL: {DATABASE_URL}")

# Kết nối đến cơ sở dữ liệu MySQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Định nghĩa bảng triệu chứng
class Symptom(Base):
    __tablename__ = "symptoms"
    symptom_id = Column(String(20), primary_key=True)
    original_id = Column(String(20))
    name_en = Column(String(255), unique=True, index=True)
    name_vn = Column(String(255))
    des_en = Column(Text)
    des_vn = Column(Text)
    synonym = Column(Text)
    frequency = Column(Enum("low", "medium", "high"))
    duration = Column(String(255))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

# Định nghĩa bảng bệnh
class Disease(Base):
    __tablename__ = "diseases"
    disease_id = Column(String(20), primary_key=True)
    original_id = Column(String(20))
    name_en = Column(String(255), unique=True, index=True)
    name_vn = Column(String(255))
    des_en = Column(Text)
    des_vn = Column(Text)
    specialization = Column(String(255))
    synonyms = Column(JSON)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

# Định nghĩa bảng mối quan hệ giữa bệnh và triệu chứng
class DiseaseSymptom(Base):
    __tablename__ = "disease_symptom"
    disease_id = Column(String(20), ForeignKey("diseases.disease_id"), primary_key=True)
    symptom_id = Column(String(20), ForeignKey("symptoms.symptom_id"), primary_key=True)
    weight = Column(Integer)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    disease = relationship("Disease")
    symptom = relationship("Symptom")

# Hàm tiện ích để lấy session kết nối cơ sở dữ liệu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Tạo bảng trong cơ sở dữ liệu
Base.metadata.create_all(bind=engine)

# Kiểm tra kết nối nếu file được chạy trực tiếp
if __name__ == "__main__":
    try:
        connection = engine.connect()
        logger.info("Kết nối thành công đến database!")
        connection.close()
    except Exception as e:
        logger.error(f"Lỗi kết nối: {e}")