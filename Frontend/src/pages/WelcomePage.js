import React from "react";
import { Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

export default function WelcomePage() {
  return (
    <div className="container text-center mt-5">
      <div className="card shadow-lg p-5">
        <h1 className="mb-4">👋 Welcome to ColourAid</h1>
        <p className="lead">
          An AI-powered assistive tool to help people with colour blindness
          understand signs and text.
        </p>
        <Link to="/userinfo">
          <button className="btn btn-primary btn-lg mt-3">Get Started</button>
        </Link>
      </div>
    </div>
  );
}

