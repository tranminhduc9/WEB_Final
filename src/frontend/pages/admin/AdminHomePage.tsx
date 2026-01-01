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
    // Step 2: Thêm state visitAnalytics trong AdminHomePage
    const [visitAnalytics, setVisitAnalytics] = useState<{
        visits_trend: Array<{ date: string; count: number }>;
        summary: { total_visits: number; unique_visitors: number };
    } | null>(null);

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

            // Step 3: Gọi API fetch visit analytics trong useEffect
            try {
                const analyticsResponse = await adminService.getVisitAnalytics(7);
                if (analyticsResponse.success && analyticsResponse.data?.visits) {
                    setVisitAnalytics({
                        visits_trend: analyticsResponse.data.visits.visits_trend || [],
                        summary: analyticsResponse.data.visits.summary || { total_visits: 0, unique_visitors: 0 }
                    });
                }
            } catch (error) {
                console.error('Error fetching visit analytics:', error);
            }

            setIsLoading(false);
        };

        fetchData();
    }, []);

    // Build stats display array from API data
    const overallStats = stats ? [
        {
            label: 'Số người hoạt động',
            value: formatNumber(stats.total_users ?? 0),
            change: `Hôm nay: +${stats.new_users_today ?? 0}`
        },
        {
            label: 'Số bài viết',
            value: formatNumber(stats.total_posts ?? 0),
            change: `Hôm nay: +${stats.new_posts_today ?? 0}`
        },
        {
            label: 'Chờ duyệt',
            value: (stats.pending_posts ?? 0).toString(),
            change: 'Bài viết cần xử lý'
        },
        {
            label: 'Báo cáo',
            value: (stats.total_reports ?? 0).toString(),
            change: 'Cần xem xét'
        },
    ] : [];

    // Build featured locations from API or fallback
    const displayLocations = featuredPlaces.length > 0
        ? featuredPlaces.map(place => ({
            id: String(place.id),
            imageSrc: place.main_image_url || 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=600',
            title: place.name || 'Địa điểm chưa có tên',
            address: place.address || place.district_name || 'Hà Nội',
            priceMin: place.price_min ?? 0,
            priceMax: place.price_max ?? 0,
            rating: place.rating_average ?? 0,
            reviewCount: place.rating_count ?? 0,
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
                        <h2 className="admin-section__title">Lượt truy cập (7 ngày gần đây)</h2>
                        <Icons.Graph className="admin-section__icon" />
                    </div>

                    <div className="admin-chart-container">
                        {/* Step 4: Cập nhật phần chart để hiển thị dữ liệu thực */}
                        {visitAnalytics && visitAnalytics.visits_trend.length > 0 ? (
                            <div className="admin-chart-placeholder">
                                {/* Summary stats */}
                                <div className="admin-visits-summary">
                                    <div className="admin-visits-stat">
                                        <span className="admin-visits-stat__label">Tổng lượt truy cập</span>
                                        <span className="admin-visits-stat__value">{visitAnalytics.summary.total_visits.toLocaleString()}</span>
                                    </div>
                                    <div className="admin-visits-stat">
                                        <span className="admin-visits-stat__label">Khách truy cập</span>
                                        <span className="admin-visits-stat__value">{visitAnalytics.summary.unique_visitors.toLocaleString()}</span>
                                    </div>
                                </div>
                                {/* Line chart */}
                                <div className="admin-line-chart">
                                    <svg viewBox="0 0 700 200" className="admin-line-chart__svg">
                                        {/* Grid lines */}
                                        <line x1="0" y1="160" x2="700" y2="160" stroke="#E0E0E0" strokeWidth="1" />
                                        {/* Horizontal grid lines */}
                                        <line x1="0" y1="50" x2="700" y2="50" stroke="#F0F0F0" strokeWidth="1" strokeDasharray="5,5" />
                                        <line x1="0" y1="90" x2="700" y2="90" stroke="#F0F0F0" strokeWidth="1" strokeDasharray="5,5" />
                                        <line x1="0" y1="130" x2="700" y2="130" stroke="#F0F0F0" strokeWidth="1" strokeDasharray="5,5" />

                                        {/* Line path - with date-proportional spacing */}
                                        <polyline
                                            fill="none"
                                            stroke="#F88622"
                                            strokeWidth="3"
                                            strokeLinejoin="round"
                                            strokeLinecap="round"
                                            points={(() => {
                                                const dates = visitAnalytics.visits_trend.map((item: { date: string }) => new Date(item.date).getTime());
                                                const minDate = Math.min(...dates);
                                                const maxDate = Math.max(...dates);
                                                const dateRange = maxDate - minDate || 1;
                                                const maxCount = Math.max(...visitAnalytics.visits_trend.map((v: { count: number }) => v.count));

                                                return visitAnalytics.visits_trend.map((item: { date: string; count: number }) => {
                                                    const dateTime = new Date(item.date).getTime();
                                                    const x = ((dateTime - minDate) / dateRange) * 700;
                                                    const y = 160 - ((item.count / (maxCount || 1)) * 130);
                                                    return `${x},${y}`;
                                                }).join(' ');
                                            })()}
                                        />

                                        {/* Area fill - with date-proportional spacing */}
                                        <polygon
                                            fill="url(#areaGradient)"
                                            opacity="0.3"
                                            points={(() => {
                                                const dates = visitAnalytics.visits_trend.map((item: { date: string }) => new Date(item.date).getTime());
                                                const minDate = Math.min(...dates);
                                                const maxDate = Math.max(...dates);
                                                const dateRange = maxDate - minDate || 1;
                                                const maxCount = Math.max(...visitAnalytics.visits_trend.map((v: { count: number }) => v.count));

                                                const points = visitAnalytics.visits_trend.map((item: { date: string; count: number }) => {
                                                    const dateTime = new Date(item.date).getTime();
                                                    const x = ((dateTime - minDate) / dateRange) * 700;
                                                    const y = 160 - ((item.count / (maxCount || 1)) * 130);
                                                    return `${x},${y}`;
                                                }).join(' ');

                                                return `0,160 ${points} 700,160`;
                                            })()}
                                        />

                                        {/* Gradient definition */}
                                        <defs>
                                            <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                                <stop offset="0%" stopColor="#F88622" />
                                                <stop offset="100%" stopColor="#FFFFFF" />
                                            </linearGradient>
                                        </defs>

                                        {/* Data points and labels - with date-proportional spacing */}
                                        {(() => {
                                            const dates = visitAnalytics.visits_trend.map((item: { date: string }) => new Date(item.date).getTime());
                                            const minDate = Math.min(...dates);
                                            const maxDate = Math.max(...dates);
                                            const dateRange = maxDate - minDate || 1;
                                            const maxCount = Math.max(...visitAnalytics.visits_trend.map((v: { count: number }) => v.count));
                                            const totalItems = visitAnalytics.visits_trend.length;

                                            return visitAnalytics.visits_trend.map((item: { date: string; count: number }, index: number) => {
                                                const dateTime = new Date(item.date).getTime();
                                                const x = ((dateTime - minDate) / dateRange) * 700;
                                                const y = 160 - ((item.count / (maxCount || 1)) * 130);

                                                // Adjust textAnchor for first and last labels
                                                let textAnchor = "middle";
                                                if (index === 0) textAnchor = "start";
                                                if (index === totalItems - 1) textAnchor = "end";

                                                return (
                                                    <g key={index} className="admin-chart-point">
                                                        {/* Invisible larger circle for better hover */}
                                                        <circle
                                                            cx={x}
                                                            cy={y}
                                                            r="15"
                                                            fill="transparent"
                                                            style={{ cursor: 'pointer' }}
                                                        />
                                                        {/* Visible circle */}
                                                        <circle
                                                            cx={x}
                                                            cy={y}
                                                            r="6"
                                                            fill="#FFFFFF"
                                                            stroke="#F88622"
                                                            strokeWidth="2"
                                                            style={{ cursor: 'pointer', pointerEvents: 'none' }}
                                                        />
                                                        {/* Tooltip text - appears on hover via CSS */}
                                                        <text
                                                            x={x}
                                                            y={y - 20}
                                                            textAnchor="middle"
                                                            fill="#333"
                                                            fontSize="12"
                                                            fontWeight="600"
                                                            fontFamily="Inter, sans-serif"
                                                            className="admin-chart-tooltip-text"
                                                        >
                                                            {item.count.toLocaleString()} lượt
                                                        </text>
                                                        {/* Date label */}
                                                        <text
                                                            x={x}
                                                            y="185"
                                                            textAnchor={textAnchor as "start" | "middle" | "end"}
                                                            fill="#666"
                                                            fontSize="14"
                                                            fontFamily="Inter, sans-serif"
                                                        >
                                                            {new Date(item.date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })}
                                                        </text>
                                                    </g>
                                                );
                                            });
                                        })()}
                                    </svg>
                                </div>
                            </div>
                        ) : (
                            <div className="admin-chart-placeholder">
                                <div className="admin-chart-empty">
                                    {isLoading ? 'Đang tải dữ liệu...' : 'Chưa có dữ liệu lượt truy cập'}
                                </div>
                            </div>
                        )}
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
