import React, { useState, useEffect, useCallback } from 'react';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import BlogCard from '../../components/common/BlogCard';
import CreatePostModal from '../../components/client/CreatePostModal';
import { postService } from '../../services';
import type { PostDetail, Pagination } from '../../types/models';
import '../../assets/styles/pages/BlogPage.css';

// Default placeholder image
const placeholderImage = 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=600';
const defaultAvatar = 'https://i.pravatar.cc/88';


// Helper function to format time ago
const formatTimeAgo = (dateString?: string): string => {
  if (!dateString) return 'Vừa xong';

  const now = new Date();
  const date = new Date(dateString);
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  if (diffHours < 1) return 'Vừa xong';
  if (diffHours < 24) return `${diffHours} giờ`;
  if (diffDays < 7) return `${diffDays} ngày`;
  return date.toLocaleDateString('vi-VN');
};

const BlogPage: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [posts, setPosts] = useState<PostDetail[]>([]);
  const [pagination, setPagination] = useState<Pagination | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const itemsPerPage = 10;

  // Fetch posts
  const fetchPosts = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await postService.getPosts(currentPage, itemsPerPage);
      if (response.data && response.data.length > 0) {
        setPosts(response.data);
        if (response.pagination) {
          setPagination(response.pagination);
        }
      }
    } catch (err) {
      console.error('Error fetching posts:', err);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  // Handle post creation
  const handleCreatePost = async (data: {
    location: string;
    related_place_id?: number;
    rating: number;
    content: string;
    images: File[]
  }) => {
    try {
      let imageUrls: string[] = [];

      // Upload images first if any
      if (data.images && data.images.length > 0) {
        try {
          const uploadResponse = await postService.uploadPostImages(data.images);
          if (uploadResponse.success && uploadResponse.urls) {
            imageUrls = uploadResponse.urls;
          }
        } catch (uploadError) {
          console.error('Error uploading images:', uploadError);
          // Continue with post creation even if image upload fails
        }
      }

      // Create post with uploaded image URLs
      await postService.createPost({
        title: data.content.slice(0, 50) || 'Bài viết mới',
        content: data.content,
        rating: data.rating || undefined,
        related_place_id: data.related_place_id,
        images: imageUrls  // Sử dụng URLs đã upload
      });

      setIsModalOpen(false);
      alert('Đăng bài thành công! Bài viết đang chờ duyệt.');
      fetchPosts();
    } catch (err) {
      console.error('Error creating post:', err);
      alert('Có lỗi xảy ra khi đăng bài. Vui lòng thử lại!');
    }
  };

  // Map PostDetail to BlogCard props
  const mapPostToCard = (post: PostDetail) => ({
    id: post._id,
    authorId: post.author?.id,
    avatarSrc: post.author?.avatar_url || defaultAvatar,
    username: post.author?.full_name || 'Người dùng',
    timeAgo: formatTimeAgo(post.created_at),
    location: post.related_place?.name || 'Hà Nội',
    rating: post.rating || 0,
    imageSrc1: post.images?.[0] || placeholderImage,
    imageSrc2: post.images?.[1] || post.images?.[0] || placeholderImage,
    likeCount: post.likes_count || 0,
    commentCount: post.comments_count || 0,
    description: post.content?.slice(0, 150) || '',
    isLiked: post.is_liked || false
  });

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const totalPages = pagination?.total_pages || 1;

  // Render pagination
  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const pages: (number | string)[] = [];

    if (totalPages <= 5) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push('...');

      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) pages.push(i);

      if (currentPage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }

    return (
      <div className="blog-page__pagination">
        <button
          className="blog-page__pagination-arrow"
          onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
        >
          «
        </button>

        {pages.map((page, idx) => (
          typeof page === 'number' ? (
            <button
              key={idx}
              className={`blog-page__pagination-btn ${currentPage === page ? 'active' : ''}`}
              onClick={() => handlePageChange(page)}
            >
              {page}
            </button>
          ) : (
            <span key={idx} className="blog-page__pagination-ellipsis">{page}</span>
          )
        ))}

        <button
          className="blog-page__pagination-arrow"
          onClick={() => handlePageChange(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage === totalPages}
        >
          »
        </button>
      </div>
    );
  };

  // Get display data
  const displayPosts = posts.map(mapPostToCard);

  return (
    <>
      <Header />
      <div className="blog-page">
        {/* Chia sẻ trải nghiệm Section */}
        <section className="blog-page__share-section">
          <h1 className="blog-page__title">Chia sẻ trải nghiệm</h1>
          <div
            className="blog-page__input-box"
            onClick={() => setIsModalOpen(true)}
            style={{ cursor: 'pointer' }}
          >
            <span className="blog-page__input-placeholder">
              Hãy chia sẻ trải nghiệm của bạn!!
            </span>
          </div>
        </section>

        {/* Create Post Modal */}
        <CreatePostModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleCreatePost}
        />

        {/* Newfeed Section */}
        <section className="blog-page__newfeed-section">
          <h2 className="blog-page__section-title">Newfeed</h2>

          {isLoading ? (
            <div className="blog-page__loading">
              <div className="loading-spinner"></div>
              <p>Đang tải bài viết...</p>
            </div>
          ) : (
            <div className="blog-page__posts">
              {displayPosts.map((post) => (
                <BlogCard
                  key={post.id}
                  id={post.id}
                  authorId={post.authorId}
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
              ))}
            </div>
          )}
        </section>

        {/* Pagination */}
        {!isLoading && displayPosts.length > 0 && renderPagination()}
      </div>
      <Footer />
    </>
  );
};

export default BlogPage;
