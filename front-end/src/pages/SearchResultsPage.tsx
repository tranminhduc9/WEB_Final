import React from 'react';
import { useSearchParams } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import LocationCard from '../components/LocationCard';
import '../../css/SearchResultsPage.css';

const SearchResultsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || 'Alo em à?';

  // Dữ liệu và số lượng LocationCard giống hệt FeaturedPlaces.tsx
  const featuredLocations = [
    {
      imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '360',
    },
    {
      imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      title: 'Phố Cổ Hà Nội',
      address: 'Phường Hàng Bồ - Quận Hoàn Kiếm',
      tags: ['Ẩm thực', 'Giải trí'],
      rating: 4.2,
      reviewCount: '1.2K+',
    },
    {
      imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      title: 'Văn Miếu - Quốc Tử Giám',
      address: 'Phường Văn Miếu - Quận Đống Đa',
      tags: ['Thiên nhiên', 'Thư giãn'],
      rating: 4.8,
      reviewCount: '5.0K+',
    },
    {
      imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      title: 'Chùa Một Cột',
      address: 'Phường Đội Cấn - Quận Ba Đình',
      tags: ['Tâm linh', 'Lịch sử'],
      rating: 4.3,
      reviewCount: '890',
    },
    {
      imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      title: 'Lăng Chủ tịch Hồ Chí Minh',
      address: 'Phường Điện Biên - Quận Ba Đình',
      tags: ['Lịch sử', 'Tham quan'],
      rating: 4.7,
      reviewCount: '2.8K+',
    },
  ];

  return (
    <>
      <Header />
      <div className="search-page">
        <div className="search-page__container">
          <section className="search-section location-section">
            <div className="search-section__header">
              <h2 className="search-section__title">
                Kết quả tìm kiếm cho: "{query}"
              </h2>
            </div>

            <div className="scroll-container">
              {featuredLocations.map((item, index) => (
                <LocationCard
                  key={`result-${index}`}
                  imageSrc={item.imageSrc}
                  title={item.title}
                  address={item.address}
                  tags={item.tags}
                  rating={item.rating}
                  reviewCount={item.reviewCount}
                />
              ))}
            </div>
          </section>

          <section className="search-section location-section">
            <div className="search-section__header">
              <h2 className="search-section__title">
                Địa điểm lân cận <span className="icon-location">📍</span>
              </h2>
            </div>

            <div className="scroll-container">
              {featuredLocations.map((item, index) => (
                <LocationCard
                  key={`nearby-${index}`}
                  imageSrc={item.imageSrc}
                  title={item.title}
                  address={item.address}
                  tags={item.tags}
                  rating={item.rating}
                  reviewCount={item.reviewCount}
                />
              ))}
            </div>
          </section>

          <section className="search-section location-section">
            <div className="search-section__header">
              <h2 className="search-section__title">
                Có thể bạn sẽ thích <span className="icon-location">📍</span>
              </h2>
            </div>

            <div className="scroll-container">
              {featuredLocations.map((item, index) => (
                <LocationCard
                  key={`suggest-${index}`}
                  imageSrc={item.imageSrc}
                  title={item.title}
                  address={item.address}
                  tags={item.tags}
                  rating={item.rating}
                  reviewCount={item.reviewCount}
                />
              ))}
            </div>
          </section>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default SearchResultsPage;