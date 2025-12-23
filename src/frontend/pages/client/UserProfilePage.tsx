import React, { useState, useRef } from 'react';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCard from '../../components/common/LocationCard';
import PostCard from '../../components/client/PostCard';
import { useAuthContext } from '../../contexts';
import '../../assets/styles/pages/UserProfilePage.css';

const UserProfilePage: React.FC = () => {
  const { user, refreshUser } = useAuthContext();
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Dữ liệu mẫu địa điểm yêu thích
  const favoriteLocations = [
    {
      id: '1',
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      id: '2',
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      title: 'Hồ Gươm - Quận Hoàn Kiếm',
      address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
      tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
      rating: 4.5,
      reviewCount: '3.6K+'
    },
    {
      id: '3',
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
      authorName: user?.name || 'User',
      timeAgo: '36 phút trước',
      content: 'Thấy Hà Nội okee phết!!',
      likeCount: 36,
      commentCount: 36
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      authorName: user?.name || 'User',
      timeAgo: '36 phút trước',
      content: 'Thấy Hà Nội okee phết!!',
      likeCount: 36,
      commentCount: 36
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      authorName: user?.name || 'User',
      timeAgo: '36 phút trước',
      content: 'Thấy Hà Nội okee phết!!',
      likeCount: 36,
      commentCount: 36
    },
    {
      imageSrc: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      authorName: user?.name || 'User',
      timeAgo: '36 phút trước',
      content: 'Thấy Hà Nội okee phết!!',
      likeCount: 36,
      commentCount: 36
    }
  ];

  // Handle avatar click - open file picker
  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  // Handle avatar upload (demo mode - just update localStorage)
  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      alert('File quá lớn. Tối đa 5MB');
      return;
    }

    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert('Chỉ chấp nhận file ảnh (JPEG, PNG, GIF, WebP)');
      return;
    }

    setIsUploading(true);

    try {
      // Demo mode: Convert to base64 and save to localStorage
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;

        // Update user in localStorage
        if (user) {
          const updatedUser = { ...user, avatar: base64 };
          localStorage.setItem('user', JSON.stringify(updatedUser));

          // Dispatch event to update all components
          window.dispatchEvent(new CustomEvent('user:updated', { detail: updatedUser }));
        }

        setIsUploading(false);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload thất bại');
      setIsUploading(false);
    }
  };

  return (
    <>
      <Header />
      <div className="profile-page">
        {/* User Hero */}
        <section className="profile-hero">
          <div
            className="profile-avatar"
            onClick={handleAvatarClick}
            style={{ cursor: 'pointer', position: 'relative' }}
            title="Click để thay đổi avatar"
          >
            {user?.avatar ? (
              <img src={user.avatar} alt={user.name} />
            ) : (
              <div className="avatar-placeholder-large">
                {user?.name?.[0]?.toUpperCase() || 'U'}
              </div>
            )}
            {isUploading && (
              <div className="avatar-uploading">
                <span>Đang tải...</span>
              </div>
            )}
            <div className="avatar-overlay">
              <span>📷</span>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
              style={{ display: 'none' }}
            />
          </div>
          <div className="profile-info">
            <h1 className="profile-username">{user?.name || 'User'}</h1>
            <p className="profile-email">{user?.email}</p>
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
                id={loc.id}
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
