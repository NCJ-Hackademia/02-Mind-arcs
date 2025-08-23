/*import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export const analyzeImage = async (imageFile, colorblindType) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('type', colorblindType);

  const response = await axios.post(`${API_BASE_URL}/analyze`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};*/
export const analyzeImage = async (imageFile, colorblindType) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        colors: ['Red', 'Green'],
        text: 'Sample description',
        meaning: 'Test meaning'
      });
    }, 1000);
  });
};