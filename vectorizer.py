from sklearn.feature_extraction.text import TfidfVectorizer

def symptoms_to_vector(symptoms, all_symptoms):
    """
    Chuyển danh sách triệu chứng thành vector sử dụng TfidfVectorizer.
    :param symptoms: Danh sách triệu chứng nhập vào từ bệnh nhân.
    :param all_symptoms: Danh sách tất cả triệu chứng trong cơ sở dữ liệu.
    :return: Vector biểu diễn triệu chứng.
    """
    if not all_symptoms:
        raise ValueError("Danh sách triệu chứng từ cơ sở dữ liệu bị rỗng.")
    if not symptoms:
        raise ValueError("Danh sách triệu chứng đầu vào bị rỗng.")

    vectorizer = TfidfVectorizer()
    vectorizer.fit(all_symptoms)  # Huấn luyện trên tất cả triệu chứng
    symptom_vector = vectorizer.transform([' '.join(symptoms)])  # Chuyển triệu chứng nhập vào thành vector
    return symptom_vector