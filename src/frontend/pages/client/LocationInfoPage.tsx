import { useState } from 'react';
import { useParams } from 'react-router-dom';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCardHorizontal from '../../components/common/LocationCardHorizontal';
import BlogCard from '../../components/client/BlogCard';
import { Icons } from '../../config/constants';
import '../../assets/styles/pages/LocationInfoPage.css';

// Mock data - sau này sẽ fetch từ API
const mockLocationData = {
    id: '1',
    name: 'Hồ Hoàn Kiếm',
    rating: 3.6,
    reviewCount: '3,6k',
    address: 'Phường Hoàn Kiếm, thành phố Hà Nội',
    images: [
        'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        'https://images.unsplash.com/photo-1599708153386-09f68a3f6d66?w=800',
    ],
    openingHours: 'Tất cả các ngày trong tuần / Cuối tuần mở phố đi bộ',
    description: `Hồ Hoàn Kiếm (Hán-Nôm: 湖還劍) còn được gọi là Hồ Gươm là một hồ nước ngọt tự nhiên nằm ở phường Hoàn Kiếm, trung tâm thành phố Hà Nội. Hồ có diện tích khoảng 12 ha. Trước kia, hồ còn có các tên gọi là hồ Lục Thủy (vì nước có màu xanh quanh năm), hồ Thủy Quân (dùng để duyệt thủy binh).`,
    fullDescription: `Hồ Hoàn Kiếm (Hán-Nôm: 湖還劍) còn được gọi là Hồ Gươm là một hồ nước ngọt tự nhiên nằm ở phường Hoàn Kiếm, trung tâm thành phố Hà Nội. Hồ có diện tích khoảng 12 ha. Trước kia, hồ còn có các tên gọi là hồ Lục Thủy (vì nước có màu xanh quanh năm), hồ Thủy Quân (dùng để duyệt thủy binh).

Theo truyền thuyết, vào thế kỷ 15, Lê Lợi nhận được thanh gươm thần từ Long Quân để đánh giặc Minh. Sau khi đất nước thái bình, khi vua Lê Thái Tổ dạo thuyền trên hồ, Rùa Vàng nổi lên đòi lại gươm báu. Từ đó hồ được đổi tên thành Hồ Hoàn Kiếm (hồ trả gươm).

Hồ Hoàn Kiếm là một trong những danh lam thắng cảnh nổi tiếng nhất của thủ đô Hà Nội, thu hút hàng triệu du khách trong và ngoài nước mỗi năm. Xung quanh hồ có nhiều công trình kiến trúc quan trọng như đền Ngọc Sơn, cầu Thê Húc, tháp Bút, đài Nghiên...`,
};

const nearbyLocations = [
    {
        id: '2',
        imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        title: 'Hồ Tây',
        description: 'Lê Lợi dùng thanh gươm báu đó làm gươm chiến đấu, xông pha chém địch nhiều trận...',
        rating: 1.8,
        likeCount: '1.8k',
        distance: '1.8km',
    },
    {
        id: '3',
        imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        title: 'Hồ Tây',
        description: 'Lê Lợi dùng thanh gươm báu đó làm gươm chiến đấu, xông pha chém địch nhiều trận...',
        rating: 1.8,
        likeCount: '1.8k',
        distance: '1.8km',
    },
];

const recommendations = [
    {
        id: '4',
        imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        title: 'Hồ(me) Tây',
        description: 'Lê Lợi dùng thanh gươm báu đó làm gươm chiến đấu, xông pha chém địch nhiều trận...',
        rating: 1.8,
        likeCount: '1.8k',
        distance: '1.8km',
    },
    {
        id: '5',
        imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        title: 'Hồ(me) Tây',
        description: 'Lê Lợi dùng thanh gươm báu đó làm gươm chiến đấu, xông pha chém địch nhiều trận...',
        rating: 1.8,
        likeCount: '1.8k',
        distance: '1.8km',
    },
];

// Mock posts data for BlogCard
const mockPosts = [
    {
        id: 1,
        avatarSrc: 'https://i.pravatar.cc/150?img=1',
        username: 'Entekie',
        timeAgo: '36 phút trước',
        location: 'Hồ Hoàn Kiếm, Hà Nội',
        rating: 5.0,
        imageSrc1: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        imageSrc2: 'https://images.unsplash.com/photo-1599708153386-09f68a3f6d66?w=400',
        likeCount: 36,
        commentCount: 36,
        description: 'Em có tin là anh tung địa chỉ nhà em lên mạng không? Anh là anh có hết thông tin của em rồi đấy nhé!',
    },
];

const LocationInfoPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [isFavorite, setIsFavorite] = useState(false);
    const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);

    // Sau này sẽ fetch data dựa trên id
    // Hiện tại dùng mock data, id sẽ dùng để fetch từ API
    console.log('Location ID:', id);
    const location = mockLocationData;

    return (
        <div className="location-info-page">
            <Header />

            <main className="location-info-main">
                {/* Head Section */}
                <section className="location-head">
                    <h1 className="location-head__title">{location.name}</h1>

                    <div className="location-head__meta">
                        <div className="location-head__rating-box">
                            <span className="location-head__rating">{location.rating}/5</span>
                        </div>
                        <a href="#reviews" className="location-head__reviews">
                            {location.reviewCount} reviews
                        </a>

                        <div className="location-head__address">
                            <Icons.Location className="location-head__icon" />
                            <span>{location.address}</span>
                        </div>

                        <button
                            className={`location-head__favorite ${isFavorite ? 'active' : ''}`}
                            onClick={() => setIsFavorite(!isFavorite)}
                        >
                            <Icons.Heart className="location-head__icon" />
                            <span>Lưu vào yêu thích</span>
                        </button>
                    </div>
                </section>

                {/* Image Gallery */}
                <section className="location-gallery">
                    <div className="location-gallery__container">
                        <div className="location-gallery__main">
                            <img src={location.images[0]} alt={location.name} />
                        </div>
                        <div className="location-gallery__side">
                            <img src={location.images[1] || location.images[0]} alt={location.name} />
                            <button className="location-gallery__add-btn">
                                <Icons.ImageFileAdd />
                                <span>Thêm ảnh</span>
                            </button>
                        </div>
                    </div>
                </section>

                {/* Content Layout */}
                <div className="location-content">
                    {/* Left Column */}
                    <div className="location-content__left">
                        {/* Opening Hours */}
                        <section className="location-section">
                            <div className="location-section__header">
                                <div className="location-section__accent"></div>
                                <h2 className="location-section__title">Thời gian mở cửa:</h2>
                            </div>
                            <p className="location-section__text">{location.openingHours}</p>
                        </section>

                        {/* General Info */}
                        <section className="location-section location-section--info">
                            <div className="location-section__header">
                                <div className="location-section__accent"></div>
                                <h2 className="location-section__title">Thông tin chung:</h2>
                            </div>
                            <p className={`location-section__text ${!isDescriptionExpanded ? 'location-section__text--truncated' : ''}`}>
                                {isDescriptionExpanded ? location.fullDescription : location.description}
                            </p>
                            <button
                                className="location-section__expand-btn"
                                onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                            >
                                {isDescriptionExpanded ? 'Thu gọn' : 'Xem thêm...'}
                            </button>
                        </section>

                        {/* Posts */}
                        <section className="location-section">
                            <div className="location-section__header">
                                <div className="location-section__accent"></div>
                                <h2 className="location-section__title">Posts:</h2>
                            </div>

                            <div className="location-posts">
                                {mockPosts.map((post) => (
                                    <div key={post.id} className="location-blog-card">
                                        <BlogCard
                                            id={post.id}
                                            avatarSrc={post.avatarSrc}
                                            username={post.username}
                                            timeAgo={post.timeAgo}
                                            location={post.location}
                                            rating={post.rating}
                                            imageSrc1={post.imageSrc1}
                                            imageSrc2={post.imageSrc2}
                                            likeCount={post.likeCount}
                                            commentCount={post.commentCount}
                                            description={post.description}
                                        />
                                    </div>
                                ))}
                            </div>
                        </section>
                    </div>

                    {/* Right Column - Sidebar */}
                    <div className="location-content__right">
                        {/* Nearby Locations */}
                        <section className="location-sidebar-section">
                            <div className="location-sidebar-section__header">
                                <div className="location-section__accent"></div>
                                <h2 className="location-sidebar-section__title">Địa điểm lân cận</h2>
                                <Icons.Location className="location-sidebar-section__icon" />
                            </div>
                            <div className="location-sidebar-section__list">
                                {nearbyLocations.map((loc) => (
                                    <LocationCardHorizontal
                                        key={loc.id}
                                        id={loc.id}
                                        imageSrc={loc.imageSrc}
                                        title={loc.title}
                                        description={loc.description}
                                        rating={loc.rating}
                                        likeCount={loc.likeCount}
                                        distance={loc.distance}
                                    />
                                ))}
                            </div>
                        </section>

                        {/* Recommendations */}
                        <section className="location-sidebar-section">
                            <div className="location-sidebar-section__header">
                                <div className="location-section__accent"></div>
                                <h2 className="location-sidebar-section__title">Có thể bạn sẽ thích</h2>
                                <Icons.Location className="location-sidebar-section__icon" />
                            </div>
                            <div className="location-sidebar-section__list">
                                {recommendations.map((loc) => (
                                    <LocationCardHorizontal
                                        key={loc.id}
                                        id={loc.id}
                                        imageSrc={loc.imageSrc}
                                        title={loc.title}
                                        description={loc.description}
                                        rating={loc.rating}
                                        likeCount={loc.likeCount}
                                        distance={loc.distance}
                                    />
                                ))}
                            </div>
                        </section>
                    </div>
                </div>
            </main>

            <Footer />
        </div>
    );
};

export default LocationInfoPage;
