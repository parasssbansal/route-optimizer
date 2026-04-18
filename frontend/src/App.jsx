import { useState } from 'react';
import axios from 'axios';
import MapView from './components/MapView';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';

export default function App() {
  const [locations, setLocations] = useState([]);
  const [route, setRoute] = useState([]);
  const [distanceKm, setDistanceKm] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const canOptimize = locations.length >= 2 && !loading;

  const handleAddLocation = (coordinate) => {
    if (locations.length >= 10) {
      setError('You can add up to 10 locations per optimization request.');
      return;
    }

    setError('');
    setLocations((current) => [...current, coordinate]);
    setRoute([]);
    setDistanceKm(null);
  };

  const handleReset = () => {
    setLocations([]);
    setRoute([]);
    setDistanceKm(null);
    setError('');
  };

  const handleOptimize = async () => {
    if (locations.length < 2) {
      setError('Add at least two locations to optimize a route.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${apiBaseUrl}/optimize-route`, { locations });
      const data = response.data;

      if (!Array.isArray(data.optimal_route) || typeof data.total_distance_km !== 'number') {
        throw new Error('The backend returned an invalid response.');
      }

      setRoute(data.optimal_route);
      setDistanceKm(data.total_distance_km);
    } catch (requestError) {
      const message =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        'Unable to optimize the route right now.';
      setError(message);
      setRoute([]);
      setDistanceKm(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">Route Planner</p>
          <h1>Optimize your stops with live road distances.</h1>
          <p className="description">
            Click anywhere on the map to add delivery points, then let the optimizer compute the
            most efficient order using OSRM road distances and dynamic programming.
          </p>
        </div>
        <div className="control-card">
          <div className="stat-row">
            <span>Stops</span>
            <strong>{locations.length}</strong>
          </div>
          <div className="stat-row">
            <span>Total Distance</span>
            <strong>{distanceKm !== null ? `${distanceKm.toFixed(2)} km` : 'Not calculated'}</strong>
          </div>
          <div className="button-row">
            <button type="button" className="primary-btn" onClick={handleOptimize} disabled={!canOptimize}>
              {loading ? 'Optimizing...' : 'Optimize Route'}
            </button>
            <button type="button" className="secondary-btn" onClick={handleReset} disabled={loading}>
              Reset
            </button>
          </div>
          {error && <p className="error-banner">{error}</p>}
          <p className="hint">Maximum 10 stops per request to keep routing fast and reliable.</p>
        </div>
      </section>

      <section className="map-panel">
        <MapView locations={locations} route={route} onAddLocation={handleAddLocation} />
      </section>

      <section className="list-panel">
        <h2>Selected Locations</h2>
        {locations.length === 0 ? (
          <p className="empty-state">No points added yet. Click the map to place your first stop.</p>
        ) : (
          <ol className="location-list">
            {locations.map(([lat, lon], index) => (
              <li key={`${lat}-${lon}-${index}`}>
                <span>Stop {index + 1}</span>
                <code>
                  {lat}, {lon}
                </code>
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  );
}
