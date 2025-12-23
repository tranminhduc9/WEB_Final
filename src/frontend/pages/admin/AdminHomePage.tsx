import AdminHeader from '../../components/admin/AdminHeader';
import LocationCard from '../../components/common/LocationCard';
import { Icons } from '../../config/constants';
import '../../assets/styles/pages/AdminHomePage.css';

// Mock data for statistics
const overallStats = [
    { label: 'Số người hoạt động', value: '3.6K', change: 'Tăng 1.8k (50%)' },
    { label: 'Số bài viết', value: '3.6K', change: 'Tăng 1.8k (50%)' },
    { label: 'Số Lượt thích', value: '3.6K', change: 'Tăng 1.8k (50%)' },
    { label: 'Số Bình luận', value: '3.6K', change: 'Tăng 1.8k (50%)' },
];

// Mock data for featured locations
const featuredLocations = [
    {
        id: '1',
        imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        title: 'Hồ Gươm - Quận Hoàn Kiếm',
        address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
        tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
        rating: 4.5,
        reviewCount: '360',
        stats: {
            searches: '3.6K',
            searchesChange: 'Tăng 1.8k (50%)',
            posts: '3.6K',
            postsChange: 'Tăng 1.8k (50%)',
            avgRating: '3.6/5',
        },
    },
    {
        id: '2',
        imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        title: 'Hồ Gươm - Quận Hoàn Kiếm',
        address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
        tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
        rating: 4.5,
        reviewCount: '360',
        stats: {
            searches: '3.6K',
            searchesChange: 'Tăng 1.8k (50%)',
            posts: '3.6K',
            postsChange: 'Tăng 1.8k (50%)',
            avgRating: '3.6/5',
        },
    },
    {
        id: '3',
        imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        title: 'Hồ Gươm - Quận Hoàn Kiếm',
        address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
        tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
        rating: 4.5,
        reviewCount: '360',
        stats: {
            searches: '3.6K',
            searchesChange: 'Tăng 1.8k (50%)',
            posts: '3.6K',
            postsChange: 'Tăng 1.8k (50%)',
            avgRating: '3.6/5',
        },
    },
];

function AdminHomePage() {
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

                    <div className="admin-stats-grid">
                        {overallStats.map((stat, index) => (
                            <div key={index} className="admin-stat-item">
                                <span className="admin-stat-item__label">{stat.label}</span>
                                <span className="admin-stat-item__value">{stat.value}</span>
                                <span className="admin-stat-item__change">{stat.change}</span>
                            </div>
                        ))}
                    </div>
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
                        {featuredLocations.map((location, index) => (
                            <div key={location.id} className={`admin-location-row ${index % 2 === 1 ? 'admin-location-row--reverse' : ''}`}>
                                <div className="admin-location-card-wrapper">
                                    <LocationCard
                                        id={location.id}
                                        imageSrc={location.imageSrc}
                                        title={location.title}
                                        address={location.address}
                                        tags={location.tags}
                                        rating={location.rating}
                                        reviewCount={location.reviewCount}
                                    />
                                </div>

                                <div className="admin-location-stats">
                                    <div className="admin-location-stat">
                                        <span className="admin-location-stat__label">Số người tìm kiếm</span>
                                        <span className="admin-location-stat__value">{location.stats.searches}</span>
                                        <span className="admin-location-stat__change">{location.stats.searchesChange}</span>
                                    </div>
                                    <div className="admin-location-stat">
                                        <span className="admin-location-stat__label">Số bài viết</span>
                                        <span className="admin-location-stat__value">{location.stats.posts}</span>
                                        <span className="admin-location-stat__change">{location.stats.postsChange}</span>
                                    </div>
                                    <div className="admin-location-stat">
                                        <span className="admin-location-stat__label">Đánh giá trung bình</span>
                                        <span className="admin-location-stat__value">{location.stats.avgRating}</span>
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
