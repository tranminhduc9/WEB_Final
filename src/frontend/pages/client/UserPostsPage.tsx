/**
 * User Posts Page - Trang bài viết của người dùng
 * Route: /posts/user (own) or /posts/user/:userId (other user)
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import { useAuthContext } from '../../contexts';
import { userService } from '../../services';
import type { PostDetail } from '../../types/models';
import '../../assets/styles/pages/UserPostsPage.css';

// Items per page
const ITEMS_PER_PAGE = 3;

// Format time ago helper
const formatTimeAgo = (dateStr?: string): string => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 60) return `${diffMins} phút`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} giờ`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} ngày`;
};

const UserPostsPage: React.FC = () => {
    const navigate = useNavigate();
    const { userId } = useParams<{ userId: string }>();
    const { isAuthenticated, isLoading: authLoading, user: currentUser } = useAuthContext();

    // Determine if viewing own posts
    const isOwnProfile = !userId || (currentUser && String(currentUser.id) === userId);

    const [posts, setPosts] = useState<PostDetail[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const [userName, setUserName] = useState<string>('');

    // Redirect to login if viewing own posts and not authenticated
    useEffect(() => {
        if (!authLoading && !isAuthenticated && isOwnProfile) {
            navigate('/login', { state: { from: '/posts/user' } });
        }
    }, [authLoading, isAuthenticated, isOwnProfile, navigate]);

    // Fetch posts
    useEffect(() => {
        const fetchPosts = async () => {
            // If viewing own and not authenticated, skip
            if (isOwnProfile && !isAuthenticated) return;

            setIsLoading(true);
            try {
                if (isOwnProfile) {
                    // Fetch own posts
                    const profile = await userService.getProfile();
                    if (profile.recent_posts && profile.recent_posts.length > 0) {
                        setPosts(profile.recent_posts);
                    }
                    setUserName(currentUser?.name || currentUser?.full_name || 'bạn');
                } else {
                    // Fetch other user's posts
                    const profile = await userService.getUserProfile(userId!);
                    if (profile.recent_posts && profile.recent_posts.length > 0) {
                        setPosts(profile.recent_posts);
                    }
                    setUserName(profile.full_name || 'người dùng');
                }
            } catch (error) {
                console.error('Error fetching posts:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchPosts();
    }, [isAuthenticated, isOwnProfile, userId, currentUser]);

    // Pagination logic
    const totalPages = Math.ceil(posts.length / ITEMS_PER_PAGE);
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const currentItems = posts.slice(startIndex, startIndex + ITEMS_PER_PAGE);

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
                <div className="user-posts-page user-posts-page--loading">
                    <div className="user-posts-loading">
                        <div className="loading-spinner"></div>
                        <p>Đang tải bài viết...</p>
                    </div>
                </div>
                <Footer />
            </>
        );
    }

    // Title uses userName from state (set during fetch)

    return (
        <>
            <Header />
            <div className="user-posts-page">
                {/* Title Section */}
                <section className="user-posts-header">
                    <h1 className="user-posts-title">
                        <span className="user-posts-title__bar"></span>
                        Bài viết của '{userName}'
                    </h1>
                </section>

                {/* Posts List */}
                {posts.length > 0 ? (
                    <>
                        <section className="user-posts-list">
                            {currentItems.map((post) => (
                                <article key={post._id} className="blog-card">
                                    {/* Header: Avatar, Username, Time, Rating */}
                                    <div className="blog-card__header">
                                        <div className="blog-card__user">
                                            {post.author?.avatar_url ? (
                                                <img
                                                    src={post.author.avatar_url}
                                                    alt={post.author.full_name}
                                                    className="blog-card__avatar"
                                                />
                                            ) : (
                                                <div className="blog-card__avatar blog-card__avatar--placeholder">
                                                    {post.author?.full_name?.charAt(0) || 'U'}
                                                </div>
                                            )}
                                            <div className="blog-card__user-info">
                                                <span className="blog-card__username">
                                                    {post.author?.full_name || 'Ẩn danh'} • {formatTimeAgo(post.created_at)}
                                                </span>
                                                {post.related_place && (
                                                    <span className="blog-card__location">
                                                        📍 {post.related_place.name}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        {post.rating && (
                                            <div className="blog-card__rating">
                                                {post.rating}/5
                                            </div>
                                        )}
                                    </div>

                                    {/* Images */}
                                    <div className="blog-card__images">
                                        {post.images?.slice(0, 2).map((img, idx) => (
                                            <img
                                                key={idx}
                                                src={img}
                                                alt={`Post image ${idx + 1}`}
                                                className="blog-card__image"
                                            />
                                        ))}
                                    </div>

                                    {/* Footer: Likes, Comments, Content */}
                                    <div className="blog-card__footer">
                                        <div className="blog-card__stats">
                                            <span className="blog-card__stat">
                                                ❤️ {post.likes_count || 0}
                                            </span>
                                            <span className="blog-card__stat">
                                                💬 {post.comments_count || 0}
                                            </span>
                                        </div>
                                        <p className="blog-card__content">
                                            {post.content?.slice(0, 100)}
                                            {post.content && post.content.length > 100 && (
                                                <Link to={`/blog/${post._id}`} className="blog-card__read-more">
                                                    xem toàn bộ bài viết...
                                                </Link>
                                            )}
                                        </p>
                                    </div>
                                </article>
                            ))}
                        </section>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="user-posts-pagination">
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
                    <div className="user-posts-empty">
                        <p>Bạn chưa có bài viết nào.</p>
                        <Link to="/blogs" className="user-posts-empty__link">
                            Khám phá bài viết →
                        </Link>
                    </div>
                )}
            </div>
            <Footer />
        </>
    );
};

export default UserPostsPage;
