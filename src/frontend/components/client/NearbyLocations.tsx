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
                        tags={location.tags}
                        rating={location.rating}
                        reviewCount={location.reviewCount}
                    />
                ))}
            </div>
        </div>
    );
}