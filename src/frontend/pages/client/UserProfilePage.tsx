import React from 'react';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCard from '../../components/common/LocationCard';
import PostCard from '../../components/client/PostCard';
import '../../assets/styles/pages/UserProfilePage.css';

const UserProfilePage: React.FC = () => {
  // Dữ liệu mẫu địa điểm yêu thích
  const favoriteLocations = [
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    }
  ];

  // Dữ liệu mẫu bài viết nổi bật
  const featuredPosts = [
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      authorName: 'Trần Minh Đức',
      timeAgo: '36 phút trước',
      content: 'Thấy Hà Nội okee phết!!',
      likeCount: 36,
      commentCount: 36
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      authorName: 'Trần Minh Đức',
      timeAgo: '36 phút trước',
      content: 'Thấy Hà Nội okee phết!!',
      likeCount: 36,
      commentCount: 36
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      authorName: 'Trần Minh Đức',
      timeAgo: '36 phút trước',
      content: 'Thấy Hà Nội okee phết!!',
      likeCount: 36,
      commentCount: 36
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      authorName: 'Trần Minh Đức',
      timeAgo: '36 phút trước',
      content: 'Thấy Hà Nội okee phết!!',
      likeCount: 36,
      commentCount: 36
    }
  ];

  return (
    <>
      <Header />
      <div className="profile-page">
        {/* User Hero */}
        <section className="profile-hero">
          <div className="profile-avatar">
            <img src="https://i.pravatar.cc/200" alt="User avatar" />
          </div>
          <div className="profile-info">
            <h1 className="profile-username">Username</h1>
            <p className="profile-metric">Độ uy tín: (Tổng Like + cmt) / số bài viết</p>
          </div>
          <button className="profile-edit-btn">
            <span className="profile-edit-icon">⚙️</span>
            Chỉnh sửa thông tin cá nhân
          </button>
        </section>

        {/* Địa điểm yêu thích */}
        <section className="profile-section">
          <h2 className="profile-section__title">
            Địa điểm yêu thích <span className="profile-icon">📍</span>
          </h2>
          <div className="profile-locations-scroll">
            {favoriteLocations.map((loc, idx) => (
              <LocationCard
                key={`fav-${idx}`}
                imageSrc={loc.imageSrc}
                title={loc.title}
                address={loc.address}
                tags={loc.tags}
                rating={loc.rating}
                reviewCount={loc.reviewCount}
              />
            ))}
          </div>
        </section>

        {/* Bài viết nổi bật */}
        <section className="profile-section">
          <h2 className="profile-section__title">
            Bài viết nổi bật <span className="profile-icon">💬</span>
          </h2>
          <div className="profile-posts-grid">
            {featuredPosts.map((post, idx) => (
              <PostCard
                key={`post-${idx}`}
                imageSrc={post.imageSrc}
                authorName={post.authorName}
                timeAgo={post.timeAgo}
                content={post.content}
                likeCount={post.likeCount}
                commentCount={post.commentCount}
              />
            ))}
          </div>
        </section>
      </div>
      <Footer />
    </>
  );
};

export default UserProfilePage;
