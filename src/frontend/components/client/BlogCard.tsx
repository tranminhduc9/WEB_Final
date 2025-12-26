import React from 'react';
import { useNavigate } from 'react-router';
import { Icons } from '../../config/constants';
import '../../assets/styles/components/BlogCard.css';

interface BlogCardProps {
  id: string | number; // Support both string (API) and number
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
}

const BlogCard: React.FC<BlogCardProps> = ({
  id,
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
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/blog/${id}`);
  };

  return (
    <div className="blog-card" onClick={handleClick} style={{ cursor: 'pointer' }}>
      {/* Header */}
      <div className="blog-card__header">
        <div className="blog-card__user">
          <img src={avatarSrc} alt={username} className="blog-card__avatar" />
          <div className="blog-card__user-info">
            <span className="blog-card__username">{username} • {timeAgo}</span>
            <div className="blog-card__location">
              <Icons.Location className="blog-card__location-icon" />
              <span>{location}</span>
            </div>
          </div>
        </div>
        <div className="blog-card__rating">
          {rating.toFixed(1)}/5
        </div>
      </div>

      {/* Images */}
      <div className="blog-card__images">
        <img src={imageSrc1} alt="Blog image 1" className="blog-card__image" />
        <img src={imageSrc2} alt="Blog image 2" className="blog-card__image" />
      </div>

      {/* Actions */}
      <div className="blog-card__actions">
        <div className="blog-card__action">
          <Icons.Heart className="blog-card__icon blog-card__icon--love" />
          <span>{likeCount}</span>
        </div>
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
  );
};

export default BlogCard;

