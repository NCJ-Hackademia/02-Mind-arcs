import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function ColorBlindnessPage() {
  const [selected, setSelected] = useState("");

  return (
    <div className="container mt-5">
      <div className="card shadow p-4">
        <h2 className="mb-4">Select Your Color Blindness Type</h2>

        <div className="form-check">
          <input type="radio" name="cb" value="Protanopia" className="form-check-input"
            onChange={(e) => setSelected(e.target.value)} />
          <label className="form-check-label">Protanopia (Red-Blind)</label>
        </div>

        <div className="form-check">
          <input type="radio" name="cb" value="Deuteranopia" className="form-check-input"
            onChange={(e) => setSelected(e.target.value)} />
          <label className="form-check-label">Deuteranopia (Green-Blind)</label>
        </div>

        <div className="form-check">
          <input type="radio" name="cb" value="Tritanopia" className="form-check-input"
            onChange={(e) => setSelected(e.target.value)} />
          <label className="form-check-label">Tritanopia (Blue-Blind)</label>
        </div>

        <div className="form-check">
          <input type="radio" name="cb" value="Other" className="form-check-input"
            onChange={(e) => setSelected(e.target.value)} />
          <label className="form-check-label">Other / Not Sure</label>
        </div>

        <Link to="/camera">
          <button className="btn btn-success w-100 mt-4">Next</button>
        </Link>
      </div>
    </div>
  );
}


