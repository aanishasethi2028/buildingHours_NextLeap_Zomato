import React, { useState } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import SearchCard from './components/SearchCard';
import AICurationBox from './components/AICurationBox';
import RestaurantCard from './components/RestaurantCard';

export default function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [summary, setSummary] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (prefs) => {
    setLoading(true);
    setHasSearched(true);
    setError(null);
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/recommend', prefs);
      setRecommendations(response.data.recommendations || []);
      setSummary(response.data.summary || '');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Our concierge is currently unavailable. Please try again later.");
      setRecommendations([]);
      setSummary('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Navbar />
      <div style={{ padding: '0 var(--spacing-xxl)', maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* SearchCard remains visible and interactive */}
        <SearchCard onSearch={handleSearch} loading={loading} />
        
        {loading && (
          <div style={{ textAlign: 'center', margin: '60px 0', fontSize: '18px', color: 'var(--text-muted)' }}>
            ✨ Curating your dining experience...
          </div>
        )}
        
        {error && (
          <div style={{ textAlign: 'center', margin: '40px auto 60px auto', maxWidth: '600px' }}>
            <div style={{ color: 'var(--primary)', fontSize: '18px', fontWeight: '600' }}>{error}</div>
            <button className="btn-primary" style={{ marginTop: '20px' }} onClick={() => setError(null)}>
              Clear Error
            </button>
          </div>
        )}

        {!loading && hasSearched && !error && (
          <div style={{ marginTop: '40px' }}>
            {recommendations.length > 0 ? (
              <>
                <AICurationBox summary={summary} />
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                  gap: 'var(--spacing-lg)',
                  paddingBottom: 'var(--spacing-xxl)'
                }}>
                  {recommendations.map(r => (
                    <RestaurantCard key={r.restaurant.id} item={r} />
                  ))}
                </div>
              </>
            ) : (
              <div style={{ textAlign: 'center', margin: '80px 0' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '18px', marginBottom: '20px' }}>
                  No exclusive tables found matching your criteria.
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
