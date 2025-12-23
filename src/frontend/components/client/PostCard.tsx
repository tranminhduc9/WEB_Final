import { Link } from 'react-router-dom';
import { Icons } from '../../config/constants';
import '../../assets/styles/components/PostCard.css';

interface PostCardProps {
  id?: string | number;
  imageSrc: string;
  authorName: string;
  timeAgo: string;
  content: string;
  likeCount: number;
  commentCount: number;
}

const PostCard: React.FC<PostCardProps> = ({
  id,
  imageSrc,
  authorName,
  timeAgo,
  content,
  likeCount,
  commentCount
}) => {
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
          <div className="post-card__action">
            <Icons.Heart className="post-card__icon post-card__icon--love" />
            <span className="post-card__count">{likeCount}</span>
          </div>
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
