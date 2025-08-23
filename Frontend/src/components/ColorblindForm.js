// Person 1 → User selects type of colorblindness
import React, { useState } from 'react';

const ColorblindForm = ({ onSelect }) => {
  const [type, setType] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (type) onSelect(type);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <label htmlFor="colorblindType" className="form-label">Select Colorblindness Type:</label>
      <select
        id="colorblindType"
        className="form-select"
        value={type}
        onChange={(e) => setType(e.target.value)}
        required
      >
        <option value="">Choose...</option>
        <option value="protanopia">Protanopia (Red-Green)</option>
        <option value="deuteranopia">Deuteranopia (Green-Red)</option>
        <option value="tritanopia">Tritanopia (Blue-Yellow)</option>
        <option value="achromatopsia">Achromatopsia (Monochrome)</option>
      </select>
      <button type="submit" className="btn btn-primary mt-2">Submit</button>
    </form>
  );
};

export default ColorblindForm;