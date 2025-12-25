import '../../assets/styles/components/FeaturedPlaces.css';
import LocationCard from '../common/LocationCard';

function FeaturedPlaces() {
    // Dữ liệu mẫu cho các địa điểm
    const featuredLocations = [
        {
            id: '1',
            imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
            title: 'Hồ Gươm - Quận Hoàn Kiếm',
            address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
            priceMin: 0,
            priceMax: 0,
            rating: 4.5,
            reviewCount: '360'
        },
        {
            id: '2',
            imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
            title: 'Phố Cổ Hà Nội',
            address: 'Phường Hàng Bồ - Quận Hoàn Kiếm',
            priceMin: 50000,
            priceMax: 200000,
            rating: 4.2,
            reviewCount: '1.2K+'
        },
        {
            id: '3',
            imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
            title: 'Văn Miếu - Quốc Tử Giám',
            address: 'Phường Văn Miếu - Quận Đống Đa',
            priceMin: 30000,
            priceMax: 50000,
            rating: 4.8,
            reviewCount: '5.0K+'
        },
        {
            id: '4',
            imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
            title: 'Chùa Một Cột',
            address: 'Phường Đội Cấn - Quận Ba Đình',
            priceMin: 0,
            priceMax: 0,
            rating: 4.3,
            reviewCount: '890'
        },
        {
            id: '5',
            imageSrc: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
            title: 'Lăng Chủ tịch Hồ Chí Minh',
            address: 'Phường Điện Biên - Quận Ba Đình',
            priceMin: 0,
            priceMax: 0,
            rating: 4.7,
            reviewCount: '2.8K+'
        }
    ];

    return (
        <div id="featured-places" className="location-section">
            <h3 className="featured-places-title">Các đặc điểm nổi bật</h3>
            <p className="featured-places-description">Cùng khám phá các đặc điểm, di tích để hiểu thêm về Hà Nội nghìn năm văn hiến nhé!</p>
            <div className="scroll-container">
                {featuredLocations.map((location) => (
                    <LocationCard
                        key={location.id}
                        id={location.id}
                        imageSrc={location.imageSrc}
                        title={location.title}
                        address={location.address}
                        priceMin={location.priceMin}
                        priceMax={location.priceMax}
                        rating={location.rating}
                        reviewCount={location.reviewCount}
                    />
                ))}
            </div>
        </div>
    )
}
export default FeaturedPlaces;