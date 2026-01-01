import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCardHorizontal from '../../components/common/LocationCardHorizontal';
import BlogCard from '../../components/common/BlogCard';
import { Icons } from '../../config/constants';
import { placeService } from '../../services';
import { useAuthContext } from '../../contexts';
import { useScrollToTop } from '../../hooks';
import type { PlaceDetail, PlaceCompact } from '../../types/models';
import '../../assets/styles/pages/LocationInfoPage.css';


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
    const [favoriteIds, setFavoriteIds] = useState<number[]>([]);

    // Nearby & suggestions
    const [nearbyPlaces, setNearbyPlaces] = useState<PlaceCompact[]>([]);
    const [suggestions, setSuggestions] = useState<PlaceCompact[]>([]);
    const [isLoadingNearby, setIsLoadingNearby] = useState(true);
    const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(true);

    // UI state
    const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);

    // Carousel state
    const [currentSlide, setCurrentSlide] = useState(0);

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
            if (response.success && response.data) {
                // Filter out current place from nearby
                const filtered = response.data.filter(p => p.id !== Number(id));
                setNearbyPlaces(filtered.slice(0, 5));
            }
        } catch (err) {
            console.error('Error fetching nearby:', err);
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
            if (response.success && response.data) {
                // Filter out current place and nearby places to avoid duplicates
                const nearbyIds = new Set(nearbyPlaces.map(p => p.id));
                const filtered = response.data.filter(p =>
                    p.id !== Number(id) && !nearbyIds.has(p.id)
                );
                setSuggestions(filtered.slice(0, 5));
            }
        } catch (err) {
            console.error('Error fetching suggestions:', err);
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
            // Use profile API which includes recent_favorites
            const { userService } = await import('../../services');
            const profile = await userService.getProfile();
            if (profile.recent_favorites && profile.recent_favorites.length > 0) {
                const ids = profile.recent_favorites.map((p: PlaceCompact) => p.id);
                setFavoriteIds(ids);
                setIsFavorite(ids.includes(Number(id)));
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
        const posts = place?.related_posts || [];

        return (
            <div className="location-posts">
                {posts.map((post) => (
                    <div key={post._id} className="location-blog-card">
                        <BlogCard
                            id={post._id}
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
                            isLiked={post.is_liked || false}
                            isBanned={post.author?.is_banned}
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
                        isFavorite={favoriteIds.includes(loc.id)}
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

    if (!place) {
        return (
            <div className="location-info-page">
                <Header />
                <main className="location-info-main">
                    <div className="location-error">
                        <h2>Không tìm thấy địa điểm</h2>
                    </div>
                </main>
                <Footer />
            </div>
        );
    }

    const location = place;

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

                {/* Image Carousel */}
                <section className="location-gallery">
                    <div className="location-carousel">
                        {/* Main image viewport */}
                        <div className="location-carousel__viewport">
                            {(() => {
                                const images = location.images && location.images.length > 0
                                    ? location.images
                                    : [location.main_image_url];
                                return (
                                    <img
                                        src={images[currentSlide] || location.main_image_url}
                                        alt={`${location.name} - Ảnh ${currentSlide + 1}`}
                                        className="location-carousel__image"
                                    />
                                );
                            })()}
                        </div>

                        {/* Navigation arrows */}
                        {location.images && location.images.length > 1 && (
                            <>
                                <button
                                    className="location-carousel__arrow location-carousel__arrow--prev"
                                    onClick={() => {
                                        const images = location.images || [];
                                        setCurrentSlide(prev => prev === 0 ? images.length - 1 : prev - 1);
                                    }}
                                    aria-label="Previous image"
                                >
                                    ‹
                                </button>
                                <button
                                    className="location-carousel__arrow location-carousel__arrow--next"
                                    onClick={() => {
                                        const images = location.images || [];
                                        setCurrentSlide(prev => prev === images.length - 1 ? 0 : prev + 1);
                                    }}
                                    aria-label="Next image"
                                >
                                    ›
                                </button>
                            </>
                        )}

                        {/* Dots indicator */}
                        {location.images && location.images.length > 1 && (
                            <div className="location-carousel__dots">
                                {location.images.map((_, index) => (
                                    <button
                                        key={index}
                                        className={`location-carousel__dot ${currentSlide === index ? 'active' : ''}`}
                                        onClick={() => setCurrentSlide(index)}
                                        aria-label={`Go to image ${index + 1}`}
                                    />
                                ))}
                            </div>
                        )}
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
