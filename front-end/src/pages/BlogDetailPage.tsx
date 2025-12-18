import React, { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Icons } from '../constants';
import '../../css/BlogDetailPage.css';

// Placeholder image URL
const placeholderImage = 'https://images.unsplash.com/photo-1599708153386-62bf3f035e78?w=600&h=400&fit=crop';

interface Comment {
  id: number;
  avatar: string;
  username: string;
  content: string;
  timeAgo: string;
  replies?: Comment[];
}

const BlogDetailPage: React.FC = () => {
  const [comments] = useState<Comment[]>([
    {
      id: 1,
      avatar: '/duckk.jpg',
      username: 'Entekie',
      content: 'Em có tin là anh tung địa chỉ nhà em lên mạng không? Anh là anh có hết thông tin của em rồi đấy nhé!',
      timeAgo: '3 giờ trước',
      replies: [
        {
          id: 2,
          avatar: '/duckk.jpg',
          username: 'Entekie',
          content: 'Em đừng có chối!!',
          timeAgo: '2 giờ trước',
        },
      ],
    },
    {
      id: 3,
      avatar: '/duckk.jpg',
      username: 'Entekie',
      content: 'Em có tin là anh tung địa chỉ nhà em lên mạng không? Anh là anh có hết thông tin của em rồi đấy nhé!',
      timeAgo: '3 giờ trước',
    },
    {
      id: 4,
      avatar: '/duckk.jpg',
      username: 'Entekie',
      content: 'Em có tin là anh tung địa chỉ nhà em lên mạng không? Anh là anh có hết thông tin của em rồi đấy nhé!',
      timeAgo: '3 giờ trước',
    },
  ]);

  // Blog post data
  const post = {
    avatar: '/duckk.jpg',
    username: 'user_name',
    timeAgo: '20 giờ',
    location: 'Hồ Gươm - Quận Hoàn Kiếm',
    rating: 3.6,
    image1: placeholderImage,
    image2: placeholderImage,
    likeCount: 36,
    commentCount: 36,
    description: `Hồ Hoàn Kiếm (Hán-Nôm: 湖還劍) còn được gọi là Hồ Gươm là một hồ nước ngọt tự nhiên nằm ở phường Hoàn Kiếm, trung tâm thành phố Hà Nội. Hồ có diện tích khoảng 12 ha[2]. Trước kia, hồ còn có các tên gọi là hồ Lục Thủy (vì nước có màu xanh quanh năm), hồ Thủy Quân (dùng để duyệt thủy binh) Hồ Hoàn Kiếm (Hán-Nôm: 湖還劍) còn được gọi là Hồ Gươm là một hồ nước ngọt tự nhiên nằm ở phường Hoàn Kiếm, trung tâm thành phố Hà Nội. Hồ có diện tích khoảng 12 ha[2]. Trước kia, hồ còn có các tên gọi là hồ Lục Thủy (vì nước có màu xanh quanh năm), hồ Thủy Quân (dùng để duyệt thủy binh)`,
  };

  return (
    <>
      <Header />
      <div className="blog-detail-page">
        {/* Post Section */}
        <section className="blog-detail__post">
          {/* Rating Badge */}
          <div className="blog-detail__rating-badge">
            {post.rating}/5
          </div>

          {/* Report Button */}
          <div className="blog-detail__report">
            <span>Báo cáo</span>
            <Icons.Flag className="blog-detail__report-icon" />
          </div>

          {/* User Info */}
          <div className="blog-detail__user-info">
            <img 
              src={post.avatar} 
              alt={post.username} 
              className="blog-detail__avatar"
            />
            <span className="blog-detail__username">
              {post.username} • {post.timeAgo}
            </span>
          </div>

          {/* Location */}
          <div className="blog-detail__location">
            <Icons.Location className="blog-detail__location-icon" />
            <span>{post.location}</span>
          </div>

          {/* Images */}
          <div className="blog-detail__images">
            <img src={post.image1} alt="Post 1" className="blog-detail__image" />
            <img src={post.image2} alt="Post 2" className="blog-detail__image" />
          </div>

          {/* Actions */}
          <div className="blog-detail__actions">
            <div className="blog-detail__action">
              <Icons.Heart className="blog-detail__action-icon" />
              <span>{post.likeCount}</span>
            </div>
            <div className="blog-detail__action">
              <Icons.Comment className="blog-detail__action-icon" />
              <span>{post.commentCount}</span>
            </div>
          </div>

          {/* Description */}
          <p className="blog-detail__description">{post.description}</p>
        </section>

        {/* Comments Section */}
        <section className="blog-detail__comments">
          <h2 className="blog-detail__comments-title">Bình luận</h2>

          <div className="blog-detail__comments-list">
            {comments.map((comment) => (
              <div key={comment.id} className="blog-detail__comment-wrapper">
                {/* Main Comment */}
                <div className="blog-detail__comment">
                  <img 
                    src={comment.avatar} 
                    alt={comment.username} 
                    className="blog-detail__comment-avatar"
                  />
                  <div className="blog-detail__comment-content">
                    <div className="blog-detail__comment-header">
                      <span className="blog-detail__comment-username">{comment.username}</span>
                      <p className="blog-detail__comment-text">{comment.content}</p>
                    </div>
                    <div className="blog-detail__comment-footer">
                      <span className="blog-detail__comment-time">{comment.timeAgo}</span>
                      <button className="blog-detail__comment-reply">
                        <Icons.Comment className="blog-detail__comment-icon" />
                        <span>Trả lời</span>
                      </button>
                      <button className="blog-detail__comment-report">
                        <Icons.Flag className="blog-detail__comment-icon" />
                        <span>Báo cáo</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Replies */}
                {comment.replies && comment.replies.map((reply) => (
                  <div key={reply.id} className="blog-detail__reply">
                    <img 
                      src={reply.avatar} 
                      alt={reply.username} 
                      className="blog-detail__comment-avatar"
                    />
                    <div className="blog-detail__comment-content">
                      <div className="blog-detail__comment-header">
                        <span className="blog-detail__comment-username">{reply.username}</span>
                        <p className="blog-detail__comment-text">{reply.content}</p>
                      </div>
                      <div className="blog-detail__comment-footer">
                        <span className="blog-detail__comment-time">{reply.timeAgo}</span>
                        <button className="blog-detail__comment-report">
                          <Icons.Flag className="blog-detail__comment-icon" />
                          <span>Báo cáo</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>

          <button className="blog-detail__load-more">
            Tải thêm bình luận...
          </button>
        </section>
      </div>
      <Footer />
    </>
  );
};

export default BlogDetailPage;

