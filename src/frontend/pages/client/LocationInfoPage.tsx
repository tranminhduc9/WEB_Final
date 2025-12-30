import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCardHorizontal from '../../components/common/LocationCardHorizontal';
import BlogCard from '../../components/client/BlogCard';
import { Icons } from '../../config/constants';
import { placeService } from '../../services';
import { useAuthContext } from '../../contexts';
import { useScrollToTop } from '../../hooks';
import type { PlaceDetail, PlaceCompact, PostDetail } from '../../types/models';
import '../../assets/styles/pages/LocationInfoPage.css';

// ============================
// MOCK DATA (Fallback khi API fail)
// ============================
const MOCK_LOCATION: PlaceDetail = {
    id: 1,
    name: 'Hồ Hoàn Kiếm',
    district_id: 1,
    place_type_id: 1,
    rating_average: 3.6,
    price_min: 0,
    price_max: 100000,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
    address: 'Phường Hoàn Kiếm, thành phố Hà Nội',
    description: 'Hồ Hoàn Kiếm (Hán-Nôm: 湖還劍) còn được gọi là Hồ Gươm là một hồ nước ngọt tự nhiên nằm ở phường Hoàn Kiếm, trung tâm thành phố Hà Nội.',
    opening_hours: 'Tất cả các ngày trong tuần / Cuối tuần mở phố đi bộ',
    images: [
        'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
        'https://images.unsplash.com/photo-1599708153386-09f68a3f6d66?w=800',
    ],
    reviews_count: 3600,
    latitude: 21.0285,
    longitude: 105.8542,
};

const MOCK_NEARBY: PlaceCompact[] = [
    {
        id: 2,
        name: 'Hồ Tây',
        district_id: 1,
        place_type_id: 1,
        rating_average: 4.2,
        price_min: 0,
        price_max: 0,
        main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
    },
    {
        id: 3,
        name: 'Văn Miếu Quốc Tử Giám',
        district_id: 2,
        place_type_id: 1,
        rating_average: 4.5,
        price_min: 30000,
        price_max: 50000,
        main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
    },
];

const MOCK_POSTS: PostDetail[] = [
    {
        _id: '1',
        author: { id: 1, full_name: 'Entekie', avatar_url: 'https://i.pravatar.cc/150?img=1', role_id: 1 },
        title: 'Trải nghiệm Hồ Hoàn Kiếm',
        content: 'Thấy Hà Nội okee phết!!',
        rating: 5,
        images: [
            'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
            'https://images.unsplash.com/photo-1599708153386-09f68a3f6d66?w=400'
        ],
        likes_count: 36,
        comments_count: 36,
        is_liked: false,
        created_at: new Date(Date.now() - 36 * 60 * 1000).toISOString(),
    },
];

// Helper: Format time ago
const formatTimeAgo = (dateString?: string): string => {
    if (!dateString) return 'Vừa xong';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 60) return `${diffMins} phút trước`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} giờ trước`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} ngày trước`;
};

// Helper: Format reviews count
const formatReviewCount = (count?: number): string => {
    if (!count) return '0';
    if (count >= 1000) return `${(count / 1000).toFixed(1)}k`.replace('.0k', 'k');
    return String(count);
};

const LocationInfoPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { isAuthenticated } = useAuthContext();

    // Scroll to top on navigation
    useScrollToTop();

    // Main place data
    const [place, setPlace] = useState<PlaceDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Favorite state
    const [isFavorite, setIsFavorite] = useState(false);
    const [isFavoriteLoading, setIsFavoriteLoading] = useState(false);

    // Nearby & suggestions
    const [nearbyPlaces, setNearbyPlaces] = useState<PlaceCompact[]>([]);
    const [suggestions, setSuggestions] = useState<PlaceCompact[]>([]);
    const [isLoadingNearby, setIsLoadingNearby] = useState(true);
    const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(true);

    // UI state
    const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);

    // ============================
    // FETCH PLACE DETAILS
    // GET /places/{id}
    // ============================
    const fetchPlaceDetails = useCallback(async () => {
        if (!id) return;

        setIsLoading(true);
        setError(null);

        try {
            const response = await placeService.getPlaceById(Number(id));
            if (response.success && response.data) {
                setPlace(response.data);
                // Fetch nearby places using place's coordinates
                if (response.data.latitude && response.data.longitude) {
                    fetchNearbyPlaces(response.data.latitude, response.data.longitude);
                } else {
                    // Fallback to default Hanoi coordinates
                    fetchNearbyPlaces(21.0285, 105.8542);
                }
            } else {
                throw new Error('Place not found');
            }
        } catch (err) {
            console.error('Error fetching place:', err);
            setError('Không thể tải thông tin địa điểm');
            // Fallback to mock data
            setPlace(MOCK_LOCATION);
            setNearbyPlaces(MOCK_NEARBY);
        } finally {
            setIsLoading(false);
        }
    }, [id]);

    // ============================
    // FETCH NEARBY PLACES
    // GET /places/nearby
    // ============================
    const fetchNearbyPlaces = async (lat: number, long: number) => {
        setIsLoadingNearby(true);
        try {
            const response = await placeService.getNearbyPlaces({ lat, long });
            if (response.success && response.data.length > 0) {
                // Filter out current place from nearby
                const filtered = response.data.filter(p => p.id !== Number(id));
                setNearbyPlaces(filtered.slice(0, 5));
            } else {
                setNearbyPlaces(MOCK_NEARBY);
            }
        } catch (err) {
            console.error('Error fetching nearby:', err);
            setNearbyPlaces(MOCK_NEARBY);
        } finally {
            setIsLoadingNearby(false);
        }
    };

    // ============================
    // FETCH SUGGESTIONS
    // GET /places/nearby (to get distance info)
    // ============================
    const fetchSuggestions = useCallback(async (lat?: number, long?: number) => {
        setIsLoadingSuggestions(true);
        try {
            const coords = {
                lat: lat || 21.0285,  // Default to Hanoi center
                long: long || 105.8542
            };
            const response = await placeService.getNearbyPlaces(coords);
            if (response.success && response.data.length > 0) {
                // Filter out current place and nearby places to avoid duplicates
                const nearbyIds = new Set(nearbyPlaces.map(p => p.id));
                const filtered = response.data.filter(p =>
                    p.id !== Number(id) && !nearbyIds.has(p.id)
                );
                setSuggestions(filtered.slice(0, 5));
            } else {
                setSuggestions(MOCK_NEARBY);
            }
        } catch (err) {
            console.error('Error fetching suggestions:', err);
            setSuggestions(MOCK_NEARBY);
        } finally {
            setIsLoadingSuggestions(false);
        }
    }, [id, nearbyPlaces]);

    // ============================
    // TOGGLE FAVORITE
    // POST /places/{id}/favorite
    // ============================
    const handleToggleFavorite = async () => {
        if (!id) return;

        if (!isAuthenticated) {
            alert('Vui lòng đăng nhập để lưu yêu thích');
            return;
        }

        setIsFavoriteLoading(true);
        try {
            const response = await placeService.toggleFavoritePlace(Number(id));
            if (response.success) {
                setIsFavorite(response.is_favorited);
            }
        } catch (err) {
            console.error('Error toggling favorite:', err);
            // Toggle locally as fallback
            setIsFavorite(prev => !prev);
        } finally {
            setIsFavoriteLoading(false);
        }
    };

    // ============================
    // CHECK FAVORITE STATUS
    // ============================
    const checkFavoriteStatus = useCallback(async () => {
        if (!id || !isAuthenticated) return;

        try {
            // Fetch user's favorite places and check if this place is in the list
            const response = await placeService.getFavoritePlaces();
            if (response.success && response.data) {
                const favoriteIds = response.data.map((p: PlaceCompact) => p.id);
                setIsFavorite(favoriteIds.includes(Number(id)));
            }
        } catch (err) {
            console.error('Error checking favorite status:', err);
        }
    }, [id, isAuthenticated]);

    // ============================
    // EFFECTS
    // ============================
    useEffect(() => {
        fetchPlaceDetails();
    }, [fetchPlaceDetails]);

    // Check favorite status when user is authenticated
    useEffect(() => {
        checkFavoriteStatus();
    }, [checkFavoriteStatus]);

    // Fetch suggestions after place is loaded (to use its coordinates)
    useEffect(() => {
        if (place?.latitude && place?.longitude) {
            fetchSuggestions(place.latitude, place.longitude);
        } else if (place) {
            fetchSuggestions();
        }
    }, [place, fetchSuggestions]);

    // ============================
    // RENDER HELPERS
    // ============================
    const renderSkeleton = () => (
        <div className="location-skeleton">
            <div className="skeleton-header" />
            <div className="skeleton-gallery" />
            <div className="skeleton-content" />
        </div>
    );

    const renderPosts = () => {
        const posts = place?.related_posts || MOCK_POSTS;

        return (
            <div className="location-posts">
                {posts.map((post) => (
                    <div key={post._id} className="location-blog-card">
                        <BlogCard
                            id={Number(post._id) || 0}
                            avatarSrc={post.author?.avatar_url || 'https://i.pravatar.cc/150'}
                            username={post.author?.full_name || 'Ẩn danh'}
                            timeAgo={formatTimeAgo(post.created_at)}
                            location={place?.name || ''}
                            rating={post.rating || 0}
                            imageSrc1={post.images?.[0] || ''}
                            imageSrc2={post.images?.[1] || ''}
                            likeCount={post.likes_count}
                            commentCount={post.comments_count}
                            description={post.content}
                        />
                    </div>
                ))}
            </div>
        );
    };

    const renderNearbyCards = (places: PlaceCompact[], loading: boolean) => {
        if (loading) {
            return (
                <div className="location-sidebar-section__list">
                    {[1, 2].map(i => (
                        <div key={i} className="skeleton-card-horizontal" />
                    ))}
                </div>
            );
        }

        return (
            <div className="location-sidebar-section__list">
                {places.map((loc) => (
                    <LocationCardHorizontal
                        key={loc.id}
                        id={String(loc.id)}
                        imageSrc={loc.main_image_url || 'https://via.placeholder.com/300'}
                        title={loc.name}
                        description={loc.address || loc.district_name || 'Hà Nội'}
                        rating={loc.rating_average}
                        likeCount={String(loc.favorites_count || 0)}
                        distance={loc.distance || '~'}
                    />
                ))}
            </div>
        );
    };

    // ============================
    // LOADING STATE
    // ============================
    if (isLoading) {
        return (
            <div className="location-info-page">
                <Header />
                <main className="location-info-main">
                    {renderSkeleton()}
                </main>
                <Footer />
            </div>
        );
    }

    // ============================
    // ERROR STATE
    // ============================
    if (error && !place) {
        return (
            <div className="location-info-page">
                <Header />
                <main className="location-info-main">
                    <div className="location-error">
                        <h2>Lỗi</h2>
                        <p>{error}</p>
                    </div>
                </main>
                <Footer />
            </div>
        );
    }

    // Use place data or fallback
    const location = place || MOCK_LOCATION;

    return (
        <div className="location-info-page">
            <Header />

            <main className="location-info-main">
                {/* Head Section */}
                <section className="location-head">
                    <h1 className="location-head__title">{location.name}</h1>

                    <div className="location-head__meta">
                        <div className="location-head__rating-box">
                            <span className="location-head__rating">
                                {location.rating_average?.toFixed(1) || '0'}/5
                            </span>
                        </div>
                        <a href="#reviews" className="location-head__reviews">
                            {formatReviewCount(location.reviews_count)} reviews
                        </a>

                        <div className="location-head__address">
                            <Icons.Location className="location-head__icon" />
                            <span>{location.address || 'Hà Nội'}</span>
                        </div>

                        <button
                            className={`location-head__favorite ${isFavorite ? 'active' : ''}`}
                            onClick={handleToggleFavorite}
                            disabled={isFavoriteLoading}
                        >
                            <Icons.Heart className="location-head__icon" />
                            <span>
                                {isFavoriteLoading ? 'Đang xử lý...' : (isFavorite ? 'Đã lưu' : 'Lưu vào yêu thích')}
                            </span>
                        </button>
                    </div>
                </section>

                {/* Image Gallery */}
                <section className="location-gallery">
                    <div className="location-gallery__container">
                        <div className="location-gallery__main">
                            <img
                                src={location.images?.[0] || location.main_image_url}
                                alt={location.name}
                            />
                        </div>
                        <div className="location-gallery__side">
                            <img
                                src={location.images?.[1] || location.images?.[0] || location.main_image_url}
                                alt={location.name}
                            />
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
                            <p className="location-section__text">
                                {location.opening_hours || 'Liên hệ để biết thêm chi tiết'}
                            </p>
                        </section>

                        {/* General Info */}
                        <section className="location-section location-section--info">
                            <div className="location-section__header">
                                <div className="location-section__accent"></div>
                                <h2 className="location-section__title">Thông tin chung:</h2>
                            </div>
                            <p className={`location-section__text ${!isDescriptionExpanded ? 'location-section__text--truncated' : ''}`}>
                                {location.description || 'Chưa có thông tin mô tả.'}
                            </p>
                            {location.description && location.description.length > 200 && (
                                <button
                                    className="location-section__expand-btn"
                                    onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                                >
                                    {isDescriptionExpanded ? 'Thu gọn' : 'Xem thêm...'}
                                </button>
                            )}
                        </section>

                        {/* Price Section */}
                        <section className="location-section">
                            <div className="location-section__header">
                                <div className="location-section__accent"></div>
                                <h2 className="location-section__title">Giá:</h2>
                            </div>
                            <p className="location-price">
                                {location.price_min === 0 && location.price_max === 0 ? (
                                    <span className="location-price__free">Miễn phí</span>
                                ) : (
                                    <>
                                        <span className="location-price__value">
                                            {location.price_min?.toLocaleString('vi-VN') || 0}
                                        </span>
                                        <span className="location-price__unit"> VNĐ</span>
                                        <span className="location-price__separator"> - </span>
                                        <span className="location-price__value">
                                            {location.price_max?.toLocaleString('vi-VN') || 0}
                                        </span>
                                        <span className="location-price__unit"> VNĐ</span>
                                    </>
                                )}
                            </p>
                        </section>

                        {/* Posts */}
                        <section className="location-section" id="reviews">
                            <div className="location-section__header">
                                <div className="location-section__accent"></div>
                                <h2 className="location-section__title">Posts:</h2>
                            </div>
                            {renderPosts()}
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
                            {renderNearbyCards(nearbyPlaces, isLoadingNearby)}
                        </section>

                        {/* Recommendations */}
                        <section className="location-sidebar-section">
                            <div className="location-sidebar-section__header">
                                <div className="location-section__accent"></div>
                                <h2 className="location-sidebar-section__title">Có thể bạn sẽ thích</h2>
                                <Icons.Location className="location-sidebar-section__icon" />
                            </div>
                            {renderNearbyCards(suggestions, isLoadingSuggestions)}
                        </section>
                    </div>
                </div>
            </main>

            <Footer />
        </div>
    );
};

export default LocationInfoPage;
