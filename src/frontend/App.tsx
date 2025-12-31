import { useState, useEffect } from 'react';
import Header from './components/client/Header';
import HeroCarousel from './components/client/HeroCarousel';
import LocationCard from './components/common/LocationCard';
import Footer from './components/client/Footer'
import PostCard from './components/client/PostCard'
import { placeService, postService } from './services';
import type { PlaceCompact, PostDetail } from './types/models';
import './App.css'


// Helper: Format time ago
function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 60) return `${diffMins} phút trước`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} giờ trước`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} ngày trước`;
}

export default function App() {
  const [places, setPlaces] = useState<PlaceCompact[]>([]);
  const [posts, setPosts] = useState<PostDetail[]>([]);
  const [isLoadingPlaces, setIsLoadingPlaces] = useState(true);
  const [isLoadingPosts, setIsLoadingPosts] = useState(true);

  // Fetch places from API
  useEffect(() => {
    const fetchPlaces = async () => {
      try {
        const response = await placeService.getPlaces({ page: 1, limit: 5 });
        if (response.success && response.data) {
          setPlaces(response.data);
        }
      } catch (error) {
        console.warn('Failed to fetch places:', error);
      } finally {
        setIsLoadingPlaces(false);
      }
    };

    fetchPlaces();
  }, []);

  // Fetch posts from API
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await postService.getPosts(1, 6);
        if (response.success && response.data) {
          setPosts(response.data);
        }
      } catch (error) {
        console.warn('Failed to fetch posts:', error);
      } finally {
        setIsLoadingPosts(false);
      }
    };

    fetchPosts();
  }, []);

  return (
    <div className="app-container">
      <Header />
      <main className="app-main">
        {/* Hero Carousel với hình ảnh slideshow */}
        <HeroCarousel />

        {/* Các địa điểm nổi bật */}
        <section className="featured-places-section">
          <h3 className="featured-places-title">Các địa điểm nổi bật</h3>
          <p className="featured-places-subtitle">Cùng khám phá các địa điểm, di tích để hiểu thêm về Hà Nội nghìn năm văn hiến nhé!</p>

          {isLoadingPlaces ? (
            <div className="scroll-container">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="place-card skeleton" style={{ minWidth: 280, height: 320 }} />
              ))}
            </div>
          ) : (
            <div className="scroll-container">
              {places.map((place) => (
                <LocationCard
                  key={place.id}
                  id={String(place.id)}
                  imageSrc={place.main_image_url || ''}
                  title={place.name}
                  address={place.address || place.district_name || 'Hà Nội'}
                  priceMin={place.price_min}
                  priceMax={place.price_max}
                  rating={place.rating_average}
                  reviewCount={place.rating_count || 0}
                />
              ))}
            </div>
          )}
        </section>

        {/* Bài viết nổi bật */}
        <section className="featured-posts-section">
          <h3 className="featured-posts-title">Bài viết nổi bật</h3>
          <p className="featured-posts-subtitle">Đố anh biết em đang nghĩ gì??</p>

          {isLoadingPosts ? (
            <div className="featured-posts-grid">
              {[1, 2].map((i) => (
                <div key={i} className="post-card skeleton" style={{ height: 200 }} />
              ))}
            </div>
          ) : (
            <div className="featured-posts-grid">
              {posts.map((post) => (
                <PostCard
                  key={post._id}
                  id={post._id}
                  imageSrc={post.images?.[0] || 'https://via.placeholder.com/300'}
                  authorName={post.author?.full_name || 'Ẩn danh'}
                  timeAgo={post.created_at ? formatTimeAgo(post.created_at) : 'Vừa xong'}
                  content={post.content}
                  likeCount={post.likes_count}
                  commentCount={post.comments_count}
                />
              ))}
            </div>
          )}
        </section>

        {/* Vì sao bạn nên chọn Hanoivivu? */}
        <section className="why-choose-section">
          <h2 className="why-choose-title">Vì sao bạn nên chọn Hanoivivu?</h2>
          <div className="why-choose-grid">
            <div className="why-choose-item">
              <div className="why-choose-icon">🍊</div>
              <h3 className="why-choose-item-title">Vô vàn lựa chọn</h3>
              <p className="why-choose-item-desc">Với hàng trăm ngàn điểm tham quan, khách sạn &amp; nhiều hơn nữa, chắc chắn bạn sẽ tìm thấy niềm vui.</p>
            </div>
            <div className="why-choose-item">
              <div className="why-choose-icon">🍊</div>
              <h3 className="why-choose-item-title">Chơi vui giá tốt</h3>
              <p className="why-choose-item-desc">Trải nghiệm chất lượng với giá tốt. Với chatbot thông minh giúp tối ưu kinh phí cho bạn</p>
            </div>
            <div className="why-choose-item">
              <div className="why-choose-icon">🍊</div>
              <h3 className="why-choose-item-title">Cộng đồng vui vẻ</h3>
              <p className="why-choose-item-desc">Giao lưu chia sẻ trải nghiệm cuộc sống giúp cuộc đời thêm vui</p>
            </div>
            <div className="why-choose-item">
              <div className="why-choose-icon">🍊</div>
              <h3 className="why-choose-item-title">Đáng tin cậy</h3>
              <p className="why-choose-item-desc">Không seeder, không book bài (trừ khi được gài)</p>
            </div>
          </div>
        </section>

        <Footer />
      </main>
    </div>
  );
}