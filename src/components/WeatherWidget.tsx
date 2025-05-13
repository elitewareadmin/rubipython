import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface WeatherData {
  temperature: number;
  condition: string;
  icon: string;
  location: string;
}

export default function WeatherWidget() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get user's location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(async (position) => {
        try {
          const response = await fetch(
            `https://api.openweathermap.org/data/2.5/weather?lat=${position.coords.latitude}&lon=${position.coords.longitude}&appid=${import.meta.env.VITE_OPENWEATHER_API_KEY}&units=metric`
          );
          const data = await response.json();
          
          setWeather({
            temperature: Math.round(data.main.temp),
            condition: data.weather[0].main,
            icon: `https://openweathermap.org/img/wn/${data.weather[0].icon}@2x.png`,
            location: data.name
          });
        } catch (error) {
          console.error('Error fetching weather:', error);
        } finally {
          setLoading(false);
        }
      });
    }
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse bg-gray-200 dark:bg-gray-700 rounded-lg p-4">
        <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-3/4 mb-2"></div>
        <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
      </div>
    );
  }

  if (!weather) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-lg"
    >
      <div className="flex items-center gap-4">
        <img src={weather.icon} alt={weather.condition} className="w-16 h-16" />
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {weather.location}
          </h3>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {weather.temperature}°C
          </p>
          <p className="text-gray-600 dark:text-gray-300">{weather.condition}</p>
        </div>
      </div>
    </motion.div>
  );
}