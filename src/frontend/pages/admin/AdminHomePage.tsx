import { useState, useEffect } from 'react';
import AdminHeader from '../../components/admin/AdminHeader';
import LocationCard from '../../components/common/LocationCard';
import { Icons } from '../../config/constants';
import { adminService, placeService } from '../../services';
import type { DashboardStats } from '../../types/admin';
import type { PlaceCompact } from '../../types/models';
import '../../assets/styles/pages/AdminHomePage.css';

// Mock data fallback for statistics
const mockStats: DashboardStats = {
    total_users: 3600,
    total_posts: 3600,
    total_places: 120,
    total_reports: 45,
    pending_posts: 12,
    new_users_today: 180,
    new_posts_today: 50,
};

// Mock data fallback for featured locations
const mockFeaturedLocations = [
    {
        id: '1',
        imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        title: 'Hồ Gươm - Quận Hoàn Kiếm',
        address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
        priceMin: 0,
        priceMax: 0,
        rating: 4.5,
        reviewCount: 360,
    },
    {
        id: '2',
        imageSrc: 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=600',
        title: 'Văn Miếu - Quốc Tử Giám',
        address: 'Quận Đống Đa - Thành phố Hà Nội',
        priceMin: 30000,
        priceMax: 50000,
        rating: 4.7,
        reviewCount: 280,
    },
    {
        id: '3',
        imageSrc: 'https://images.unsplash.com/photo-1509030450996-dd1a26dda07a?w=600',
        title: 'Lăng Chủ tịch Hồ Chí Minh',
        address: 'Quận Ba Đình - Thành phố Hà Nội',
        priceMin: 0,
        priceMax: 0,
        rating: 4.9,
        reviewCount: 520,
    },
];

// Format number (3600 -> "3.6K")
const formatNumber = (num: number): string => {
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
};

function AdminHomePage() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [featuredPlaces, setFeaturedPlaces] = useState<PlaceCompact[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    // Fetch dashboard stats và featured places
    useEffect(() => {
        const fetchData = async () => {
            setIsLoading(true);

            try {
                // Fetch dashboard stats
                const dashboardResponse = await adminService.getDashboardStats();
                if (dashboardResponse.success && dashboardResponse.data) {
                    setStats(dashboardResponse.data);
                } else {
                    setStats(mockStats);
                }
            } catch (error) {
                console.error('Error fetching dashboard stats:', error);
                setStats(mockStats);
            }

            try {
                // Fetch featured places
                const placesResponse = await placeService.getPlaces({ page: 1, limit: 3 });
                if (placesResponse.success && placesResponse.data.length > 0) {
                    setFeaturedPlaces(placesResponse.data);
                }
            } catch (error) {
                console.error('Error fetching featured places:', error);
            }

            setIsLoading(false);
        };

        fetchData();
    }, []);

    // Build stats display array from API data
    const overallStats = stats ? [
        {
            label: 'Số người hoạt động',
            value: formatNumber(stats.total_users),
            change: `Hôm nay: +${stats.new_users_today}`
        },
        {
            label: 'Số bài viết',
            value: formatNumber(stats.total_posts),
            change: `Hôm nay: +${stats.new_posts_today}`
        },
        {
            label: 'Chờ duyệt',
            value: stats.pending_posts.toString(),
            change: 'Bài viết cần xử lý'
        },
        {
            label: 'Báo cáo',
            value: stats.total_reports.toString(),
            change: 'Cần xem xét'
        },
    ] : [];

    // Build featured locations from API or fallback
    const displayLocations = featuredPlaces.length > 0
        ? featuredPlaces.map(place => ({
            id: String(place.id),
            imageSrc: place.main_image_url || 'https://via.placeholder.com/400x300',
            title: place.name,
            address: place.address || place.district_name || 'Hà Nội',
            priceMin: place.price_min || 0,
            priceMax: place.price_max || 0,
            rating: place.rating_average || 0,
            reviewCount: place.rating_count || 0,
        }))
        : mockFeaturedLocations;

    return (
        <div className="admin-home-page">
            <AdminHeader />

            <main className="admin-home-main">
                {/* Thống kê số liệu Section */}
                <section className="admin-section">
                    <div className="admin-section__header">
                        <div className="admin-section__accent"></div>
                        <h2 className="admin-section__title">Thống kê số liệu</h2>
                        <Icons.Graph className="admin-section__icon" />
                    </div>

                    {isLoading ? (
                        <div className="admin-stats-grid">
                            {[1, 2, 3, 4].map((i) => (
                                <div key={i} className="admin-stat-item admin-stat-item--loading">
                                    <span className="admin-stat-item__label">Đang tải...</span>
                                    <span className="admin-stat-item__value">--</span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="admin-stats-grid">
                            {overallStats.map((stat, index) => (
                                <div key={index} className="admin-stat-item">
                                    <span className="admin-stat-item__label">{stat.label}</span>
                                    <span className="admin-stat-item__value">{stat.value}</span>
                                    <span className="admin-stat-item__change">{stat.change}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </section>

                {/* Lượt truy cập Section */}
                <section className="admin-section">
                    <div className="admin-section__header">
                        <div className="admin-section__accent"></div>
                        <h2 className="admin-section__title">Lượt truy cập</h2>
                        <Icons.Graph className="admin-section__icon" />
                    </div>

                    <div className="admin-chart-container">
                        {/* Placeholder for chart - có thể dùng thư viện như Chart.js hoặc Recharts */}
                        <div className="admin-chart-placeholder">
                            <div className="admin-chart-line"></div>
                            <div className="admin-chart-labels">
                                <span>Tháng 11</span>
                                <span>17 tháng 11</span>
                                <span>18 tháng 11</span>
                                <span>19 tháng 11</span>
                                <span>20 tháng 11</span>
                                <span>21 tháng 11</span>
                                <span>22 tháng 11</span>
                            </div>
                            <div className="admin-chart-tooltip">
                                <span>17 tháng mười một</span>
                                <span className="admin-chart-tooltip__value">147,517</span>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Địa điểm nổi bật Section */}
                <section className="admin-section">
                    <div className="admin-section__header">
                        <div className="admin-section__accent"></div>
                        <h2 className="admin-section__title">Địa điểm nổi bật</h2>
                    </div>

                    <div className="admin-featured-locations">
                        {displayLocations.map((location, index) => (
                            <div key={location.id} className={`admin-location-row ${index % 2 === 1 ? 'admin-location-row--reverse' : ''}`}>
                                <div className="admin-location-card-wrapper">
                                    <LocationCard
                                        id={location.id}
                                        imageSrc={location.imageSrc}
                                        title={location.title}
                                        address={location.address}
                                        priceMin={location.priceMin}
                                        priceMax={location.priceMax}
                                        rating={location.rating}
                                        reviewCount={location.reviewCount}
                                    />
                                </div>

                                <div className="admin-location-stats">
                                    <div className="admin-location-stat">
                                        <span className="admin-location-stat__label">Đánh giá</span>
                                        <span className="admin-location-stat__value">{location.rating}/5</span>
                                        <span className="admin-location-stat__change">{location.reviewCount} reviews</span>
                                    </div>
                                    <div className="admin-location-stat">
                                        <span className="admin-location-stat__label">Giá</span>
                                        <span className="admin-location-stat__value">
                                            {location.priceMin === 0 && location.priceMax === 0
                                                ? 'Miễn phí'
                                                : `${location.priceMin.toLocaleString()}đ - ${location.priceMax.toLocaleString()}đ`
                                            }
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            </main>
        </div>
    );
}

export default AdminHomePage;
