import { useEffect, useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { supabase } from './lib/supabase';
import Auth from './components/Auth';
import Chat from './components/Chat';
import WeatherWidget from './components/WeatherWidget';
import TouristGuide from './components/TouristGuide';

function App() {
  const [session, setSession] = useState(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <>
      <Toaster position="top-right" />
      {!session ? (
        <Auth />
      ) : (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Dashboard
              </h1>
              <button
                onClick={() => supabase.auth.signOut()}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                Sign Out
              </button>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              <div className="lg:col-span-3">
                <Chat />
              </div>
              <div className="space-y-8">
                <WeatherWidget />
                <TouristGuide />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default App;