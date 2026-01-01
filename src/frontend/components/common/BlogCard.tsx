import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icons } from '../../config/constants';
import { useAuthContext } from '../../contexts';
import { postService } from '../../services';
import '../../assets/styles/components/BlogCard.css';

interface BlogCardProps {
  id: string | number; // Support both string (API) and number
  authorId?: number;   // User ID for profile link
  avatarSrc: string;
  username: string;
  timeAgo: string;
  location: string;
  rating: number;
  imageSrc1: string;
  imageSrc2: string;
  likeCount: number;
  commentCount: number;
  description: string;
  isLiked?: boolean;   // Initial like state from parent
  onDeleted?: () => void; // Callback when post is deleted
  onLikeChanged?: (isLiked: boolean, newCount: number) => void; // Callback when like changes
  isBanned?: boolean; // User banned status
}

const BlogCard: React.FC<BlogCardProps> = ({
  id,
  authorId,
  avatarSrc,
  username,
  timeAgo,
  location,
  rating,
  imageSrc1,
  imageSrc2,
  likeCount,
  commentCount,
  description,
  isLiked: initialIsLiked = false,
  onDeleted,
  onLikeChanged,
  isBanned = false,
}) => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuthContext();
  const [isDeleting, setIsDeleting] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [isReporting, setIsReporting] = useState(false);

  // Like state
  const [liked, setLiked] = useState(initialIsLiked);
  const [currentLikeCount, setCurrentLikeCount] = useState(likeCount);
  const [isLiking, setIsLiking] = useState(false);

  // Check if current user is the author
  const isOwner = isAuthenticated && user && authorId && user.id === authorId;

  const handleCardClick = () => {
    navigate(`/blog/${id}`);
  };

  const handleUserClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click
    if (authorId) {
      navigate(`/user/${authorId}`);
    }
  };

  const handleLikeClick = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click

    if (!isAuthenticated) {
      alert('Vui lòng đăng nhập để thích bài viết');
      navigate('/login');
      return;
    }

    if (isLiking) return;

    setIsLiking(true);
    try {
      const response = await postService.toggleLike(String(id));
      if (response.success) {
        setLiked(response.is_liked);
        setCurrentLikeCount(response.likes_count);
        onLikeChanged?.(response.is_liked, response.likes_count);
      }
    } catch (error) {
      console.error('Like error:', error);
    } finally {
      setIsLiking(false);
    }
  };

  const handleDeleteClick = async (e: React.MouseEvent) => {
    e.stopPropagation();

    if (!window.confirm('Bạn có chắc chắn muốn xóa bài viết này?')) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await postService.deleteOwnPost(String(id));
      if (response.success) {
        alert('Đã xóa bài viết thành công!');
        onDeleted?.();
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
      setIsDeleting(false);
    }
  };

  const handleReportClick = (e: React.MouseEvent) => {
    e.stopPropagation();

    if (!isAuthenticated) {
      alert('Vui lòng đăng nhập để báo cáo bài viết');
      return;
    }

    setShowReportModal(true);
  };

  const handleReportSubmit = async () => {
    if (!reportReason.trim()) {
      alert('Vui lòng nhập lý do báo cáo');
      return;
    }

    setIsReporting(true);
    try {
      const response = await postService.reportPost(String(id), reportReason);
      if (response.success) {
        alert('Đã gửi báo cáo thành công!');
        setShowReportModal(false);
        setReportReason('');
      } else {
        alert('Không thể gửi báo cáo: ' + (response.message || 'Lỗi không xác định'));
      }
    } catch (error) {
      console.error('Report post error:', error);
      alert('Có lỗi xảy ra khi gửi báo cáo');
    } finally {
      setIsReporting(false);
    }
  };

  return (
    <>
      <div className="blog-card" onClick={handleCardClick} style={{ cursor: 'pointer' }}>
        {/* Header */}
        <div className="blog-card__header">
          <div className="blog-card__user">
            <img
              src={avatarSrc}
              alt={username}
              className={`blog-card__avatar ${authorId ? 'blog-card__avatar--clickable' : ''}`}
              onClick={handleUserClick}
            />
            <div className="blog-card__user-info">
              <span
                className={`blog-card__username ${authorId ? 'blog-card__username--clickable' : ''} ${isBanned ? 'blog-card__username--banned' : ''}`}
                onClick={handleUserClick}
              >
                {username} • {timeAgo}
              </span>
              <div className="blog-card__location">
                <Icons.Location className="blog-card__location-icon" />
                <span>{location}</span>
              </div>
            </div>
          </div>
          <div className="blog-card__header-actions">
            <div className="blog-card__rating">
              {rating.toFixed(1)}/5
            </div>
            {/* Delete button for owner, Report button for others */}
            {isOwner ? (
              <button
                className="blog-card__action-btn blog-card__action-btn--delete"
                onClick={handleDeleteClick}
                disabled={isDeleting}
                title="Xóa bài viết"
              >
                {isDeleting ? '...' : <Icons.Trash />}
              </button>
            ) : isAuthenticated ? (
              <button
                className="blog-card__action-btn blog-card__action-btn--report"
                onClick={handleReportClick}
                title="Báo cáo bài viết"
              >
                <Icons.Flag />
              </button>
            ) : null}
          </div>
        </div>

        {/* Images */}
        <div className="blog-card__images">
          <img src={imageSrc1} alt="Blog image 1" className="blog-card__image" />
          <img src={imageSrc2} alt="Blog image 2" className="blog-card__image" />
        </div>

        {/* Actions */}
        <div className="blog-card__actions">
          <button
            className={`blog-card__action blog-card__action--like ${liked ? 'blog-card__action--liked' : ''}`}
            onClick={handleLikeClick}
            disabled={isLiking}
          >
            <Icons.Heart className={`blog-card__icon blog-card__icon--love ${liked ? 'blog-card__icon--loved' : ''}`} />
            <span>{currentLikeCount}</span>
          </button>
          <div className="blog-card__action">
            <Icons.Comment className="blog-card__icon blog-card__icon--comment" />
            <span>{commentCount}</span>
          </div>
        </div>

        {/* Description */}
        <p className="blog-card__description">
          {description} <span className="blog-card__link">xem toàn bộ bài viết...</span>
        </p>
      </div>

      {/* Report Modal */}
      {showReportModal && (
        <div className="blog-card__modal-overlay" onClick={() => setShowReportModal(false)}>
          <div className="blog-card__modal" onClick={(e) => e.stopPropagation()}>
            <h3>Báo cáo bài viết</h3>
            <textarea
              placeholder="Nhập lý do báo cáo..."
              value={reportReason}
              onChange={(e) => setReportReason(e.target.value)}
              rows={4}
            />
            <div className="blog-card__modal-actions">
              <button onClick={() => setShowReportModal(false)} disabled={isReporting}>
                Hủy
              </button>
              <button onClick={handleReportSubmit} disabled={isReporting || !reportReason.trim()}>
                {isReporting ? 'Đang gửi...' : 'Gửi báo cáo'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BlogCard;
