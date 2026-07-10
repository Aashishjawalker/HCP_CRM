import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateFormField, resetForm, clearFeedback, submitFormData } from '../store/interactionSlice';

const SENTIMENT_OPTIONS = ['Positive', 'Neutral', 'Negative'];
const TYPE_OPTIONS = ['Meeting', 'Call', 'Email', 'Other'];

export default function StructuredForm() {
  const dispatch = useDispatch();
  const { currentForm, submitSuccess, submitError, loading } = useSelector(
    (state) => state.interactions
  );

  const [localErrors, setLocalErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    dispatch(updateFormField({ field: name, value }));
    if (localErrors[name]) {
      setLocalErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const validate = () => {
    const errors = {};
    if (!currentForm.hcpName.trim()) errors.hcpName = 'HCP name is required';
    if (!currentForm.date.trim()) errors.date = 'Date is required';
    if (!currentForm.time.trim()) errors.time = 'Time is required';
    setLocalErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(clearFeedback());
    if (!validate()) return;

    dispatch(submitFormData({
      hcp_name: currentForm.hcpName,
      interaction_type: currentForm.interactionType,
      date: currentForm.date,
      time: currentForm.time,
      attendees: currentForm.attendees,
      topics_discussed: currentForm.topicsDiscussed,
      sentiment: currentForm.sentiment.toLowerCase(),
      materials_shared: currentForm.materialsShared,
    }));
  };

  const handleReset = () => {
    dispatch(clearFeedback());
    dispatch(resetForm());
    setLocalErrors({});
  };

  return (
    <form className="structured-form" onSubmit={handleSubmit} noValidate>
      <h2 className="form-title">Interaction Details</h2>

      <div className="form-group">
        <label htmlFor="hcpName">HCP Name *</label>
        <input
          id="hcpName"
          name="hcpName"
          type="text"
          placeholder="e.g. Dr. Sharma"
          value={currentForm.hcpName}
          onChange={handleChange}
          className={localErrors.hcpName ? 'input-error' : ''}
        />
        {localErrors.hcpName && <span className="error-text">{localErrors.hcpName}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="interactionType">Interaction Type</label>
        <select
          id="interactionType"
          name="interactionType"
          value={currentForm.interactionType}
          onChange={handleChange}
        >
          {TYPE_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="date">Date *</label>
        <input
          id="date"
          name="date"
          type="date"
          value={currentForm.date}
          onChange={handleChange}
          className={localErrors.date ? 'input-error' : ''}
        />
        {localErrors.date && <span className="error-text">{localErrors.date}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="time">Time *</label>
        <input
          id="time"
          name="time"
          type="time"
          value={currentForm.time}
          onChange={handleChange}
          className={localErrors.time ? 'input-error' : ''}
        />
        {localErrors.time && <span className="error-text">{localErrors.time}</span>}
      </div>

      {/* Attendees */}
      <div className="form-group">
        <label htmlFor="attendees">Attendees</label>
        <input
          id="attendees"
          name="attendees"
          type="text"
          placeholder="e.g. Dr. Sharma, Dr. Patel"
          value={currentForm.attendees}
          onChange={handleChange}
        />
      </div>

      {/* Topics Discussed */}
      <div className="form-group">
        <label htmlFor="topicsDiscussed">Topics Discussed</label>
        <textarea
          id="topicsDiscussed"
          name="topicsDiscussed"
          placeholder="e.g. New product launch, clinical data"
          rows={3}
          value={currentForm.topicsDiscussed}
          onChange={handleChange}
        />
      </div>

      {/* Sentiment */}
      <div className="form-group">
        <label htmlFor="sentiment">Sentiment</label>
        <select
          id="sentiment"
          name="sentiment"
          value={currentForm.sentiment}
          onChange={handleChange}
        >
          {SENTIMENT_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>

      {/* Materials Shared */}
      <div className="form-group">
        <label htmlFor="materialsShared">Materials Shared</label>
        <input
          id="materialsShared"
          name="materialsShared"
          type="text"
          placeholder="e.g. Brochure, Sample"
          value={currentForm.materialsShared}
          onChange={handleChange}
        />
      </div>

      {/* Feedback messages */}
      {submitSuccess && <div className="feedback feedback-success">{submitSuccess}</div>}
      {submitError && <div className="feedback feedback-error">{submitError}</div>}

      {/* Buttons */}
      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Submitting…' : 'Submit Interaction'}
        </button>
        <button type="button" className="btn btn-secondary" onClick={handleReset}>
          Reset
        </button>
      </div>
    </form>
  );
}
