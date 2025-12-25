import React from 'react';
import LocationCard from '../common/LocationCard';
import '../../assets/styles/components/SearchResults.css';
import '../../assets/styles/components/LocationCard.css';

interface SearchResultsProps {
  searchQuery?: string;
  results?: any[];
}

function SearchResults({ searchQuery = "", results = [] }: SearchResultsProps) {
  // Dữ liệu mẫu cho kết quả tìm kiếm
  const sampleResults = [
    {
      id: '1',
      imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '360'
    },
    {
      id: '2',
      imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      title: 'Phố Cổ Hà Nội',
      address: 'Phường Hàng Bồ - Quận Hoàn Kiếm',
      tags: ['Ẩm thực', 'Giải trí'],
      rating: 4.2,
      reviewCount: '1.2K+'
    },
    {
      id: '3',
      imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      title: 'Văn Miếu - Quốc Tử Giám',
      address: 'Phường Văn Miếu - Quận Đống Đa',
      tags: ['Thiên nhiên', 'Thư giãn'],
      rating: 4.8,
      reviewCount: '5.0K+'
    },
    {
      id: '4',
      imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      title: 'Chùa Một Cột',
      address: 'Phường Đội Cấn - Quận Ba Đình',
      tags: ['Tâm linh', 'Lịch sử'],
      rating: 4.3,
      reviewCount: '890'
    },
    {
      id: '5',
      imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      title: 'Lăng Chủ tịch Hồ Chí Minh',
      address: 'Phường Điện Biên - Quận Ba Đình',
      tags: ['Lịch sử', 'Tham quan'],
      rating: 4.7,
      reviewCount: '2.8K+'
    },

  ];

  const displayResults = results.length > 0 ? results : sampleResults;
  const resultCount = displayResults.length;

  return (
    <div className="search-results-container">
      <div className="search-results-header">
        <h2 className="search-results-title location-list-title">
          {searchQuery ? `Kết quả tìm kiếm cho "${searchQuery}"` : 'Kết quả tìm kiếm'}
        </h2>
        <p className="search-results-count">
          Tìm thấy {resultCount} kết quả
        </p>
      </div>

      <div className="scroll-container">
        {displayResults.map((location, index) => (
          <LocationCard
            key={index}
            id={location.id}
            imageSrc={location.imageSrc}
            title={location.title}
            address={location.address}
            tags={location.tags}
            rating={location.rating}
            reviewCount={location.reviewCount}
          />
        ))}
      </div>

      {displayResults.length === 0 && (
        <div className="no-results">
          <h3>Không tìm thấy kết quả</h3>
          <p>Thử tìm kiếm với từ khóa khác hoặc kiểm tra lại chính tả.</p>
        </div>
      )}




    </div>
  );
}

export default SearchResults;
