from sqlalchemy import create_engine, Column, String, Text, Enum, ForeignKey, JSON, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Kết nối đến cơ sở dữ liệu MySQL
DATABASE_URL = "mysql+pymysql://thien:thienhuu098@127.0.0.1:3306/medical_diagnosis"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Định nghĩa bảng triệu chứng
class Symptom(Base):
    __tablename__ = "symptoms"
    symptom_id = Column(String(20), primary_key=True)  # Đã sửa từ sym_ptm_id thành symptom_id
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
    symptom_id = Column(String(20), ForeignKey("symptoms.symptom_id"), primary_key=True)  # Đã sửa từ sym_ptm_id thành symptom_id
    weight = Column(Integer)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    disease = relationship("Disease")
    symptom = relationship("Symptom")

# Tạo bảng trong cơ sở dữ liệu
Base.metadata.create_all(bind=engine)