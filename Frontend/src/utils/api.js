import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const analyzeImage = async (imageFile, colorblindType) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('preferences', JSON.stringify([colorblindType]));
  formData.append('ocr_language', 'eng');

  const response = await axios.post(`${API_BASE_URL}/upload-image/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};