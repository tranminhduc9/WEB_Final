/**
 * AdminPostsPage - Trang duyệt bài viết cho Admin
 * 
 * Features:
 * - Hiển thị danh sách bài viết pending
 * - Chấp nhận/Từ chối bài viết
 * - Phân trang
 */

import { useState, useEffect, useCallback } from 'react';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { adminService } from '../../services';
import { formatTimeAgo } from '../../utils/timeUtils';
import type { PostDetail, Pagination } from '../../types/models';
import '../../assets/styles/pages/AdminPostsPage.css';

// Default images
const defaultAvatar = 'https://i.pravatar.cc/88';
const placeholderImage = 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=600';


function AdminPostsPage() {
    const [posts, setPosts] = useState<PostDetail[]>([]);
    const [pagination, setPagination] = useState<Pagination | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());

    // Fetch pending posts
    const fetchPosts = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await adminService.getPosts({
                status: 'pending',
                page: currentPage
            });
            if (response.success && response.data) {
                setPosts(response.data);
                if (response.pagination) {
                    setPagination(response.pagination);
                }
            }
        } catch (err) {
            console.error('Error fetching pending posts:', err);
        } finally {
            setIsLoading(false);
        }
    }, [currentPage]);

    useEffect(() => {
        fetchPosts();
    }, [fetchPosts]);

    // Handle approve post
    const handleApprove = async (postId: string) => {
        setProcessingIds(prev => new Set(prev).add(postId));
        try {
            const response = await adminService.updatePostStatus(postId, 'published');
            if (response.success) {
                // Remove post from list (optimistic update)
                setPosts(prev => prev.filter(p => p._id !== postId));
            }
        } catch (err) {
            console.error('Error approving post:', err);
            alert('Có lỗi xảy ra khi duyệt bài!');
        } finally {
            setProcessingIds(prev => {
                const next = new Set(prev);
                next.delete(postId);
                return next;
            });
        }
    };

    // Handle reject post
    const handleReject = async (postId: string) => {
        setProcessingIds(prev => new Set(prev).add(postId));
        try {
            const response = await adminService.updatePostStatus(postId, 'rejected');
            if (response.success) {
                // Remove post from list (optimistic update)
                setPosts(prev => prev.filter(p => p._id !== postId));
            }
        } catch (err) {
            console.error('Error rejecting post:', err);
            alert('Có lỗi xảy ra khi từ chối bài!');
        } finally {
            setProcessingIds(prev => {
                const next = new Set(prev);
                next.delete(postId);
                return next;
            });
        }
    };

    // Pagination
    const totalPages = pagination?.total_pages || 1;

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const renderPagination = () => {
        if (totalPages <= 1) return null;

        const pages: (number | string)[] = [];
        if (totalPages <= 5) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else {
            pages.push(1, 2, 3);
            if (currentPage > 4) pages.push('...');
            if (currentPage > 3 && currentPage < totalPages - 2) {
                pages.push(currentPage);
            }
            if (currentPage < totalPages - 3) pages.push('...');
            pages.push(totalPages);
        }

        return (
            <div className="admin-posts__pagination">
                <button
                    className="admin-posts__pagination-nav"
                    onClick={() => handlePageChange(1)}
                    disabled={currentPage === 1}
                >
                    «
                </button>
                <button
                    className="admin-posts__pagination-nav"
                    onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                >
                    ‹
                </button>

                {pages.map((page, idx) => (
                    typeof page === 'number' ? (
                        <button
                            key={idx}
                            className={`admin-posts__pagination-btn ${currentPage === page ? 'active' : ''}`}
                            onClick={() => handlePageChange(page)}
                        >
                            {page}
                        </button>
                    ) : (
                        <span key={idx} className="admin-posts__pagination-ellipsis">{page}</span>
                    )
                ))}

                <button
                    className="admin-posts__pagination-nav"
                    onClick={() => handlePageChange(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                >
                    ›
                </button>
                <button
                    className="admin-posts__pagination-nav"
                    onClick={() => handlePageChange(totalPages)}
                    disabled={currentPage === totalPages}
                >
                    »
                </button>
            </div>
        );
    };

    return (
        <div className="admin-posts-page">
            <AdminHeader />

            <main className="admin-posts-main">
                {/* Title Section */}
                <div className="admin-posts-header">
                    <div className="admin-section__accent"></div>
                    <h1 className="admin-posts-title">Duyệt bài</h1>
                </div>

                {/* Posts List */}
                {isLoading ? (
                    <div className="admin-posts__loading">
                        <div className="loading-spinner"></div>
                        <p>Đang tải bài viết...</p>
                    </div>
                ) : posts.length === 0 ? (
                    <div className="admin-posts__empty">
                        <p>Không có bài viết nào đang chờ duyệt.</p>
                    </div>
                ) : (
                    <div className="admin-posts__list">
                        {posts.map((post) => (
                            <div key={post._id} className="admin-post-card">
                                {/* Header */}
                                <div className="admin-post-card__header">
                                    <div className="admin-post-card__author">
                                        <img
                                            src={post.author?.avatar_url || defaultAvatar}
                                            alt={post.author?.full_name || 'User'}
                                            className="admin-post-card__avatar"
                                        />
                                        <span className="admin-post-card__username">
                                            {post.author?.full_name || 'Người dùng'} • {formatTimeAgo(post.created_at)}
                                        </span>
                                    </div>
                                    <div className="admin-post-card__rating">
                                        {post.rating?.toFixed(1) || '0'}/5
                                    </div>
                                </div>

                                {/* Location */}
                                <div className="admin-post-card__location">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                                        <circle cx="12" cy="10" r="3" />
                                    </svg>
                                    <span>{post.related_place?.name || 'Hà Nội'}</span>
                                </div>

                                {/* Images */}
                                <div className="admin-post-card__images">
                                    <img
                                        src={post.images?.[0] || placeholderImage}
                                        alt="Post image 1"
                                        className="admin-post-card__image"
                                    />
                                    <img
                                        src={post.images?.[1] || post.images?.[0] || placeholderImage}
                                        alt="Post image 2"
                                        className="admin-post-card__image"
                                    />
                                </div>

                                {/* Description */}
                                <p className="admin-post-card__description">
                                    {post.content?.slice(0, 200)}
                                    {post.content && post.content.length > 200 && (
                                        <span className="admin-post-card__more"> xem toàn bộ bài viết...</span>
                                    )}
                                </p>

                                {/* Actions */}
                                <div className="admin-post-card__actions">
                                    <button
                                        className="admin-post-card__btn admin-post-card__btn--reject"
                                        onClick={() => handleReject(post._id)}
                                        disabled={processingIds.has(post._id)}
                                    >
                                        {processingIds.has(post._id) ? 'Đang xử lý...' : 'Từ chối'}
                                    </button>
                                    <button
                                        className="admin-post-card__btn admin-post-card__btn--approve"
                                        onClick={() => handleApprove(post._id)}
                                        disabled={processingIds.has(post._id)}
                                    >
                                        {processingIds.has(post._id) ? 'Đang xử lý...' : 'Chấp nhận'}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Pagination */}
                {!isLoading && posts.length > 0 && renderPagination()}
            </main>

            <Footer />
        </div>
    );
}

export default AdminPostsPage;
