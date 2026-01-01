import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import { Icons } from '../../config/constants';
import { postService } from '../../services';
import { useAuthContext } from '../../contexts';
import { useScrollToTop } from '../../hooks';
import type { PostDetail, PostCommentInDetail } from '../../types/models';
import '../../assets/styles/pages/BlogDetailPage.css';

// Placeholder image URL
const placeholderImage = 'https://images.unsplash.com/photo-1599708153386-62bf3f035e78?w=600&h=400&fit=crop';
const defaultAvatar = '/duckk.jpg';

// Format time ago helper
const formatTimeAgo = (dateStr?: string): string => {
  if (!dateStr) return '';

  // Backend returns UTC time without 'Z' suffix, add it if missing
  let normalizedDateStr = dateStr;
  if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
    normalizedDateStr = dateStr + 'Z';
  }

  const date = new Date(normalizedDateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffDays > 0) return `${diffDays} ngày trước`;
  if (diffHours > 0) return `${diffHours} giờ trước`;
  if (diffMins > 0) return `${diffMins} phút trước`;
  return 'Vừa xong';
};

const BlogDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated, user } = useAuthContext();

  // Scroll to top on navigation
  useScrollToTop();

  // Post states
  const [post, setPost] = useState<PostDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Like states
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);
  const [isLiking, setIsLiking] = useState(false);

  // Comment states
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [replyContent, setReplyContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deletingCommentId, setDeletingCommentId] = useState<string | null>(null);

  // Report modal states
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportTarget, setReportTarget] = useState<{ type: 'post' | 'comment'; id: string } | null>(null);
  const [reportReason, setReportReason] = useState('');
  const [isReporting, setIsReporting] = useState(false);

  // Carousel state
  const [currentImageSlide, setCurrentImageSlide] = useState(0);

  // Delete post state
  const [isDeletingPost, setIsDeletingPost] = useState(false);
  const navigate = useNavigate();


  // Fetch post data
  const fetchPost = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await postService.getPostById(id);
      if (response.success && response.data) {
        setPost(response.data);
        // Ensure is_liked is properly set (handle both boolean and undefined)
        const likedStatus = response.data.is_liked === true;
        setIsLiked(likedStatus);
        setLikesCount(response.data.likes_count || 0);
      } else {
        setError('Không tìm thấy bài viết');
      }
    } catch (err) {
      console.error('Error fetching post:', err);
      setError('Không thể tải bài viết');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchPost();
  }, [fetchPost]);

  // Handle Like toggle
  const handleLike = async () => {
    if (!isAuthenticated) {
      alert('Vui lòng đăng nhập để thích bài viết');
      return;
    }
    if (!id || isLiking) return;

    setIsLiking(true);
    try {
      const response = await postService.toggleLike(id);
      if (response.success) {
        // Ensure is_liked is properly set (handle both boolean and undefined)
        const likedStatus = response.is_liked === true;
        setIsLiked(likedStatus);
        setLikesCount(response.likes_count || 0);
      }
    } catch (err) {
      console.error('Error toggling like:', err);
      alert('Có lỗi xảy ra. Vui lòng thử lại.');
    } finally {
      setIsLiking(false);
    }
  };

  // Handle Add Comment
  const handleAddComment = async () => {
    if (!isAuthenticated) {
      alert('Vui lòng đăng nhập để bình luận');
      return;
    }
    if (!id || !newComment.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await postService.addComment(id, newComment.trim());
      setNewComment('');
      // Refresh post to get new comments
      await fetchPost();
    } catch (err) {
      console.error('Error adding comment:', err);
      alert('Có lỗi xảy ra khi gửi bình luận. Vui lòng thử lại.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle Reply to Comment
  const handleReply = async (commentId: string) => {
    if (!isAuthenticated) {
      alert('Vui lòng đăng nhập để trả lời');
      return;
    }
    if (!replyContent.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await postService.replyToComment(commentId, replyContent.trim());
      setReplyingTo(null);
      setReplyContent('');
      // Refresh post to get new replies
      await fetchPost();
    } catch (err) {
      console.error('Error replying to comment:', err);
      alert('Có lỗi xảy ra khi gửi trả lời. Vui lòng thử lại.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Open Report Modal
  const openReportModal = (type: 'post' | 'comment', targetId: string) => {
    if (!isAuthenticated) {
      alert('Vui lòng đăng nhập để báo cáo');
      return;
    }
    setReportTarget({ type, id: targetId });
    setShowReportModal(true);
  };

  // Handle Report
  const handleReport = async () => {
    if (!reportTarget || !reportReason.trim() || isReporting) return;

    setIsReporting(true);
    try {
      if (reportTarget.type === 'post') {
        await postService.reportPost(reportTarget.id, reportReason.trim());
      } else {
        await postService.reportComment(reportTarget.id, reportReason.trim());
      }
      alert('Báo cáo đã được gửi. Cảm ơn bạn!');
      setShowReportModal(false);
      setReportTarget(null);
      setReportReason('');
    } catch (err) {
      console.error('Error reporting:', err);
      alert('Có lỗi xảy ra khi gửi báo cáo. Vui lòng thử lại.');
    } finally {
      setIsReporting(false);
    }
  };

  // Handle Delete Comment
  const handleDeleteComment = async (commentId: string) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa bình luận này?')) {
      return;
    }

    setDeletingCommentId(commentId);
    try {
      const response = await postService.deleteOwnComment(commentId);
      if (response.success) {
        alert('Đã xóa bình luận thành công!');
        // Refresh post to update comments list
        await fetchPost();
      } else {
        alert('Không thể xóa bình luận: ' + (response.message || 'Lỗi không xác định'));
      }
    } catch (error: any) {
      console.error('Delete comment error:', error);
      if (error.response?.status === 403) {
        alert('Bạn không có quyền xóa bình luận này');
      } else {
        alert('Có lỗi xảy ra khi xóa bình luận');
      }
    } finally {
      setDeletingCommentId(null);
    }
  };

  // Handle Delete Post (for post owner)
  const handleDeletePost = async () => {
    if (!post || !id) return;

    if (!window.confirm('Bạn có chắc chắn muốn xóa bài viết này? Hành động này không thể hoàn tác.')) {
      return;
    }

    setIsDeletingPost(true);
    try {
      const response = await postService.deleteOwnPost(id);
      if (response.success) {
        alert('Đã xóa bài viết thành công!');
        navigate('/blogs');
      } else {
        alert('Không thể xóa bài viết: ' + (response.message || 'Lỗi không xác định'));
      }
    } catch (error: any) {
      console.error('Delete post error:', error);
      if (error.response?.status === 403) {
        alert('Bạn không có quyền xóa bài viết này');
      } else {
        alert('Có lỗi xảy ra khi xóa bài viết');
      }
    } finally {
      setIsDeletingPost(false);
    }
  };

  // Render comment item
  const renderComment = (comment: PostCommentInDetail, isReply = false) => {
    const isCommentOwner = isAuthenticated && user && comment.user?.id === user.id;
    const isDeleting = deletingCommentId === comment._id;

    return (
      <div key={comment._id} className={isReply ? 'blog-detail__reply' : 'blog-detail__comment'}>
        <Link to={`/user/${comment.user?.id}`}>
          <img
            src={comment.user?.avatar_url || defaultAvatar}
            alt={comment.user?.full_name || 'User'}
            className="blog-detail__comment-avatar blog-detail__comment-avatar--clickable"
          />
        </Link>
        <div className="blog-detail__comment-content">
          <div className="blog-detail__comment-header">
            <Link to={`/user/${comment.user?.id}`} className="blog-detail__comment-username-link">
              <span className={`blog-detail__comment-username ${comment.user?.is_banned ? 'blog-detail__username--banned' : ''}`}>
                {comment.user?.full_name || 'Người dùng'}
              </span>
            </Link>
            <p className="blog-detail__comment-text">{comment.content}</p>
          </div>
          <div className="blog-detail__comment-footer">
            <span className="blog-detail__comment-time">
              {formatTimeAgo(comment.created_at)}
            </span>
            {!isReply && (
              <button
                className="blog-detail__comment-reply"
                onClick={() => setReplyingTo(comment._id)}
              >
                <Icons.Comment className="blog-detail__comment-icon" />
                <span>Trả lời</span>
              </button>
            )}
            {/* Delete button for owner, Report button for others */}
            {isCommentOwner ? (
              <button
                className="blog-detail__comment-delete"
                onClick={() => handleDeleteComment(comment._id)}
                disabled={isDeleting}
              >
                <Icons.Trash className="blog-detail__comment-icon" />
                <span>{isDeleting ? 'Đang xóa...' : 'Xóa'}</span>
              </button>
            ) : isAuthenticated ? (
              <button
                className="blog-detail__comment-report"
                onClick={() => openReportModal('comment', comment._id)}
              >
                <Icons.Flag className="blog-detail__comment-icon" />
                <span>Báo cáo</span>
              </button>
            ) : null}
          </div>

          {/* Reply Input */}
          {replyingTo === comment._id && (
            <div className="blog-detail__reply-input">
              <textarea
                placeholder="Viết trả lời..."
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                disabled={isSubmitting}
              />
              <div className="blog-detail__reply-actions">
                <button
                  onClick={() => {
                    setReplyingTo(null);
                    setReplyContent('');
                  }}
                  disabled={isSubmitting}
                >
                  Hủy
                </button>
                <button
                  onClick={() => handleReply(comment._id)}
                  disabled={isSubmitting || !replyContent.trim()}
                >
                  {isSubmitting ? 'Đang gửi...' : 'Gửi'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Loading state
  if (isLoading) {
    return (
      <>
        <Header />
        <div className="blog-detail-page blog-detail-page--loading">
          <div className="blog-detail__loading">
            <div className="loading-spinner"></div>
            <p>Đang tải bài viết...</p>
          </div>
        </div>
        <Footer />
      </>
    );
  }

  // Error state
  if (error || !post) {
    return (
      <>
        <Header />
        <div className="blog-detail-page blog-detail-page--error">
          <div className="blog-detail__error">
            <h2>😕 {error || 'Không tìm thấy bài viết'}</h2>
            <Link to="/blogs" className="blog-detail__back-link">
              ← Quay lại danh sách bài viết
            </Link>
          </div>
        </div>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="blog-detail-page">
        {/* Post Section */}
        <section className="blog-detail__post">
          {/* Rating Badge */}
          {post.rating && (
            <div className="blog-detail__rating-badge">
              {post.rating}/5
            </div>
          )}

          {/* Delete Button for Owner / Report Button for Others */}
          {isAuthenticated && user && post.author?.id === user.id ? (
            <button
              className="blog-detail__delete"
              onClick={handleDeletePost}
              disabled={isDeletingPost}
            >
              <span>{isDeletingPost ? 'Đang xóa...' : 'Xóa bài viết'}</span>
              <Icons.Trash className="blog-detail__delete-icon" />
            </button>
          ) : (
            <div
              className="blog-detail__report"
              onClick={() => openReportModal('post', post._id)}
            >
              <span>Báo cáo</span>
              <Icons.Flag className="blog-detail__report-icon" />
            </div>
          )}

          {/* User Info */}
          <Link to={`/user/${post.author?.id}`} className="blog-detail__user-info">
            <img
              src={post.author?.avatar_url || defaultAvatar}
              alt={post.author?.full_name || 'User'}
              className="blog-detail__avatar"
            />
            <span className={`blog-detail__username ${post.author?.is_banned ? 'blog-detail__username--banned' : ''}`}>
              {post.author?.full_name || 'Người dùng'} • {formatTimeAgo(post.created_at)}
            </span>
          </Link>

          {/* Location */}
          {post.related_place && (
            <Link
              to={`/location/${post.related_place.id}`}
              className="blog-detail__location"
            >
              <Icons.Location className="blog-detail__location-icon" />
              <span>{post.related_place.name}</span>
            </Link>
          )}

          {/* Image Carousel */}
          {post.images && post.images.length > 0 && (
            <div className="blog-detail__carousel">
              {/* Main image */}
              <div className="blog-detail__carousel-viewport">
                <img
                  src={post.images[currentImageSlide] || placeholderImage}
                  alt={`Post image ${currentImageSlide + 1}`}
                  className="blog-detail__carousel-image"
                />
              </div>

              {/* Navigation arrows */}
              {post.images.length > 1 && (
                <>
                  <button
                    className="blog-detail__carousel-arrow blog-detail__carousel-arrow--prev"
                    onClick={() => setCurrentImageSlide(prev => prev === 0 ? post.images!.length - 1 : prev - 1)}
                    aria-label="Previous image"
                  >
                    ‹
                  </button>
                  <button
                    className="blog-detail__carousel-arrow blog-detail__carousel-arrow--next"
                    onClick={() => setCurrentImageSlide(prev => prev === post.images!.length - 1 ? 0 : prev + 1)}
                    aria-label="Next image"
                  >
                    ›
                  </button>
                </>
              )}

              {/* Dots indicator */}
              {post.images.length > 1 && (
                <div className="blog-detail__carousel-dots">
                  {post.images.map((_, index) => (
                    <button
                      key={index}
                      className={`blog-detail__carousel-dot ${currentImageSlide === index ? 'active' : ''}`}
                      onClick={() => setCurrentImageSlide(index)}
                      aria-label={`Go to image ${index + 1}`}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="blog-detail__actions">
            <div
              className={`blog-detail__action ${isLiked ? 'blog-detail__action--liked' : ''}`}
              onClick={handleLike}
            >
              <Icons.Heart className="blog-detail__action-icon" />
              <span>{likesCount}</span>
            </div>
            <div className="blog-detail__action">
              <Icons.Comment className="blog-detail__action-icon" />
              <span>{post.comments_count || 0}</span>
            </div>
          </div>

          {/* Description */}
          <p className="blog-detail__description">{post.content}</p>
        </section>

        {/* Comments Section */}
        <section className="blog-detail__comments">
          <h2 className="blog-detail__comments-title">Bình luận</h2>

          {/* Add Comment Input */}
          {isAuthenticated ? (
            <div className="blog-detail__comment-input">
              <textarea
                placeholder="Viết bình luận..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                disabled={isSubmitting}
              />
              <button
                onClick={handleAddComment}
                disabled={isSubmitting || !newComment.trim()}
              >
                {isSubmitting ? 'Đang gửi...' : 'Gửi'}
              </button>
            </div>
          ) : (
            <div className="blog-detail__login-prompt">
              <Link to="/login">Đăng nhập</Link> để bình luận
            </div>
          )}

          {/* Comments List */}
          <div className="blog-detail__comments-list">
            {post.comments && post.comments.length > 0 ? (
              post.comments
                .filter((c) => !c.parent_id) // Root comments only
                .map((comment) => (
                  <div key={comment._id} className="blog-detail__comment-wrapper">
                    {renderComment(comment)}

                    {/* Replies */}
                    {post.comments
                      ?.filter((r) => r.parent_id === comment._id)
                      .map((reply) => renderComment(reply, true))}
                  </div>
                ))
            ) : (
              <p className="blog-detail__no-comments">
                Chưa có bình luận nào. Hãy là người đầu tiên!
              </p>
            )}
          </div>
        </section>
      </div>

      {/* Report Modal */}
      {showReportModal && (
        <div
          className="blog-detail__report-modal-overlay"
          onClick={() => setShowReportModal(false)}
        >
          <div
            className="blog-detail__report-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>
              Báo cáo {reportTarget?.type === 'post' ? 'bài viết' : 'bình luận'}
            </h3>
            <select
              value={reportReason}
              onChange={(e) => setReportReason(e.target.value)}
            >
              <option value="">Chọn lý do</option>
              <option value="spam">Spam</option>
              <option value="harassment">Quấy rối</option>
              <option value="inappropriate">Nội dung không phù hợp</option>
              <option value="misinformation">Thông tin sai lệch</option>
              <option value="other">Khác</option>
            </select>
            <div className="blog-detail__report-modal-actions">
              <button onClick={() => setShowReportModal(false)}>Hủy</button>
              <button
                onClick={handleReport}
                disabled={!reportReason || isReporting}
              >
                {isReporting ? 'Đang gửi...' : 'Gửi báo cáo'}
              </button>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </>
  );
};

export default BlogDetailPage;
