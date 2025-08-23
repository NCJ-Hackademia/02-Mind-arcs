import React from "react";
import { Link } from "react-router-dom";

export default function ResultPage() {
  return (
    <div className="container text-center mt-5">
      <div className="card shadow-lg p-5">
        <h2 className="mb-3">Result</h2>
        <p className="lead">
          Here we will show the processed sign/text after applying AI & color filters.
        </p>

        <div className="border rounded p-3 bg-light">
          <h4>🔎 Example Output</h4>
          <p>Detected Text: <b>Exit</b></p>
          <p>Translated for your vision: <span className="text-success">Green Exit</span></p>
        </div>

        <Link to="/">
          <button className="btn btn-primary mt-4">Go Home</button>
        </Link>
      </div>
    </div>
  );
}
