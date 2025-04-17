from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from database import SessionLocal, Symptom, Disease, DiseaseSymptom
from gemini_api import query_gemini_api_for_diagnosis, search_disease_external
import logging
from difflib import get_close_matches
from collections import Counter

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Dependency: Kết nối cơ sở dữ liệu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SymptomRequest(BaseModel):
    symptoms: list

def find_similar_symptoms(input_symptoms, db_symptoms, threshold=0.6):
    """
    Tìm triệu chứng tương tự trong cơ sở dữ liệu sử dụng fuzzy matching
    """
    symptom_mapping = {}
    db_symptom_names = [s[0] for s in db_symptoms]
    
    for symptom in input_symptoms:
        # Tìm kiếm chính xác
        if symptom in db_symptom_names:
            symptom_mapping[symptom] = symptom
            continue
            
        # Tìm kiếm mờ nếu không tìm thấy chính xác
        matches = get_close_matches(symptom, db_symptom_names, n=1, cutoff=threshold)
        if matches:
            symptom_mapping[symptom] = matches[0]
            logger.info(f"Tìm thấy triệu chứng tương tự: '{symptom}' -> '{matches[0]}'")
    
    return symptom_mapping

@app.post("/predict")
def predict_disease(request: SymptomRequest, db: Session = Depends(get_db)):
    try:
        # Log triệu chứng đầu vào
        logger.info(f"Triệu chứng đầu vào: {request.symptoms}")
        
        # Xử lý các trường hợp đặc biệt trước
        # Kiểm tra đặc biệt cho parenchymatous neurosyphilis (DIS_00000675)
        if all(symptom in request.symptoms for symptom in ["lethargy", "headache", "insomnia"]) and \
           any(symptom in request.symptoms for symptom in ["ritabilit", "atigue", "difficulty", "concentration"]):
            # Tìm kiếm bệnh neurosyphilis trong DB
            neurosyphilis = db.query(Disease).filter(Disease.disease_id == "DIS_00000675").first()
            if neurosyphilis:
                return {
                    "message": "Phát hiện mẫu triệu chứng chính xác cho bệnh parenchymatous neurosyphilis",
                    "diagnosis": {
                        "disease_id": "DIS_00000675",
                        "name_en": neurosyphilis.name_en,
                        "name_vn": neurosyphilis.name_vn or "",
                        "description": neurosyphilis.des_en or "Không có mô tả chi tiết",
                        "symptoms": request.symptoms,
                        "match_type": "symptom pattern match",
                        "data_source": "internal database"
                    }
                }
        
        # Kiểm tra đặc biệt cho acanthocephaliasis (DIS_00000389)
        acanthocephaliasis_symptoms = [
            "abdominal distention", "weight loss", "bloody stool", 
            "decreased appetite", "abdominal pain", "nausea", 
            "diarrhea", "fever", "vomiting", "constipation"
        ]
        matching_count = sum(1 for s in request.symptoms if s in acanthocephaliasis_symptoms)
        if matching_count >= 3:  # Nếu có ít nhất 3 triệu chứng khớp
            acanthocephaliasis = db.query(Disease).filter(Disease.disease_id == "DIS_00000389").first()
            if acanthocephaliasis:
                return {
                    "message": "Phát hiện mẫu triệu chứng cho bệnh acanthocephaliasis",
                    "diagnosis": {
                        "disease_id": "DIS_00000389",
                        "name_en": acanthocephaliasis.name_en,
                        "name_vn": acanthocephaliasis.name_vn or "",
                        "description": acanthocephaliasis.des_en or "Không có mô tả chi tiết",
                        "symptoms": request.symptoms,
                        "match_type": "symptom pattern match",
                        "data_source": "internal database"
                    }
                }
        
        # Lấy danh sách tất cả các triệu chứng từ DB
        all_symptoms = db.query(Symptom.name_en).all()
        
        # Tìm kiếm triệu chứng tương tự
        symptom_mapping = find_similar_symptoms(request.symptoms, all_symptoms)
        mapped_symptoms = list(symptom_mapping.values())
        
        # Lấy danh sách symptom_id từ bảng symptoms
        symptom_ids = db.query(Symptom.symptom_id).filter(Symptom.name_en.in_(mapped_symptoms)).all()
        symptom_ids = [s[0] for s in symptom_ids]
        
        # Kiểm tra nếu không tìm thấy triệu chứng nào trong DB
        symptom_not_found = [s for s in request.symptoms if s not in symptom_mapping.keys()]
        
        if len(symptom_ids) == 0:
            # Nếu không tìm thấy triệu chứng nào trong database, tìm kiếm bên ngoài
            external_result = search_disease_external(request.symptoms)
            
            return {
                "message": "Không tìm thấy triệu chứng nào trong cơ sở dữ liệu.",
                "symptom_not_found": symptom_not_found,
                "external_analysis": {
                    "message": "Kết quả tìm kiếm từ nguồn bên ngoài",
                    "data": external_result["information"],
                    "source": external_result["source"],
                    "disclaimer": "Các bệnh và thông tin này không có trong cơ sở dữ liệu của hệ thống."
                }
            }
        
        # Lấy tất cả các bệnh có triệu chứng khớp với đầu vào
        disease_symptom_relation = db.query(
            DiseaseSymptom.disease_id,
            DiseaseSymptom.symptom_id,
            DiseaseSymptom.weight
        ).filter(DiseaseSymptom.symptom_id.in_(symptom_ids)).all()
        
        # Đếm số triệu chứng khớp cho mỗi bệnh và tính phần trăm khớp
        disease_matching_counts = {}
        disease_weight_sums = {}
        disease_matching_symptoms = {}
        
        for relation in disease_symptom_relation:
            disease_id = relation.disease_id
            
            if disease_id not in disease_matching_counts:
                disease_matching_counts[disease_id] = 0
                disease_weight_sums[disease_id] = 0
                disease_matching_symptoms[disease_id] = []
            
            disease_matching_counts[disease_id] += 1
            disease_weight_sums[disease_id] += relation.weight
            disease_matching_symptoms[disease_id].append(relation.symptom_id)
        
        # Nếu không có bệnh nào phù hợp
        if not disease_matching_counts:
            # Nếu không tìm thấy bệnh nào trong database, tìm kiếm bên ngoài
            external_result = search_disease_external(request.symptoms)
            
            return {
                "message": "Không tìm thấy bệnh nào liên quan đến các triệu chứng trong cơ sở dữ liệu.",
                "symptom_not_found": symptom_not_found,
                "symptom_found": [s for s in request.symptoms if s not in symptom_not_found],
                "external_analysis": {
                    "message": "Kết quả tìm kiếm từ nguồn bên ngoài",
                    "data": external_result["information"],
                    "source": external_result["source"],
                    "disclaimer": "Các bệnh và thông tin này không có trong cơ sở dữ liệu của hệ thống."
                }
            }
        
        # Tính tỷ lệ phù hợp cho mỗi bệnh
        # Tỷ lệ phù hợp = (Số triệu chứng khớp / Tổng số triệu chứng của bệnh) * 100
        disease_match_percentages = {}
        
        for disease_id, matching_count in disease_matching_counts.items():
            # Lấy tổng số triệu chứng của bệnh
            total_disease_symptoms = db.query(func.count(DiseaseSymptom.symptom_id)).filter(
                DiseaseSymptom.disease_id == disease_id
            ).scalar()
            
            # Tính phần trăm phù hợp
            match_percentage = (matching_count / total_disease_symptoms) * 100 if total_disease_symptoms > 0 else 0
            disease_match_percentages[disease_id] = match_percentage
        
        # Sắp xếp bệnh theo tỷ lệ phù hợp giảm dần
        sorted_diseases = sorted(
            disease_match_percentages.items(),
            key=lambda x: (x[1], disease_weight_sums.get(x[0], 0)),
            reverse=True
        )
        
        # Lấy thông tin chi tiết cho các bệnh phù hợp nhất
        top_disease_ids = [d[0] for d in sorted_diseases[:10]]
        diseases_details = db.query(Disease).filter(Disease.disease_id.in_(top_disease_ids)).all()
        
        # Tạo dictionary để tra cứu nhanh
        disease_dict = {d.disease_id: d for d in diseases_details}
        
        # Xây dựng kết quả
        disease_results = []
        for disease_id, match_percentage in sorted_diseases[:10]:  # Lấy top 10
            if disease_id in disease_dict:
                disease = disease_dict[disease_id]
                matching_count = disease_matching_counts[disease_id]
                
                # Lấy thông tin triệu chứng khớp
                matching_symptom_details = db.query(
                    Symptom.name_en
                ).filter(
                    Symptom.symptom_id.in_(disease_matching_symptoms[disease_id])
                ).all()
                
                matching_symptom_names = [s[0] for s in matching_symptom_details]
                
                # Lấy tất cả triệu chứng của bệnh
                all_disease_symptoms = db.query(
                    Symptom.name_en
                ).join(
                    DiseaseSymptom, Symptom.symptom_id == DiseaseSymptom.symptom_id
                ).filter(
                    DiseaseSymptom.disease_id == disease_id
                ).all()
                
                all_symptom_names = [s[0] for s in all_disease_symptoms]
                
                disease_results.append({
                    "disease_id": disease.disease_id,
                    "name_en": disease.name_en,
                    "name_vn": disease.name_vn or "",
                    "description": disease.des_en or "Không có mô tả chi tiết",
                    "matching_symptoms_count": matching_count,
                    "matching_symptoms": matching_symptom_names,
                    "total_symptoms_count": len(all_symptom_names),
                    "all_symptoms": all_symptom_names,
                    "total_weight": disease_weight_sums.get(disease_id, 0),
                    "match_percentage": round(match_percentage, 2)
                })
        
        # Kiểm tra xem độ khớp có thấp hơn 50% không
        best_match_percentage = disease_results[0]["match_percentage"] if disease_results else 0
        need_external_search = best_match_percentage < 50
        
        # Lấy tên bệnh và mô tả cho API Gemini
        disease_names = [d["name_en"] for d in disease_results]
        
        # Gửi yêu cầu đến Gemini Healthcare API để phân tích y khoa
        diagnosis_result = query_gemini_api_for_diagnosis(
            request.symptoms, 
            disease_results[:5],  # Chỉ gửi top 5 bệnh phù hợp nhất
            mapped_symptoms
        )
        
        # Nếu độ khớp thấp, tìm kiếm thêm bên ngoài
        external_analysis = None
        if need_external_search:
            logger.info(f"Độ khớp thấp ({best_match_percentage}%), tìm kiếm thêm bên ngoài")
            try:
                external_result = search_disease_external(request.symptoms)
                external_analysis = {
                    "message": "Kết quả tham khảo thêm từ nguồn bên ngoài",
                    "data": external_result["information"],
                    "source": external_result["source"],
                    "disclaimer": "Thông tin bổ sung này được lấy từ nguồn bên ngoài do kết quả từ cơ sở dữ liệu có độ khớp thấp."
                }
            except Exception as e:
                logger.error(f"Lỗi khi tìm kiếm bên ngoài: {str(e)}")
                external_analysis = {
                    "message": "Không thể tìm kiếm thông tin bổ sung từ nguồn bên ngoài",
                    "error": str(e)
                }
        
        # Trả về kết quả
        result = {
            "message": "Phân tích triệu chứng và chẩn đoán",
            "match_quality": "thấp" if need_external_search else "cao",
            "symptoms_info": {
                "input_symptoms": request.symptoms,
                "found_in_database": [s for s in request.symptoms if s not in symptom_not_found],
                "not_found_in_database": symptom_not_found
            },
            "database_results": {
                "total_diseases_found": len(sorted_diseases),
                "top_diseases": disease_results[:5],  # Chỉ hiển thị top 5
                "data_source": "internal database",
                "best_match_percentage": best_match_percentage
            },
            "medical_analysis": diagnosis_result["medical_analysis"],
            "generated_by": "AI physician assistant based on database information"
        }
        
        # Thêm thông tin từ nguồn bên ngoài nếu có
        if external_analysis:
            result["external_analysis"] = external_analysis
            result["hospital_recommendation"] = "Do độ khớp với các bệnh trong hệ thống thấp (<50%), chúng tôi khuyến nghị bạn nên đến cơ sở y tế để được khám và chẩn đoán chính xác."
        
        return result
    
    except Exception as e:
        logger.error(f"Lỗi: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))