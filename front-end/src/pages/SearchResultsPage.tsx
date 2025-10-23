import React from 'react';
import { useSearchParams } from 'react-router-dom';
import Header from '../components/Header';
import SearchResults from '../components/SearchResults';
import NearbyLocations from '../components/NearbyLocations';

function SearchResultsPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 bg-gray-50">
        <SearchResults searchQuery={query} />
        <NearbyLocations />
      </main>
    </div>
  );
}

export default SearchResultsPage;
