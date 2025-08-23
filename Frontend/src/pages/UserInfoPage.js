import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function UserInfoPage() {
  const [form, setForm] = useState({ name: "", email: "", age: "", gender: "" });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  return (
    <div className="container mt-5">
      <div className="card shadow p-4">
        <h2 className="mb-4">User Information</h2>
        <form>
          <div className="mb-3">
            <label className="form-label">Name</label>
            <input type="text" name="name" className="form-control" onChange={handleChange} />
          </div>
          <div className="mb-3">
            <label className="form-label">Email</label>
            <input type="email" name="email" className="form-control" onChange={handleChange} />
          </div>
          <div className="mb-3">
            <label className="form-label">Age</label>
            <input type="number" name="age" className="form-control" onChange={handleChange} />
          </div>
          <div className="mb-3">
            <label className="form-label">Gender</label>
            <select name="gender" className="form-select" onChange={handleChange}>
              <option>Choose...</option>
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>
          </div>
        </form>

        <Link to="/colorblindness">
          <button className="btn btn-success w-100">Next</button>
        </Link>
      </div>
    </div>
  );
}
