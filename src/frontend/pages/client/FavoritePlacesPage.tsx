/**
 * Favorite Places Page - Trang địa điểm yêu thích
 * Route: /places/favourite (own) or /places/favourite/:userId (other user)
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCard from '../../components/common/LocationCard';
import { useAuthContext } from '../../contexts';
import { userService } from '../../services';
import type { PlaceCompact } from '../../types/models';
import '../../assets/styles/pages/FavoritePlacesPage.css';

// Items per page
const ITEMS_PER_PAGE = 9;

const FavoritePlacesPage: React.FC = () => {
    const navigate = useNavigate();
    const { userId } = useParams<{ userId: string }>();
    const { isAuthenticated, isLoading: authLoading, user: currentUser } = useAuthContext();

    // Determine if viewing own favorites
    const isOwnProfile = !userId || (currentUser && String(currentUser.id) === userId);

    const [favorites, setFavorites] = useState<PlaceCompact[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const [userName, setUserName] = useState<string>('');

    // Redirect to login if viewing own favorites and not authenticated
    useEffect(() => {
        if (!authLoading && !isAuthenticated && isOwnProfile) {
            navigate('/login', { state: { from: '/places/favourite' } });
        }
    }, [authLoading, isAuthenticated, isOwnProfile, navigate]);

    // Fetch favorites
    useEffect(() => {
        const fetchFavorites = async () => {
            // If viewing own and not authenticated, skip
            if (isOwnProfile && !isAuthenticated) return;

            setIsLoading(true);
            try {
                if (isOwnProfile) {
                    // Fetch own favorites
                    const profile = await userService.getProfile();
                    if (profile.recent_favorites && profile.recent_favorites.length > 0) {
                        setFavorites(profile.recent_favorites);
                    }
                    setUserName(profile.full_name || 'Bạn');
                } else {
                    // Fetch other user's favorites
                    const profile = await userService.getUserProfile(userId!);
                    if (profile.recent_favorites && profile.recent_favorites.length > 0) {
                        setFavorites(profile.recent_favorites);
                    }
                    setUserName(profile.full_name || 'Người dùng');
                }
            } catch (error) {
                console.error('Error fetching favorites:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchFavorites();
    }, [isAuthenticated, isOwnProfile, userId]);

    // Pagination logic
    const totalPages = Math.ceil(favorites.length / ITEMS_PER_PAGE);
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const currentItems = favorites.slice(startIndex, startIndex + ITEMS_PER_PAGE);

    const handlePageChange = (page: number) => {
        if (page >= 1 && page <= totalPages) {
            setCurrentPage(page);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    // Generate page numbers
    const getPageNumbers = () => {
        const pages: (number | string)[] = [];
        if (totalPages <= 5) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else {
            pages.push(1);
            if (currentPage > 3) pages.push('...');
            for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
                pages.push(i);
            }
            if (currentPage < totalPages - 2) pages.push('...');
            pages.push(totalPages);
        }
        return pages;
    };

    // Loading state
    if (authLoading || isLoading) {
        return (
            <>
                <Header />
                <div className="favorites-page favorites-page--loading">
                    <div className="favorites-loading">
                        <div className="loading-spinner"></div>
                        <p>Đang tải địa điểm yêu thích...</p>
                    </div>
                </div>
                <Footer />
            </>
        );
    }

    return (
        <>
            <Header />
            <div className="favorites-page">
                {/* Title Section */}
                <section className="favorites-header">
                    <h1 className="favorites-title">
                        <span className="favorites-title__bar"></span>
                        Địa điểm yêu thích
                        <span className="favorites-title__icon">📍</span>
                    </h1>
                </section>

                {/* Favorites Grid */}
                {favorites.length > 0 ? (
                    <>
                        <section className="favorites-grid">
                            {currentItems.map((place) => (
                                <LocationCard
                                    key={place.id}
                                    id={String(place.id)}
                                    imageSrc={place.main_image_url || ''}
                                    title={place.name}
                                    address={place.address || place.district_name || 'Hà Nội'}
                                    priceMin={place.price_min}
                                    priceMax={place.price_max}
                                    rating={place.rating_average}
                                    reviewCount={place.rating_count || 0}
                                />
                            ))}
                        </section>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="favorites-pagination">
                                {/* Prev buttons */}
                                <button
                                    className="pagination-btn pagination-btn--nav"
                                    onClick={() => handlePageChange(1)}
                                    disabled={currentPage === 1}
                                >
                                    «
                                </button>
                                <button
                                    className="pagination-btn pagination-btn--nav"
                                    onClick={() => handlePageChange(currentPage - 1)}
                                    disabled={currentPage === 1}
                                >
                                    ‹
                                </button>

                                {/* Page numbers */}
                                {getPageNumbers().map((page, idx) => (
                                    <button
                                        key={idx}
                                        className={`pagination-btn ${page === currentPage ? 'pagination-btn--active' : ''} ${page === '...' ? 'pagination-btn--ellipsis' : ''}`}
                                        onClick={() => typeof page === 'number' && handlePageChange(page)}
                                        disabled={page === '...'}
                                    >
                                        {page}
                                    </button>
                                ))}

                                {/* Next buttons */}
                                <button
                                    className="pagination-btn pagination-btn--nav"
                                    onClick={() => handlePageChange(currentPage + 1)}
                                    disabled={currentPage === totalPages}
                                >
                                    ›
                                </button>
                                <button
                                    className="pagination-btn pagination-btn--nav"
                                    onClick={() => handlePageChange(totalPages)}
                                    disabled={currentPage === totalPages}
                                >
                                    »
                                </button>
                            </div>
                        )}
                    </>
                ) : (
                    <div className="favorites-empty">
                        <p>Bạn chưa có địa điểm yêu thích nào.</p>
                        <Link to="/places" className="favorites-empty__link">
                            Khám phá địa điểm →
                        </Link>
                    </div>
                )}
            </div>
            <Footer />
        </>
    );
};

export default FavoritePlacesPage;
