import React, { useState, useEffect } from 'react';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCard from '../../components/common/LocationCard';
import { placeService } from '../../services';
import type { PlaceCompact } from '../../types/models';
import '../../assets/styles/pages/TrendPlacesPage.css';
import '../../assets/styles/components/LocationCard.css';

// Mock data fallback
const mockTrendingLocations = [
  {
    id: '1',
    imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
    title: 'Hồ Gươm - Quận Hoàn Kiếm',
    address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
    priceMin: 0,
    priceMax: 0,
    rating: 4.5,
    reviewCount: '3.6K+'
  },
  {
    id: '2',
    imageSrc: 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=600',
    title: 'Văn Miếu - Quốc Tử Giám',
    address: 'Quận Đống Đa - Thành phố Hà Nội',
    priceMin: 30000,
    priceMax: 50000,
    rating: 4.7,
    reviewCount: '2.8K+'
  },
  {
    id: '3',
    imageSrc: 'https://images.unsplash.com/photo-1509030450996-dd1a26dda07a?w=600',
    title: 'Lăng Chủ tịch Hồ Chí Minh',
    address: 'Quận Ba Đình - Thành phố Hà Nội',
    priceMin: 0,
    priceMax: 0,
    rating: 4.9,
    reviewCount: '5.2K+'
  }
];

const mockMustVisitLocations = [
  {
    id: '4',
    imageSrc: 'https://images.unsplash.com/photo-1555921015-5532091f6026?w=600',
    title: 'Phố cổ Hà Nội',
    address: 'Quận Hoàn Kiếm - Thành phố Hà Nội',
    priceMin: 0,
    priceMax: 0,
    rating: 4.6,
    reviewCount: '4.1K+'
  },
  {
    id: '5',
    imageSrc: 'https://images.unsplash.com/photo-1528127269322-539801943592?w=600',
    title: 'Chùa Một Cột',
    address: 'Quận Ba Đình - Thành phố Hà Nội',
    priceMin: 0,
    priceMax: 0,
    rating: 4.5,
    reviewCount: '2.3K+'
  }
];

const TrendPlacesPage: React.FC = () => {
  // State for API data
  const [trendingPlaces, setTrendingPlaces] = useState<PlaceCompact[]>([]);
  const [mustVisitPlaces, setMustVisitPlaces] = useState<PlaceCompact[]>([]);

  // Loading states
  const [isTrendingLoading, setIsTrendingLoading] = useState(true);
  const [isMustVisitLoading, setIsMustVisitLoading] = useState(true);

  // Error states for fallback
  const [trendingError, setTrendingError] = useState(false);
  const [mustVisitError, setMustVisitError] = useState(false);

  // Fetch trending places
  useEffect(() => {
    const fetchTrending = async () => {
      setIsTrendingLoading(true);
      try {
        const response = await placeService.getPlaces({ page: 1, limit: 5 });
        if (response.data && response.data.length > 0) {
          setTrendingPlaces(response.data);
        } else {
          setTrendingError(true);
        }
      } catch (error) {
        console.error('Error fetching trending places:', error);
        setTrendingError(true);
      } finally {
        setIsTrendingLoading(false);
      }
    };
    fetchTrending();
  }, []);

  // Fetch must-visit places (using page 2 for different results)
  useEffect(() => {
    const fetchMustVisit = async () => {
      setIsMustVisitLoading(true);
      try {
        const response = await placeService.getPlaces({ page: 2, limit: 5 });
        if (response.data && response.data.length > 0) {
          setMustVisitPlaces(response.data);
        } else {
          setMustVisitError(true);
        }
      } catch (error) {
        console.error('Error fetching must-visit places:', error);
        setMustVisitError(true);
      } finally {
        setIsMustVisitLoading(false);
      }
    };
    fetchMustVisit();
  }, []);

  // Helper to map PlaceCompact to LocationCard props
  const mapPlaceToCard = (place: PlaceCompact) => ({
    id: String(place.id),
    imageSrc: place.main_image_url || 'https://via.placeholder.com/400x300?text=No+Image',
    title: place.name,
    address: place.address || place.district_name || 'Hà Nội',
    priceMin: place.price_min || 0,
    priceMax: place.price_max || 0,
    rating: place.rating_average || 0,
    reviewCount: place.rating_count ? `${place.rating_count}` : '0'
  });

  // Render loading spinner
  const renderLoading = () => (
    <div className="trend-loading">
      <div className="loading-spinner"></div>
      <p>Đang tải...</p>
    </div>
  );

  return (
    <>
      <Header />
      <div className="trend-places-page">
        {/* Hero Section với 2 ảnh */}
        <section className="trend-hero">
          <div className="trend-hero__container">
            <div className="trend-hero__image trend-hero__image--left">
              <img
                src="https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg"
                alt="Hồ Hoàn Kiếm"
              />
            </div>
            <div className="trend-hero__image trend-hero__image--right">
              <img
                src="https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=800"
                alt="Phố cổ Hà Nội"
              />
            </div>
          </div>
        </section>

        {/* Section 1: Địa điểm trending */}
        <section className="trend-section location-section">
          <h2 className="trend-section__title">
            Địa điểm trending (Trend theo mùa)
          </h2>
          {isTrendingLoading ? (
            renderLoading()
          ) : (
            <div className="scroll-container">
              {(trendingError ? mockTrendingLocations : trendingPlaces.map(mapPlaceToCard)).map((location, index) => (
                <LocationCard
                  key={`trending-${location.id || index}`}
                  id={location.id}
                  imageSrc={location.imageSrc}
                  title={location.title}
                  address={location.address}
                  priceMin={location.priceMin}
                  priceMax={location.priceMax}
                  rating={location.rating}
                  reviewCount={String(location.reviewCount)}
                />
              ))}
            </div>
          )}
        </section>

        {/* Section 2: Những nơi bạn phải đến */}
        <section className="trend-section location-section">
          <h2 className="trend-section__title">
            Những nơi bạn phải đến (Mọi lúc mọi nơi)
          </h2>
          {isMustVisitLoading ? (
            renderLoading()
          ) : (
            <div className="scroll-container">
              {(mustVisitError ? mockMustVisitLocations : mustVisitPlaces.map(mapPlaceToCard)).map((location, index) => (
                <LocationCard
                  key={`must-visit-${location.id || index}`}
                  id={location.id}
                  imageSrc={location.imageSrc}
                  title={location.title}
                  address={location.address}
                  priceMin={location.priceMin}
                  priceMax={location.priceMax}
                  rating={location.rating}
                  reviewCount={String(location.reviewCount)}
                />
              ))}
            </div>
          )}
        </section>
      </div>
      <Footer />
    </>
  );
};

export default TrendPlacesPage;
