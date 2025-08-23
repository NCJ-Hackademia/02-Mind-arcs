import "./App.css";
import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import WelcomePage from "./pages/WelcomePage";
import UserInfoPage from "./pages/UserInfoPage";
import ColorBlindnessPage from "./pages/ColorBlindnessPage";
import CameraUploadPage from "./pages/CameraUploadPage";
import ResultPage from "./pages/ResultPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/userinfo" element={<UserInfoPage />} />
        <Route path="/colorblindness" element={<ColorBlindnessPage />} />
        <Route path="/camera" element={<CameraUploadPage />} />
        <Route path="/result" element={<ResultPage />} />
      </Routes>
    </Router>
  );
}

export default App;

