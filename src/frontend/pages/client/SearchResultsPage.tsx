import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCard from '../../components/common/LocationCard';
import { placeService } from '../../services';
import { Icons } from '../../config/constants';
import type { PlaceCompact } from '../../types/models';
import '../../assets/styles/pages/SearchResultsPage.css';

// Mock data fallback
const MOCK_LOCATIONS = [
  {
    id: 1,
    name: 'Hồ Gươm - Quận Hoàn Kiếm',
    district_id: 1,
    place_type_id: 1,
    rating_average: 4.5,
    price_min: 0,
    price_max: 0,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
  },
  {
    id: 2,
    name: 'Phố Cổ Hà Nội',
    district_id: 1,
    place_type_id: 2,
    rating_average: 4.2,
    price_min: 50000,
    price_max: 200000,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
  },
  {
    id: 3,
    name: 'Văn Miếu - Quốc Tử Giám',
    district_id: 2,
    place_type_id: 1,
    rating_average: 4.8,
    price_min: 30000,
    price_max: 50000,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
  },
];

const SearchResultsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  // State cho các section
  const [searchResults, setSearchResults] = useState<PlaceCompact[]>([]);
  const [nearbyPlaces, setNearbyPlaces] = useState<PlaceCompact[]>([]);
  const [suggestions, setSuggestions] = useState<PlaceCompact[]>([]);

  // Loading states
  const [isLoadingSearch, setIsLoadingSearch] = useState(true);
  const [isLoadingNearby, setIsLoadingNearby] = useState(true);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(true);

  // Lấy kết quả tìm kiếm
  const fetchSearchResults = useCallback(async () => {
    if (!query) {
      setSearchResults([]);
      setIsLoadingSearch(false);
      return;
    }

    setIsLoadingSearch(true);
    try {
      const response = await placeService.searchPlaces({ keyword: query, page: 1 });
      if (response.success && response.data.length > 0) {
        setSearchResults(response.data);
      } else {
        // Fallback to mock data
        setSearchResults(MOCK_LOCATIONS as PlaceCompact[]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults(MOCK_LOCATIONS as PlaceCompact[]);
    } finally {
      setIsLoadingSearch(false);
    }
  }, [query]);

  // Lấy địa điểm lân cận
  const fetchNearbyPlaces = useCallback(async () => {
    setIsLoadingNearby(true);
    try {
      // Thử lấy vị trí người dùng
      if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            try {
              const response = await placeService.getNearbyPlaces({
                lat: position.coords.latitude,
                long: position.coords.longitude,
              });
              if (response.success && response.data.length > 0) {
                setNearbyPlaces(response.data);
              } else {
                setNearbyPlaces(MOCK_LOCATIONS as PlaceCompact[]);
              }
            } catch {
              setNearbyPlaces(MOCK_LOCATIONS as PlaceCompact[]);
            } finally {
              setIsLoadingNearby(false);
            }
          },
          () => {
            // Không lấy được vị trí, dùng vị trí mặc định (Hà Nội)
            placeService.getNearbyPlaces({ lat: 21.0285, long: 105.8542 })
              .then((response) => {
                if (response.success && response.data.length > 0) {
                  setNearbyPlaces(response.data);
                } else {
                  setNearbyPlaces(MOCK_LOCATIONS as PlaceCompact[]);
                }
              })
              .catch(() => {
                setNearbyPlaces(MOCK_LOCATIONS as PlaceCompact[]);
              })
              .finally(() => {
                setIsLoadingNearby(false);
              });
          }
        );
      } else {
        // Không hỗ trợ geolocation
        const response = await placeService.getNearbyPlaces({ lat: 21.0285, long: 105.8542 });
        if (response.success && response.data.length > 0) {
          setNearbyPlaces(response.data);
        } else {
          setNearbyPlaces(MOCK_LOCATIONS as PlaceCompact[]);
        }
        setIsLoadingNearby(false);
      }
    } catch (error) {
      console.error('Nearby error:', error);
      setNearbyPlaces(MOCK_LOCATIONS as PlaceCompact[]);
      setIsLoadingNearby(false);
    }
  }, []);

  // Lấy gợi ý địa điểm
  const fetchSuggestions = useCallback(async () => {
    setIsLoadingSuggestions(true);
    try {
      const response = await placeService.getPlaces({ page: 1, limit: 5 });
      if (response.success && response.data.length > 0) {
        setSuggestions(response.data);
      } else {
        setSuggestions(MOCK_LOCATIONS as PlaceCompact[]);
      }
    } catch (error) {
      console.error('Suggestions error:', error);
      setSuggestions(MOCK_LOCATIONS as PlaceCompact[]);
    } finally {
      setIsLoadingSuggestions(false);
    }
  }, []);

  // Fetch data on mount và khi query thay đổi
  useEffect(() => {
    fetchSearchResults();
  }, [fetchSearchResults]);

  useEffect(() => {
    fetchNearbyPlaces();
    fetchSuggestions();
  }, [fetchNearbyPlaces, fetchSuggestions]);

  // Render skeleton loading
  const renderSkeleton = () => (
    <div className="scroll-container">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="place-card skeleton" style={{ minWidth: 280, height: 320 }} />
      ))}
    </div>
  );

  // Render location cards
  const renderLocationCards = (places: PlaceCompact[], keyPrefix: string) => (
    <div className="scroll-container">
      {places.map((place) => (
        <LocationCard
          key={`${keyPrefix}-${place.id}`}
          id={String(place.id)}
          imageSrc={place.main_image_url || 'https://via.placeholder.com/400x300'}
          title={place.name}
          address={place.address || place.district_name || 'Hà Nội'}
          priceMin={place.price_min}
          priceMax={place.price_max}
          rating={place.rating_average || 0}
          reviewCount={place.rating_count || 0}
        />
      ))}
    </div>
  );

  return (
    <>
      <Header />
      <div className="search-page">
        <div className="search-page__container">
          {/* Kết quả tìm kiếm */}
          <section className="search-section location-section">
            <div className="search-section__header">
              <h2 className="search-section__title">
                {query ? `Kết quả tìm kiếm cho: "${query}"` : 'Tất cả địa điểm'}
              </h2>
              {!isLoadingSearch && (
                <span className="search-section__count">
                  ({searchResults.length} kết quả)
                </span>
              )}
            </div>

            {isLoadingSearch ? renderSkeleton() : (
              searchResults.length > 0 ? (
                renderLocationCards(searchResults, 'result')
              ) : (
                <p className="search-empty">Không tìm thấy kết quả nào cho "{query}"</p>
              )
            )}
          </section>

          {/* Địa điểm lân cận */}
          <section className="search-section location-section">
            <div className="search-section__header">
              <h2 className="search-section__title">
                Địa điểm lân cận <Icons.Location className="title-icon" />
              </h2>
            </div>

            {isLoadingNearby ? renderSkeleton() : renderLocationCards(nearbyPlaces, 'nearby')}
          </section>

          {/* Có thể bạn sẽ thích */}
          <section className="search-section location-section">
            <div className="search-section__header">
              <h2 className="search-section__title">
                Có thể bạn sẽ thích <Icons.Location className="title-icon" />
              </h2>
            </div>

            {isLoadingSuggestions ? renderSkeleton() : renderLocationCards(suggestions, 'suggest')}
          </section>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default SearchResultsPage;