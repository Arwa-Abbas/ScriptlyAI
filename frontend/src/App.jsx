import React, { useState } from 'react';
import './App.css';

const API_BASE = 'http://localhost:8000/api';  // Port 8000 for FastAPI

function App() {
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    description: '',
    price: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState('checking');

  // Test backend connection on component load
  React.useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      if (response.ok) {
        const data = await response.json();
        setBackendStatus(`connected - ${data.status}`);
      } else {
        setBackendStatus('error - health check failed');
      }
    } catch (err) {
      setBackendStatus('disconnected - cannot reach backend');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      console.log('Sending request to:', `${API_BASE}/generate-script`);
      console.log('Data:', formData);

      const response = await fetch(`${API_BASE}/generate-script`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Response data:', data);

      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || 'Something went wrong');
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setError(`Failed to connect to backend. Error: ${err.message}. Please make sure the backend server is running on port 8000.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎬 Marketing Script Assistant</h1>
        <p>Generate professional marketing scripts for your products</p>
        <div className="backend-status">
          Backend Status: <span className={`status-${backendStatus.includes('connected') ? 'connected' : 'error'}`}>
            {backendStatus}
          </span>
        </div>
        <div className="api-info">
          API URL: {API_BASE}
        </div>
      </header>

      <div className="container">
        <form onSubmit={handleSubmit} className="product-form">
          <div className="form-group">
            <label htmlFor="name">Product Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Enter product name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="category">Product Category</label>
            <input
              type="text"
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              placeholder="e.g., Electronics, Kitchen, Fashion"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Product Description *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              rows="4"
              placeholder="Describe your product features, benefits, and target audience..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="price">Price ($)</label>
            <input
              type="number"
              id="price"
              name="price"
              value={formData.price}
              onChange={handleChange}
              placeholder="e.g., 99.99"
              step="0.01"
            />
          </div>

          <button 
            type="submit" 
            disabled={loading || backendStatus.includes('disconnected')} 
            className="generate-btn"
          >
            {loading ? 'Generating...' : 'Generate Marketing Scripts'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            ❌ {error}
            <div className="troubleshooting">
              <h4>Troubleshooting Steps:</h4>
              <ol>
                <li>Make sure backend is running on port <strong>8000</strong></li>
                <li>Check if you can visit <a href={`${API_BASE}/health`} target="_blank" rel="noopener noreferrer">{`${API_BASE}/health`}</a></li>
                <li>Verify no other applications are using port <strong>8000</strong></li>
                <li>Check backend terminal for errors</li>
                <li>Test API directly at <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">http://localhost:8000/docs</a></li>
              </ol>
            </div>
          </div>
        )}

        {result && (
          <div className="results">
            <div className="result-section">
              <h2>📦 Similar Products Found</h2>
              <div className="similar-products">
                {result.similar_products.map((product, index) => (
                  <div key={index} className="product-card">
                    <h3>{product.name}</h3>
                    <p>Category: {product.category}</p>
                    <p>Price: {product.price ? `$${product.price}` : 'Not specified'}</p>
                    <p>Similarity: {(product.similarity * 100).toFixed(1)}%</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="result-section">
              <h2>🎥 Video Marketing Script</h2>
              <div className="script-content">
                {result.marketing_content.video_script.split('\n').map((line, index) => (
                  <p key={index}>{line}</p>
                ))}
              </div>
            </div>

            <div className="result-section">
              <h2>📱 Social Media Content</h2>
              <div className="social-content">
                {result.marketing_content.social_media_posts.split('\n').map((line, index) => (
                  <p key={index}>{line}</p>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;