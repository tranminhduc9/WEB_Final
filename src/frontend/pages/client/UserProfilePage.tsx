import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCard from '../../components/common/LocationCard';
import PostCard from '../../components/client/PostCard';
import { useAuthContext } from '../../contexts';
import { userService } from '../../services';
import type { UserDetailResponse, PostDetail, PlaceCompact } from '../../types/models';
import '../../assets/styles/pages/UserProfilePage.css';

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

// Mock data for fallback
const mockFavoritePlaces: PlaceCompact[] = [
  {
    id: 1,
    name: 'Hồ Gươm - Quận Hoàn Kiếm',
    district_id: 1,
    place_type_id: 1,
    rating_average: 4.5,
    rating_count: 3600,
    price_min: 0,
    price_max: 0,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg'
  },
  {
    id: 2,
    name: 'Văn Miếu - Quốc Tử Giám',
    district_id: 2,
    place_type_id: 1,
    rating_average: 4.7,
    rating_count: 2800,
    price_min: 30000,
    price_max: 30000,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg'
  },
  {
    id: 3,
    name: 'Lăng Bác',
    district_id: 3,
    place_type_id: 1,
    rating_average: 4.8,
    rating_count: 5000,
    price_min: 0,
    price_max: 0,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg'
  }
];

const UserProfilePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user: currentUser, refreshUser } = useAuthContext();

  // Determine if viewing own profile
  const isOwnProfile = !id || (currentUser && String(currentUser.id) === id);

  // Profile states
  const [profile, setProfile] = useState<UserDetailResponse | null>(null);
  const [favoritePlaces, setFavoritePlaces] = useState<PlaceCompact[]>([]);
  const [userPosts, setUserPosts] = useState<PostDetail[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Avatar upload states
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Edit modal states
  const [showEditModal, setShowEditModal] = useState(false);
  const [editName, setEditName] = useState('');
  const [editBio, setEditBio] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  // Mock profile for fallback
  const mockProfile: UserDetailResponse = {
    id: parseInt(id || '1'),
    email: 'user@example.com',
    full_name: currentUser?.name || 'Người dùng',
    avatar_url: currentUser?.avatar || null,
    bio: 'Yêu thích du lịch và khám phá Hà Nội',
    role_id: 3,
    reputation_score: 256,
    recent_posts: []
  };

  // Fetch profile data
  const fetchProfile = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      let profileData: UserDetailResponse;

      if (isOwnProfile) {
        // Fetch own profile
        profileData = await userService.getProfile();
      } else {
        // Fetch other user's profile
        profileData = await userService.getUserProfile(id!);
      }

      setProfile(profileData);

      // Set user's posts from profile response
      if (profileData.recent_posts) {
        setUserPosts(profileData.recent_posts);
      }

      // Initialize edit form values
      if (isOwnProfile) {
        setEditName(profileData.full_name || '');
        setEditBio(profileData.bio || '');
      }

      // TODO: Fetch favorite places when API is available
      setFavoritePlaces(mockFavoritePlaces);

    } catch (err) {
      console.error('Error fetching profile, using mock data:', err);
      // Fallback to mock data
      setProfile(mockProfile);
      setFavoritePlaces(mockFavoritePlaces);
      setEditName(mockProfile.full_name || '');
      setEditBio(mockProfile.bio || '');
    } finally {
      setIsLoading(false);
    }
  }, [id, isOwnProfile, currentUser]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  // Handle avatar click - open file picker (only for own profile)
  const handleAvatarClick = () => {
    if (isOwnProfile) {
      fileInputRef.current?.click();
    }
  };

  // Handle avatar upload
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
      const avatarUrl = await userService.uploadAvatar(file);
      setProfile(prev => prev ? { ...prev, avatar_url: avatarUrl } : null);
      refreshUser();
    } catch (err) {
      console.error('Upload failed:', err);
      // Fallback: Convert to base64 and save to localStorage
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        if (currentUser) {
          const updatedUser = { ...currentUser, avatar: base64 };
          localStorage.setItem('user', JSON.stringify(updatedUser));
          window.dispatchEvent(new CustomEvent('user:updated', { detail: updatedUser }));
          setProfile(prev => prev ? { ...prev, avatar_url: base64 } : null);
        }
      };
      reader.readAsDataURL(file);
    } finally {
      setIsUploading(false);
    }
  };

  // Handle update profile
  const handleUpdateProfile = async () => {
    if (!editName.trim()) {
      alert('Vui lòng nhập họ tên');
      return;
    }

    setIsUpdating(true);
    try {
      const updated = await userService.updateProfile({
        full_name: editName.trim(),
        bio: editBio.trim()
      });
      setProfile(prev => prev ? { ...prev, ...updated } : null);
      setShowEditModal(false);
      refreshUser();
    } catch (err) {
      console.error('Update failed:', err);
      // Fallback: Update localStorage
      if (currentUser) {
        const updatedUser = { ...currentUser, name: editName.trim() };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        window.dispatchEvent(new CustomEvent('user:updated', { detail: updatedUser }));
        setProfile(prev => prev ? { ...prev, full_name: editName.trim(), bio: editBio.trim() } : null);
        setShowEditModal(false);
      }
    } finally {
      setIsUpdating(false);
    }
  };

  // Calculate reputation score
  const getReputationDisplay = () => {
    if (profile?.reputation_score) {
      return `Điểm danh tiếng: ${profile.reputation_score}`;
    }
    const totalLikes = userPosts.reduce((sum, p) => sum + (p.likes_count || 0), 0);
    const totalComments = userPosts.reduce((sum, p) => sum + (p.comments_count || 0), 0);
    const postCount = userPosts.length || 1;
    return `Điểm danh tiếng: (${totalLikes} + ${totalComments}) / ${postCount} bài viết`;
  };

  // Loading state
  if (isLoading) {
    return (
      <>
        <Header />
        <div className="profile-page profile-page--loading">
          <div className="profile-loading">
            <div className="loading-spinner"></div>
            <p>Đang tải thông tin...</p>
          </div>
        </div>
        <Footer />
      </>
    );
  }

  // Error state
  if (error && !profile) {
    return (
      <>
        <Header />
        <div className="profile-page profile-page--error">
          <div className="profile-error">
            <h2>😕 {error}</h2>
            <Link to="/" className="profile-back-link">← Về trang chủ</Link>
          </div>
        </div>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="profile-page">
        {/* User Hero */}
        <section className="profile-hero">
          <div
            className={`profile-avatar ${isOwnProfile ? 'profile-avatar--editable' : ''}`}
            onClick={handleAvatarClick}
            title={isOwnProfile ? 'Click để thay đổi avatar' : undefined}
          >
            {profile?.avatar_url ? (
              <img src={profile.avatar_url} alt={profile.full_name} />
            ) : (
              <div className="avatar-placeholder-large">
                {profile?.full_name?.[0]?.toUpperCase() || 'U'}
              </div>
            )}
            {isUploading && (
              <div className="avatar-uploading">
                <span>Đang tải...</span>
              </div>
            )}
            {isOwnProfile && (
              <>
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
              </>
            )}
          </div>
          <div className="profile-info">
            <h1 className="profile-username">{profile?.full_name || 'Người dùng'}</h1>
            {profile?.bio && (
              <p className="profile-bio">{profile.bio}</p>
            )}
            <p className="profile-metric">{getReputationDisplay()}</p>
          </div>

          {/* Edit button - only for own profile */}
          {isOwnProfile && (
            <button
              className="profile-edit-btn"
              onClick={() => setShowEditModal(true)}
            >
              <span className="profile-edit-icon">⚙️</span>
              Chỉnh sửa thông tin cá nhân
            </button>
          )}
        </section>

        {/* Địa điểm yêu thích */}
        <section className="profile-section">
          <h2 className="profile-section__title">
            Địa điểm yêu thích <span className="profile-icon">📍</span>
          </h2>
          {favoritePlaces.length > 0 ? (
            <div className="profile-locations-scroll">
              {favoritePlaces.map((place) => (
                <LocationCard
                  key={place.id}
                  id={String(place.id)}
                  imageSrc={place.main_image_url || ''}
                  title={place.name}
                  address={`Quận ${place.district_id}`}
                  priceMin={place.price_min}
                  priceMax={place.price_max}
                  rating={place.rating_average}
                  reviewCount={place.rating_count ? `${(place.rating_count / 1000).toFixed(1)}K+` : '0'}
                />
              ))}
            </div>
          ) : (
            <p className="profile-empty">Chưa có địa điểm yêu thích nào</p>
          )}
        </section>

        {/* Bài viết nổi bật */}
        <section className="profile-section">
          <h2 className="profile-section__title">
            Bài viết nổi bật <span className="profile-icon">💬</span>
          </h2>
          {userPosts.length > 0 ? (
            <div className="profile-posts-grid">
              {userPosts.map((post) => (
                <Link key={post._id} to={`/blog/${post._id}`} style={{ textDecoration: 'none' }}>
                  <PostCard
                    imageSrc={post.images?.[0] || 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg'}
                    authorName={post.author?.full_name || profile?.full_name || 'User'}
                    timeAgo={formatTimeAgo(post.created_at)}
                    content={post.content?.slice(0, 100) || ''}
                    likeCount={post.likes_count || 0}
                    commentCount={post.comments_count || 0}
                  />
                </Link>
              ))}
            </div>
          ) : (
            <p className="profile-empty">Chưa có bài viết nào</p>
          )}
        </section>
      </div>

      {/* Edit Profile Modal */}
      {showEditModal && (
        <div
          className="profile-edit-modal-overlay"
          onClick={() => setShowEditModal(false)}
        >
          <div
            className="profile-edit-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>Chỉnh sửa thông tin cá nhân</h3>

            <div className="profile-edit-field">
              <label>Họ tên</label>
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                placeholder="Nhập họ tên..."
                disabled={isUpdating}
              />
            </div>

            <div className="profile-edit-field">
              <label>Giới thiệu</label>
              <textarea
                value={editBio}
                onChange={(e) => setEditBio(e.target.value)}
                placeholder="Giới thiệu về bản thân..."
                disabled={isUpdating}
                rows={3}
              />
            </div>

            <div className="profile-edit-actions">
              <button
                onClick={() => setShowEditModal(false)}
                disabled={isUpdating}
              >
                Hủy
              </button>
              <button
                onClick={handleUpdateProfile}
                disabled={isUpdating || !editName.trim()}
              >
                {isUpdating ? 'Đang lưu...' : 'Lưu thay đổi'}
              </button>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </>
  );
};

export default UserProfilePage;
