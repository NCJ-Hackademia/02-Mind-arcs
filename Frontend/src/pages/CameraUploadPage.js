// src/pages/CameraUploadPage.js
import React, { useRef, useEffect, useState } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';

// 🔊 Utility function for TTS
function speakText(text) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US"; 
    utterance.rate = 1;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  }
}

export default function CameraUploadPage() {
  const videoRef = useRef(null);
  const [useCamera, setUseCamera] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [detectedResult, setDetectedResult] = useState(null); // backend result

  useEffect(() => {
    let stream;
    if (useCamera) {
      const startCamera = async () => {
        try {
          stream = await navigator.mediaDevices.getUserMedia({ video: true });
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        } catch (err) {
          console.error("Camera error:", err);
        }
      };
      startCamera();
    }

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [useCamera]);

  const handleFileUpload = (event) => {
    setSelectedImage(URL.createObjectURL(event.target.files[0]));
    setUseCamera(false);
  };

  // 🔹 Upload image and fetch processed data
  const uploadImageToBackend = async () => {
    if (!selectedImage) return;

    const fileInput = document.querySelector('input[type="file"]');
    if (!fileInput || !fileInput.files[0]) return;

    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("image", file);
    formData.append("preferences", JSON.stringify(["grayscale","deuteranopia"]));
    formData.append("ocr_language", "eng");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/upload-image/", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setDetectedResult(data);

      // 🔊 Speak OCR text
      if (data.extracted_text) {
        speakText(data.extracted_text);
      }
    } catch (err) {
      console.error("Error uploading image:", err);
    }
  };

  return (
    <div className="container mt-5 text-center">
      <h2>Upload a Picture or Use Live Camera</h2>

      <div className="mt-4">
        <button 
          className="btn btn-primary m-2"
          onClick={() => setUseCamera(true)}
        >
          Use Camera
        </button>

        <input 
          type="file"
          accept="image/*"
          className="form-control mt-3"
          onChange={handleFileUpload}
        />
      </div>

      {/* Container for image/video + button */}
      <div className="mt-4 upload-container">
        {useCamera && (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            style={{ width: "100%", maxWidth: "500px", borderRadius: "10px" }}
          />
        )}

        {selectedImage && (
          <img 
            src={selectedImage}
            alt="Uploaded preview"
            className="img-fluid rounded uploaded-image"
            style={{ maxWidth: "500px" }}
          />
        )}

        <button 
          className="btn btn-success mt-3 result-button" 
          onClick={uploadImageToBackend}
        >
          Process Image & Speak
        </button>
      </div>

      {detectedResult && (
        <div className="mt-4 alert alert-info">
          <p><b>OCR Text:</b> {detectedResult.extracted_text}</p>
          {detectedResult.processed_image_url && (
            <img 
              src={detectedResult.processed_image_url} 
              alt="Processed" 
              className="img-fluid rounded mt-3"
              style={{ maxWidth: "500px" }}
            />
          )}
          <p><b>Applied Filters:</b> {detectedResult.applied_filters.join(", ")}</p>
        </div>
      )}
    </div>
  );
}
