import React from 'react';
import LocationCard from '../common/LocationCard';
import '../../assets/styles/components/NearbyLocations.css';
import '../../assets/styles/components/LocationCard.css';
export default function NearbyLocations() {
    const locations = [
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
        },
    ];
    return (
        <div className="nearby-locations-container">
            <h2 className="nearby-locations-title location-list-title">Địa điểm lân cận</h2>            <div className="scroll-container">
                {locations.map((location, index) => (
                    <LocationCard
                        key={index}
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
    );
}