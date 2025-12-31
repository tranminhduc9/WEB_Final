import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Icons } from '../../config/constants';
import { useAuthContext } from '../../contexts';
import { postService } from '../../services';
import '../../assets/styles/components/PostCard.css';

interface PostCardProps {
  id?: string | number;
  imageSrc: string;
  authorName: string;
  timeAgo: string;
  content: string;
  likeCount: number;
  commentCount: number;
  isLiked?: boolean; // Initial like state from parent
}

const PostCard: React.FC<PostCardProps> = ({
  id,
  imageSrc,
  authorName,
  timeAgo,
  content,
  likeCount: initialLikeCount,
  commentCount,
  isLiked: initialIsLiked = false,
}) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthContext();
  const [liked, setLiked] = useState(initialIsLiked);
  const [currentLikeCount, setCurrentLikeCount] = useState(initialLikeCount);
  const [isLiking, setIsLiking] = useState(false);

  const handleLikeClick = async (e: React.MouseEvent) => {
    e.preventDefault(); // Prevent navigation when clicking like
    e.stopPropagation();

    if (!isAuthenticated) {
      alert('Vui lòng đăng nhập để thích bài viết');
      navigate('/login');
      return;
    }

    if (!id || isLiking) return;

    setIsLiking(true);
    try {
      const response = await postService.toggleLike(String(id));
      if (response.success) {
        setLiked(response.is_liked);
        setCurrentLikeCount(response.likes_count);
      }
    } catch (error) {
      console.error('Like error:', error);
    } finally {
      setIsLiking(false);
    }
  };
  const cardContent = (
    <>
      {/* Ảnh bên trái */}
      <div className="post-card__image">
        <img src={imageSrc} alt={authorName} />
      </div>

      {/* Nội dung bên phải */}
      <div className="post-card__content">
        {/* Thông tin tác giả */}
        <div className="post-card__author">
          <span className="post-card__author-name">{authorName}</span>
          <span className="post-card__time">{timeAgo}</span>
        </div>

        {/* Nội dung bài viết */}
        <p className="post-card__text">{content}</p>

        {/* Like và Comment */}
        <div className="post-card__actions">
          <button
            className={`post-card__action post-card__action--like ${liked ? 'post-card__action--liked' : ''}`}
            onClick={handleLikeClick}
            disabled={isLiking}
          >
            <Icons.Heart className={`post-card__icon post-card__icon--love ${liked ? 'post-card__icon--loved' : ''}`} />
            <span className="post-card__count">{currentLikeCount}</span>
          </button>
          <div className="post-card__action">
            <Icons.Comment className="post-card__icon post-card__icon--comment" />
            <span className="post-card__count">{commentCount}</span>
          </div>
        </div>
      </div>
    </>
  );

  if (id) {
    return (
      <Link to={`/blog/${id}`} className="post-card post-card--link">
        {cardContent}
      </Link>
    );
  }

  return (
    <div className="post-card">
      {cardContent}
    </div>
  );
};

export default PostCard;
