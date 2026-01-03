import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCard from '../../components/common/LocationCard';
import PostCard from '../../components/client/PostCard';
import { Icons } from '../../config/constants';
import { useAuthContext } from '../../contexts';
import { userService, authService } from '../../services';
import { formatTimeAgo } from '../../utils/timeUtils';
import type { UserDetailResponse, PostDetail, PlaceCompact } from '../../types/models';
import '../../assets/styles/pages/UserProfilePage.css';


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

  // Enhanced modal states - tabs and password
  const [activeTab, setActiveTab] = useState<'info' | 'password'>('info');
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);



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

      // Set favorite places from API response
      if (profileData.recent_favorites) {
        setFavoritePlaces(profileData.recent_favorites);
      }

    } catch (err) {
      console.error('Error fetching profile:', err);
      setError('Không thể tải thông tin người dùng');
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
    // Calculate from posts: (totalLikes + totalComments) / postCount
    const totalLikes = userPosts.reduce((sum, p) => sum + (p.likes_count || 0), 0);
    const totalComments = userPosts.reduce((sum, p) => sum + (p.comments_count || 0), 0);
    const postCount = userPosts.length || 1;
    const calculatedScore = Math.round((totalLikes + totalComments) / postCount);
    return `Điểm danh tiếng: ${calculatedScore}`;
  };

  // Reset modal state on close
  const resetEditModal = () => {
    setShowEditModal(false);
    setActiveTab('info');
    setOldPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setPasswordError(null);
    setPasswordSuccess(false);
  };

  // Handle change password
  const handleChangePassword = async () => {
    setPasswordError(null);
    setPasswordSuccess(false);

    // Validation
    if (!oldPassword.trim()) {
      setPasswordError('Vui lòng nhập mật khẩu cũ');
      return;
    }
    if (!newPassword.trim()) {
      setPasswordError('Vui lòng nhập mật khẩu mới');
      return;
    }
    if (newPassword.length < 6) {
      setPasswordError('Mật khẩu mới phải có ít nhất 6 ký tự');
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('Xác nhận mật khẩu không khớp');
      return;
    }

    setIsUpdating(true);
    try {
      await authService.changePassword({
        current_password: oldPassword,
        new_password: newPassword
      });
      setPasswordSuccess(true);
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
      // Show success then close after delay
      setTimeout(() => {
        resetEditModal();
      }, 1500);
    } catch (err) {
      console.error('Change password failed:', err);
      setPasswordError('Đổi mật khẩu thất bại. Vui lòng kiểm tra lại mật khẩu cũ.');
    } finally {
      setIsUpdating(false);
    }
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
              <Icons.Settings className="profile-edit-icon" />
              Chỉnh sửa thông tin cá nhân
            </button>
          )}
        </section>

        {/* Địa điểm yêu thích */}
        <section className="profile-section">
          <div className="profile-section__header">
            <h2 className="profile-section__title">
              Địa điểm yêu thích <Icons.Location className="profile-icon" />
            </h2>
            {favoritePlaces.length > 0 && (
              <Link
                to={isOwnProfile ? "/places/favourite" : `/places/favourite/${id}`}
                className="profile-section__view-all"
              >
                Xem tất cả →
              </Link>
            )}
          </div>
          {favoritePlaces.length > 0 ? (
            <div className="profile-locations-scroll">
              {favoritePlaces.map((place) => (
                <LocationCard
                  key={place.id}
                  id={String(place.id)}
                  imageSrc={place.main_image_url || ''}
                  title={place.name}
                  address={place.address || place.district_name || `Quận ${place.district_id}`}
                  priceMin={place.price_min}
                  priceMax={place.price_max}
                  rating={place.rating_average}
                  reviewCount={place.rating_count || 0}
                />
              ))}
            </div>
          ) : (
            <p className="profile-empty">Chưa có địa điểm yêu thích nào</p>
          )}
        </section>

        {/* Bài viết nổi bật */}
        <section className="profile-section">
          <div className="profile-section__header">
            <h2 className="profile-section__title">
              Bài viết nổi bật <Icons.Comment className="profile-icon" />
            </h2>
            {userPosts.length > 0 && (
              <Link
                to={isOwnProfile ? "/posts/user" : `/posts/user/${id}`}
                className="profile-section__view-all"
              >
                Xem tất cả →
              </Link>
            )}
          </div>
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

      {/* Edit Profile Modal - Enhanced with tabs */}
      {showEditModal && (
        <div
          className="profile-edit-modal-overlay"
          onClick={resetEditModal}
        >
          <div
            className="profile-edit-modal profile-edit-modal--enhanced"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button className="profile-edit-close" onClick={resetEditModal}>
              ×
            </button>

            {/* Modal Content with Tabs */}
            <div className="profile-edit-layout">
              {/* Tab Navigation - Left Side */}
              <div className="profile-edit-tabs">
                <button
                  className={`profile-edit-tab ${activeTab === 'info' ? 'profile-edit-tab--active' : ''}`}
                  onClick={() => setActiveTab('info')}
                >
                  Thông tin cá nhân
                </button>
                <button
                  className={`profile-edit-tab ${activeTab === 'password' ? 'profile-edit-tab--active' : ''}`}
                  onClick={() => setActiveTab('password')}
                >
                  Mật khẩu
                </button>
              </div>

              {/* Vertical Divider */}
              <div className="profile-edit-divider"></div>

              {/* Tab Content - Right Side */}
              <div className="profile-edit-content">
                {activeTab === 'info' ? (
                  <>
                    <div className="profile-edit-field">
                      <label>Tên người dùng</label>
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        placeholder="Nhập tên người dùng..."
                        disabled={isUpdating}
                      />
                    </div>

                    <div className="profile-edit-field">
                      <label>Sửa giới thiệu</label>
                      <input
                        type="text"
                        value={editBio}
                        onChange={(e) => setEditBio(e.target.value)}
                        placeholder="Giới thiệu về bản thân..."
                        disabled={isUpdating}
                      />
                    </div>

                    <div className="profile-edit-actions">
                      <button
                        className="profile-edit-submit"
                        onClick={handleUpdateProfile}
                        disabled={isUpdating || !editName.trim()}
                      >
                        {isUpdating ? 'Đang lưu...' : 'Xác nhận'}
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    {passwordError && (
                      <div className="profile-edit-error">{passwordError}</div>
                    )}
                    {passwordSuccess && (
                      <div className="profile-edit-success">Đổi mật khẩu thành công!</div>
                    )}

                    <div className="profile-edit-field">
                      <label>Mật khẩu cũ</label>
                      <input
                        type="password"
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                        placeholder="Nhập mật khẩu cũ..."
                        disabled={isUpdating}
                      />
                    </div>

                    <div className="profile-edit-field">
                      <label>Mật khẩu mới</label>
                      <input
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="Nhập mật khẩu mới..."
                        disabled={isUpdating}
                      />
                    </div>

                    <div className="profile-edit-field">
                      <label>Xác nhận mật khẩu</label>
                      <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Xác nhận mật khẩu mới..."
                        disabled={isUpdating}
                      />
                    </div>

                    <div className="profile-edit-actions">
                      <button
                        className="profile-edit-submit"
                        onClick={handleChangePassword}
                        disabled={isUpdating || !oldPassword || !newPassword || !confirmPassword}
                      >
                        {isUpdating ? 'Đang xử lý...' : 'Xác nhận'}
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </>
  );
};

export default UserProfilePage;
