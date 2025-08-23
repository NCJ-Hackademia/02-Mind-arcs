// Person 2 → Upload / capture image
import React, { useState, useRef } from 'react';

const ImageUploader = ({ onImageReady }) => {
  const [image, setImage] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setImage(url);
      onImageReady(file);
    }
  };

  const startCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      videoRef.current.play();
    } catch (err) {
      console.error('Error accessing camera:', err);
    }
  };

  const captureImage = () => {
    canvasRef.current.width = videoRef.current.videoWidth;
    canvasRef.current.height = videoRef.current.videoHeight;
    canvasRef.current.getContext('2d').drawImage(videoRef.current, 0, 0);
    const dataUrl = canvasRef.current.toDataURL('image/png');
    setImage(dataUrl);
    // Convert to file for API
    canvasRef.current.toBlob((blob) => {
      const file = new File([blob], 'captured.png', { type: 'image/png' });
      onImageReady(file);
    });
  };

  return (
    <div className="mb-4">
      <h5>Upload or Capture Image</h5>
      <input type="file" accept="image/*" onChange={handleFileChange} className="form-control mb-2" />
      <button onClick={startCapture} className="btn btn-secondary">Start Camera</button>
      <button onClick={captureImage} className="btn btn-secondary ms-2">Capture</button>
      <video ref={videoRef} style={{ display: 'block', maxWidth: '100%' }}></video>
      <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
      {image && <img src={image} alt="Uploaded" className="img-fluid mt-2" />}
    </div>
  );
};

export default ImageUploader;