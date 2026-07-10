import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchInteractions, deleteInteractionThunk, clearFeedback } from '../store/interactionSlice';

export default function InteractionList() {
  const dispatch = useDispatch();
  const { list, loading, error, submitSuccess } = useSelector((state) => state.interactions);

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  const handleDelete = (id) => {
    if (window.confirm(`Delete interaction #${id}?`)) {
      dispatch(deleteInteractionThunk(id));
    }
  };

  useEffect(() => {
    if (submitSuccess) {
      const t = setTimeout(() => dispatch(clearFeedback()), 3000);
      return () => clearTimeout(t);
    }
  }, [submitSuccess, dispatch]);

  if (loading && list.length === 0) return <div className="interaction-list"><p>Loading...</p></div>;
  if (error) return <div className="interaction-list"><p className="feedback feedback-error">{error}</p></div>;

  return (
    <div className="interaction-list">
      <h2 className="form-title">All Interactions</h2>
      {submitSuccess && <div className="feedback feedback-success">{submitSuccess}</div>}
      {list.length === 0 ? (
        <p>No interactions logged yet.</p>
      ) : (
        <table className="interaction-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>HCP</th>
              <th>Type</th>
              <th>Date</th>
              <th>Topics</th>
              <th>Sentiment</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {list.map((ix) => (
              <tr key={ix.id}>
                <td>{ix.id}</td>
                <td>{ix.hcp_name}</td>
                <td>{ix.interaction_type}</td>
                <td>{ix.date}</td>
                <td>{ix.topics_discussed || '—'}</td>
                <td>{ix.sentiment}</td>
                <td>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(ix.id)}
                    disabled={loading}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
