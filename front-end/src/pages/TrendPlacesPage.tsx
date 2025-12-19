import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import LocationCard from '../components/LocationCard';
import '../../css/TrendPlacesPage.css';
import '../../css/LocationCard.css';

const TrendPlacesPage: React.FC = () => {
  // Dữ liệu mẫu cho địa điểm trending
  const trendingLocations = [
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    }
  ];

  // Dữ liệu mẫu cho những nơi phải đến
  const mustVisitLocations = [
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    }
  ];

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
          <div className="scroll-container">
            {trendingLocations.map((location, index) => (
              <LocationCard
                key={`trending-${index}`}
                imageSrc={location.imageSrc}
                title={location.title}
                address={location.address}
                tags={location.tags}
                rating={location.rating}
                reviewCount={location.reviewCount}
              />
            ))}
          </div>
        </section>

        {/* Section 2: Những nơi bạn phải đến */}
        <section className="trend-section location-section">
          <h2 className="trend-section__title">
            Những nơi bạn phải đến (Mọi lúc mọi nơi)
          </h2>
          <div className="scroll-container">
            {mustVisitLocations.map((location, index) => (
              <LocationCard
                key={`must-visit-${index}`}
                imageSrc={location.imageSrc}
                title={location.title}
                address={location.address}
                tags={location.tags}
                rating={location.rating}
                reviewCount={location.reviewCount}
              />
            ))}
          </div>
        </section>
      </div>
      <Footer />
    </>
  );
};

export default TrendPlacesPage;

