// src/pages/CameraUploadPage.js
import React, { useRef, useEffect, useState } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';

// 🔊 Utility function for TTS
function speakText(text, priority = 'normal') {
  if ("speechSynthesis" in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = priority === 'high' ? 0.7 : 0.8; // Slower for important alerts
    utterance.pitch = priority === 'high' ? 1.2 : 1;
    utterance.volume = 1;
    
    // Stop any current speech for high priority alerts
    if (priority === 'high') {
      window.speechSynthesis.cancel();
    }
    
    window.speechSynthesis.speak(utterance);
  } else {
    console.warn("Speech synthesis not supported in this browser.");
  }
};

// 🔊 Handle audio feedback - simplified without sign alerts
const handleAudioFeedback = (data) => {
  // Play audio message or extracted text
  if (data.audio_message) {
    speakText(data.audio_message);
  } else if (data.extracted_text) {
    speakText(`Text detected: ${data.extracted_text}`);
  }
};

export default function CameraUploadPage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
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

  // 🔹 Capture image from live camera
  const captureImage = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      const file = new File([blob], "captured.png", { type: "image/png" });
      setSelectedImage(URL.createObjectURL(file));

      // store file in a ref for backend upload
      canvas.file = file;
    });
  };

  // 🔹 Upload image and fetch processed data
  const uploadImageToBackend = async () => {
    let file = null;

    // prefer captured file from canvas if camera used
    if (useCamera && canvasRef.current?.file) {
      file = canvasRef.current.file;
    } else {
      const fileInput = document.querySelector('input[type="file"]');
      if (!fileInput || !fileInput.files[0]) {
        alert("Please select an image first!");
        return;
      }
      file = fileInput.files[0];
    }

    // Show loading state
    setDetectedResult({ loading: true });
    
    const formData = new FormData();
    formData.append("image", file);
    formData.append("preferences", JSON.stringify(["grayscale", "deuteranopia"]));
    formData.append("ocr_language", "eng");

    try {
      console.log("Sending request to backend...");
      const res = await fetch("http://127.0.0.1:8000/api/upload-image/", {
        method: "POST",
        body: formData,
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      console.log("Backend response:", data);
      setDetectedResult(data);

      // 🔊 Enhanced Audio Feedback
      handleAudioFeedback(data);
    } catch (err) {
      console.error("Error uploading image:", err);
      setDetectedResult({ error: `Failed to analyze image: ${err.message}` });
      alert(`Error: ${err.message}. Make sure the backend server is running on port 8000.`);
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

      {/* Video + canvas + capture button */}
      <div className="mt-4 upload-container">
        {useCamera && (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              style={{ width: "100%", maxWidth: "500px", borderRadius: "10px" }}
            />
            <button
              className="btn btn-warning mt-2"
              onClick={captureImage}
            >
              Capture Image
            </button>
            <canvas ref={canvasRef} style={{ display: "none" }} />
          </>
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
          disabled={!selectedImage && (!useCamera || !canvasRef.current?.file)}
        >
          {detectedResult?.loading ? "🔄 Analyzing..." : "🔍 Analyze Image with AI"}
        </button>
      </div>

      {detectedResult?.loading && (
        <div className="mt-4 alert alert-info">
          <div className="d-flex align-items-center">
            <div className="spinner-border spinner-border-sm me-2" role="status"></div>
            <span>Analyzing image with AI... Please wait.</span>
          </div>
        </div>
      )}

      {detectedResult?.error && (
        <div className="mt-4 alert alert-danger">
          <strong>❌ Error:</strong> {detectedResult.error}
        </div>
      )}

      {detectedResult && !detectedResult.loading && !detectedResult.error && (
        <div className="mt-4">
          <div className="result-section">
            <h4>🔍 AI Detection Results:</h4>
            

            {/* Extracted Text */}
            {detectedResult.extracted_text && (
              <div className="text-result" style={{
                backgroundColor: '#f8f9fa',
                border: '2px solid #000',
                borderRadius: '8px',
                padding: '20px',
                margin: '15px 0'
              }}>
                <strong style={{color: '#000'}}>📝 Extracted Text:</strong>
                <pre style={{
                  whiteSpace: 'pre-wrap', 
                  fontFamily: 'inherit',
                  color: '#000',
                  backgroundColor: '#fff',
                  border: '1px solid #000',
                  padding: '15px',
                  borderRadius: '5px',
                  margin: '10px 0'
                }}>{detectedResult.extracted_text}</pre>
                <button 
                  onClick={() => speakText(detectedResult.extracted_text)}
                  style={{
                    backgroundColor: '#000',
                    color: '#fff',
                    border: '2px solid #000',
                    padding: '8px 16px',
                    borderRadius: '5px',
                    cursor: 'pointer'
                  }}
                >
                  🔊 Read Text Again
                </button>
              </div>
            )}


            {/* Visual Objects */}
            {detectedResult.visual_objects && detectedResult.visual_objects.length > 0 && (
              <div className="objects-detected alert alert-secondary">
                <strong>👁️ Visual Objects:</strong>
                <ul>
                  {detectedResult.visual_objects.map((obj, idx) => (
                    <li key={idx}>
                      <span className="object-name">{obj.object}</span>
                      <span className="confidence"> ({Math.round(obj.confidence * 100)}% confidence)</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Audio Controls */}
            <div className="audio-controls mt-3">
              <button 
                onClick={() => handleAudioFeedback(detectedResult)}
                className="btn btn-success me-2"
              >
                🔊 Repeat All Audio
              </button>
              <button 
                onClick={() => window.speechSynthesis.cancel()}
                className="btn btn-secondary"
              >
                🔇 Stop Audio
              </button>
            </div>

            {/* Applied Filters */}
            {detectedResult.applied_filters && (
              <div className="filters-applied mt-3">
                <strong style={{color: '#000'}}>🎨 Filters Applied:</strong>
                <ul>
                  {detectedResult.applied_filters.map((filter, idx) => (
                    <li key={idx}>{filter}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Processed Image */}
            {detectedResult.processed_image_url && (
              <div className="mt-3">
                <strong>🖼️ Processed Image:</strong>
                <img 
                  src={detectedResult.processed_image_url} 
                  alt="Processed" 
                  className="img-fluid rounded mt-2"
                  style={{ maxWidth: "500px" }}
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
