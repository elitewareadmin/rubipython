import { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { motion } from 'framer-motion';
import 'leaflet/dist/leaflet.css';

interface Place {
  name: string;
  type: string;
  rating: number;
  description: string;
  lat: number;
  lng: number;
}

export default function TouristGuide() {
  const [places, setPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedType, setSelectedType] = useState('restaurant');

  const searchNearbyPlaces = async (position: GeolocationPosition) => {
    setLoading(true);
    try {
      const response = await fetch(
        `https://api.foursquare.com/v3/places/search?ll=${position.coords.latitude},${position.coords.longitude}&radius=1000&categories=${selectedType}`,
        {
          headers: {
            Authorization: import.meta.env.VITE_FOURSQUARE_API_KEY,
          },
        }
      );
      const data = await response.json();
      
      setPlaces(data.results.map((place: any) => ({
        name: place.name,
        type: place.categories[0]?.name || 'Place',
        rating: place.rating || 0,
        description: place.description || 'No description available',
        lat: place.geocodes.main.latitude,
        lng: place.geocodes.main.longitude,
      })));
    } catch (error) {
      console.error('Error fetching places:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(searchNearbyPlaces);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-lg"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Tourist Guide
        </h3>
        <div className="flex gap-2">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="restaurant">Restaurants</option>
            <option value="hotel">Hotels</option>
            <option value="attraction">Attractions</option>
            <option value="museum">Museums</option>
          </select>
          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search Nearby'}
          </button>
        </div>
      </div>

      {places.length > 0 && (
        <div className="h-[400px] rounded-lg overflow-hidden">
          <MapContainer
            center={[places[0].lat, places[0].lng]}
            zoom={14}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            {places.map((place, index) => (
              <Marker key={index} position={[place.lat, place.lng]}>
                <Popup>
                  <div>
                    <h4 className="font-semibold">{place.name}</h4>
                    <p className="text-sm text-gray-600">{place.type}</p>
                    <p className="text-sm">Rating: {place.rating}/10</p>
                    <p className="text-sm mt-1">{place.description}</p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      )}

      <div className="mt-4 space-y-2">
        {places.map((place, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
          >
            <h4 className="font-semibold text-gray-900 dark:text-white">
              {place.name}
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              {place.type} • Rating: {place.rating}/10
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {place.description}
            </p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}