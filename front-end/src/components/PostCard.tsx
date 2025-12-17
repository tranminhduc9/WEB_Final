import React from 'react';
import '../../css/PostCard.css';

interface PostCardProps {
  imageSrc: string;
  authorName: string;
  timeAgo: string;
  content: string;
  likeCount: number;
  commentCount: number;
}

const PostCard: React.FC<PostCardProps> = ({
  imageSrc,
  authorName,
  timeAgo,
  content,
  likeCount,
  commentCount
}) => {
  return (
    <div className="post-card">
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
          <div className="post-card__action">
            <span className="post-card__icon post-card__icon--love">❤️</span>
            <span className="post-card__count">{likeCount}</span>
          </div>
          <div className="post-card__action">
            <span className="post-card__icon post-card__icon--comment">💬</span>
            <span className="post-card__count">{commentCount}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostCard;

