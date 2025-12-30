import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
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
  const date = new Date(dateStr);
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

  // Mock data for testing
  const mockPost: PostDetail = {
    _id: id || 'mock-123',
    author: {
      id: 1,
      full_name: 'Nguyễn Văn A',
      avatar_url: '/duckk.jpg',
      role_id: 3
    },
    content: `Hồ Hoàn Kiếm (Hán-Nôm: 湖還劍) còn được gọi là Hồ Gươm là một hồ nước ngọt tự nhiên nằm ở phường Hoàn Kiếm, trung tâm thành phố Hà Nội. Hồ có diện tích khoảng 12 ha. Trước kia, hồ còn có các tên gọi là hồ Lục Thủy (vì nước có màu xanh quanh năm), hồ Thủy Quân (dùng để duyệt thủy binh).

Đây là một trong những địa điểm du lịch nổi tiếng nhất Hà Nội, thu hút hàng triệu du khách mỗi năm. Bạn có thể đi dạo quanh hồ vào buổi sáng sớm hoặc chiều tối để ngắm cảnh đẹp nhất.`,
    title: 'Review Hồ Gươm - Địa điểm không thể bỏ lỡ khi đến Hà Nội',
    rating: 4.5,
    images: [
      'https://images.unsplash.com/photo-1599708153386-62bf3f035e78?w=600&h=400&fit=crop',
      'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=600&h=400&fit=crop'
    ],
    likes_count: 128,
    comments_count: 24,
    is_liked: false,
    related_place: {
      id: 1,
      name: 'Hồ Gươm - Quận Hoàn Kiếm',
      district_id: 1,
      place_type_id: 1,
      rating_average: 4.8,
      price_min: 0,
      price_max: 0,
      main_image_url: 'https://images.unsplash.com/photo-1599708153386-62bf3f035e78?w=300'
    },
    comments: [
      {
        _id: 'cmt-1',
        user: { id: 2, full_name: 'Trần Văn B', avatar_url: '/duckk.jpg', role_id: 3 },
        content: 'Bài viết rất hay và chi tiết! Mình cũng rất thích đến Hồ Gươm vào buổi tối, không khí rất trong lành.',
        created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
      },
      {
        _id: 'cmt-2',
        user: { id: 3, full_name: 'Lê Thị C', avatar_url: '/duckk.jpg', role_id: 3 },
        content: 'Cảm ơn bạn đã chia sẻ! Mình đang plan trip đến Hà Nội tháng tới, chắc chắn sẽ ghé thăm.',
        parent_id: 'cmt-1',
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
      },
      {
        _id: 'cmt-3',
        user: { id: 4, full_name: 'Phạm Văn D', avatar_url: '/duckk.jpg', role_id: 3 },
        content: 'Hồ Gươm đẹp nhất vào mùa thu, lá vàng rơi rất thơ mộng!',
        created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
      }
    ],
    created_at: new Date(Date.now() - 20 * 60 * 60 * 1000).toISOString()
  };

  // Fetch post data
  const fetchPost = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await postService.getPostById(id);
      if (response.success && response.data) {
        setPost(response.data);
        setIsLiked(response.data.is_liked || false);
        setLikesCount(response.data.likes_count || 0);
      } else {
        // Fallback to mock data
        console.log('API returned empty, using mock data');
        setPost(mockPost);
        setIsLiked(mockPost.is_liked || false);
        setLikesCount(mockPost.likes_count || 0);
      }
    } catch (err) {
      console.error('Error fetching post, using mock data:', err);
      // Fallback to mock data for testing
      setPost(mockPost);
      setIsLiked(mockPost.is_liked || false);
      setLikesCount(mockPost.likes_count || 0);
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
        setIsLiked(response.is_liked);
        setLikesCount(response.likes_count);
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
              <span className="blog-detail__comment-username">
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

          {/* Report Button */}
          <div
            className="blog-detail__report"
            onClick={() => openReportModal('post', post._id)}
          >
            <span>Báo cáo</span>
            <Icons.Flag className="blog-detail__report-icon" />
          </div>

          {/* User Info */}
          <Link to={`/user/${post.author?.id}`} className="blog-detail__user-info">
            <img
              src={post.author?.avatar_url || defaultAvatar}
              alt={post.author?.full_name || 'User'}
              className="blog-detail__avatar"
            />
            <span className="blog-detail__username">
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

          {/* Images */}
          {post.images && post.images.length > 0 && (
            <div className="blog-detail__images">
              {post.images.slice(0, 2).map((img, idx) => (
                <img
                  key={idx}
                  src={img || placeholderImage}
                  alt={`Post ${idx + 1}`}
                  className="blog-detail__image"
                />
              ))}
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
