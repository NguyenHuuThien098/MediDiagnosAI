import requests
import os
import json
from dotenv import load_dotenv
import logging
import time

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tải các biến môi trường từ file .env
load_dotenv()

# URL của Gemini Healthcare API
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Lấy API Key từ biến môi trường
API_KEY = os.getenv("GEMINI_API_KEY")

def query_gemini_api_for_diagnosis(symptoms, top_diseases, mapped_symptoms):
    """
    Gửi triệu chứng và danh sách bệnh ưu tiên đến Gemini để nhận chẩn đoán y khoa.
    :param symptoms: Danh sách triệu chứng gốc của bệnh nhân.
    :param top_diseases: Danh sách bệnh ưu tiên cao từ cơ sở dữ liệu (đã kèm thông tin chi tiết).
    :param mapped_symptoms: Danh sách các triệu chứng đã được map với cơ sở dữ liệu.
    :return: Kết quả chẩn đoán từ API.
    """
    if not API_KEY:
        raise Exception("API Key không được tìm thấy. Vui lòng kiểm tra file .env.")

    symptoms_str = ", ".join(symptoms)
    
    # Kiểm tra độ khớp của bệnh có thấp không
    best_match_percentage = top_diseases[0]["match_percentage"] if top_diseases else 0
    low_match_quality = best_match_percentage < 50
    
    # Tạo thông tin chi tiết về các bệnh để Gemini phân tích
    diseases_details = ""
    for i, disease in enumerate(top_diseases):
        diseases_details += f"\n{i+1}. {disease['name_en']} ({disease['match_percentage']}% khớp):\n"
        diseases_details += f"   - Triệu chứng khớp ({disease['matching_symptoms_count']}/{disease['total_symptoms_count']}): {', '.join(disease['matching_symptoms'])}\n"
        if disease['description'] and disease['description'] != "Không có mô tả chi tiết":
            # Rút gọn mô tả nếu quá dài
            description = disease['description']
            if len(description) > 500:
                description = description[:500] + "..."
            diseases_details += f"   - Mô tả: {description}\n"
    
    # Điều chỉnh prompt dựa vào độ khớp
    match_quality_text = ""
    if low_match_quality:
        match_quality_text = "\nLƯU Ý QUAN TRỌNG: Các bệnh trong danh sách có độ khớp thấp với các triệu chứng được cung cấp (<50%). Hãy đưa ra một số lý do tại sao và nhấn mạnh sự cần thiết phải tham khảo ý kiến bác sĩ trực tiếp."
    
    prompt = f"""
Hãy đóng vai một bác sĩ đa khoa giàu kinh nghiệm đang chẩn đoán bệnh cho bệnh nhân. Dựa trên thông tin sau:

TRIỆU CHỨNG BÁO CÁO: {symptoms_str}

CÁC BỆNH PHÙ HỢP NHẤT TỪ CƠ SỞ DỮ LIỆU Y KHOA: {diseases_details}{match_quality_text}

Hãy phân tích và đưa ra:
1. CHẨN ĐOÁN CHÍNH: Phân tích 2-3 bệnh có khả năng cao nhất từ danh sách trên, giải thích tại sao triệu chứng phù hợp với từng bệnh
2. CÁC XÉT NGHIỆM CẦN THỰC HIỆN: 2-3 xét nghiệm quan trọng nhất để xác định chính xác chẩn đoán
3. KHUYẾN NGHỊ: Hướng dẫn chuyên nghiệp cho bệnh nhân và các bước tiếp theo

LƯU Ý QUAN TRỌNG: 
- Chỉ phân tích các bệnh từ danh sách đã cung cấp, không đưa ra bệnh khác ngoài danh sách
- Tập trung vào bệnh có tỷ lệ khớp cao nhất và số lượng triệu chứng khớp nhiều nhất
- Trả lời như một bác sĩ chuyên nghiệp, ngắn gọn và chính xác
- {"Nhấn mạnh rằng nên đến gặp bác sĩ để thăm khám trực tiếp do độ khớp với các bệnh thấp" if low_match_quality else ""}
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        logger.info(f"Gửi yêu cầu đến Gemini API với {len(symptoms)} triệu chứng")
        response = requests.post(f"{API_URL}?key={API_KEY}", json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        logger.info("Nhận phản hồi thành công từ Gemini API")
        
        # Trích xuất kết quả phân tích
        medical_analysis = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        return {
            "medical_analysis": medical_analysis
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi khi gọi Gemini API: {str(e)}")
        return {
            "medical_analysis": "Không thể tạo phân tích y khoa do lỗi kết nối với API. Vui lòng thử lại sau."
        }

def search_disease_external(symptoms=None, disease_name=None):
    """
    Tìm kiếm thông tin bệnh từ nguồn bên ngoài khi không có trong database hoặc độ khớp thấp.
    
    :param symptoms: Danh sách triệu chứng (nếu tìm theo triệu chứng)
    :param disease_name: Tên bệnh (nếu tìm theo tên bệnh)
    :return: Thông tin bệnh từ nguồn bên ngoài
    """
    if not API_KEY:
        raise Exception("API Key không được tìm thấy. Vui lòng kiểm tra file .env.")
    
    # Xây dựng prompt dựa vào thông tin đầu vào
    prompt = ""
    if symptoms:
        symptoms_str = ", ".join(symptoms)
        prompt = f"""
Hãy đóng vai một bác sĩ chuyên khoa và phân tích các triệu chứng sau: {symptoms_str}

1. Liệt kê 3-5 bệnh có thể liên quan nhất dựa trên các triệu chứng này, kèm theo mô tả ngắn gọn về mỗi bệnh
2. Với mỗi bệnh, giải thích tại sao nó phù hợp với các triệu chứng đã nêu
3. Đề xuất 2-3 xét nghiệm cần thực hiện để xác định chẩn đoán
4. Đưa ra lời khuyên y tế cho bệnh nhân dựa trên các triệu chứng này
5. Khuyến nghị rõ ràng về việc cần tham khảo ý kiến bác sĩ và loại bác sĩ chuyên khoa nào nên gặp

QUAN TRỌNG: Với mỗi bệnh được đề cập, hãy cung cấp ít nhất một nguồn tham khảo y khoa đáng tin cậy (URL đầy đủ, tên bài báo, hoặc tên sách y khoa và tác giả). Ví dụ: "Theo Mayo Clinic (https://www.mayoclinic.org/diseases-conditions/disease-name/symptoms-causes/syc-12345)"
"""
    elif disease_name:
        prompt = f"""
Hãy cung cấp thông tin y khoa chi tiết về bệnh: {disease_name}

Bao gồm các phần:
1. Định nghĩa và mô tả tổng quan về bệnh
2. Nguyên nhân chính
3. Các triệu chứng phổ biến và dấu hiệu cần chú ý
4. Phương pháp chẩn đoán tiêu chuẩn
5. Các biện pháp điều trị thường được áp dụng
6. Tiên lượng và biến chứng có thể xảy ra

QUAN TRỌNG: Hãy cung cấp ít nhất hai nguồn tham khảo y khoa đáng tin cậy cho thông tin này (URL đầy đủ, tên bài báo, hoặc tên sách y khoa và tác giả). Ví dụ: "Theo Mayo Clinic (https://www.mayoclinic.org/diseases-conditions/disease-name/symptoms-causes/syc-12345)"
"""
    else:
        raise ValueError("Cần cung cấp triệu chứng hoặc tên bệnh để tìm kiếm.")
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    
    try:
        logger.info(f"Tìm kiếm thông tin y tế bổ sung từ nguồn bên ngoài")
        response = requests.post(f"{API_URL}?key={API_KEY}", json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Trích xuất phần text từ kết quả
        information = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        # Thêm thông báo rõ ràng về nguồn
        disclaimer = "Lưu ý: Thông tin này được cung cấp như một tham khảo bổ sung do các kết quả từ cơ sở dữ liệu có độ khớp thấp hoặc không đủ. Vui lòng tham khảo ý kiến bác sĩ trước khi áp dụng bất kỳ thông tin y tế nào."
        
        # Thêm thời gian tìm kiếm
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "information": information,
            "source": "Gemini AI Physician Knowledge Base",
            "searched_at": timestamp,
            "disclaimer": disclaimer
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi khi tìm kiếm thông tin bên ngoài: {str(e)}")
        raise Exception(f"Error searching external information: {e}")