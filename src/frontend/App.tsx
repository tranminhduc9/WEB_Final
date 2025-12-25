import { useState, useEffect } from 'react';
import Header from './components/client/Header';
import homePhoto from './assets/images/home_photo_1.png';
import LocationCard from './components/common/LocationCard';
import Footer from './components/client/Footer'
import PostCard from './components/client/PostCard'
import { placeService, postService } from './services';
import type { PlaceCompact, PostDetail } from './types/models';
import './App.css'

// ============================
// MOCK DATA (Fallback khi API fail)
// ============================
const MOCK_LOCATIONS = [
  {
    id: 1,
    name: 'Hồ Gươm - Quận Hoàn Kiếm',
    district_id: 1,
    place_type_id: 1,
    rating_average: 4.5,
    price_min: 0,
    price_max: 0,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
    address: 'Phường Hoàn Kiếm - Thành phố Hà Nội',
    tags: ['Phố đi bộ', 'Du lịch - Văn hóa'],
  },
  {
    id: 2,
    name: 'Văn Miếu - Quốc Tử Giám',
    district_id: 2,
    place_type_id: 1,
    rating_average: 4.7,
    price_min: 30000,
    price_max: 30000,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
    address: 'Quốc Tử Giám, Đống Đa, Hà Nội',
    tags: ['Di tích lịch sử', 'Du lịch - Văn hóa'],
  },
  {
    id: 3,
    name: 'Lăng Bác',
    district_id: 3,
    place_type_id: 1,
    rating_average: 4.8,
    price_min: 0,
    price_max: 0,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
    address: 'Quảng trường Ba Đình, Hà Nội',
    tags: ['Di tích lịch sử', 'Văn hóa'],
  },
  {
    id: 4,
    name: 'Hoàng Thành Thăng Long',
    district_id: 3,
    place_type_id: 1,
    rating_average: 4.6,
    price_min: 30000,
    price_max: 50000,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
    address: 'Ba Đình, Hà Nội',
    tags: ['Di sản UNESCO', 'Lịch sử'],
  },
  {
    id: 5,
    name: 'Phố cổ Hà Nội',
    district_id: 1,
    place_type_id: 2,
    rating_average: 4.4,
    price_min: 0,
    price_max: 0,
    main_image_url: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
    address: 'Hoàn Kiếm, Hà Nội',
    tags: ['Phố đi bộ', 'Ẩm thực'],
  },
];

const MOCK_POSTS = [
  {
    _id: '1',
    title: 'Khám phá Hà Nội',
    content: 'Thấy Hà Nội okee phết!!',
    author: { id: 1, full_name: 'Trần Minh Đức', avatar_url: '', role_id: 1 },
    images: ['https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg'],
    likes_count: 36,
    comments_count: 36,
    is_liked: false,
    created_at: new Date(Date.now() - 36 * 60 * 1000).toISOString(),
  },
  {
    _id: '2',
    title: 'Ẩm thực đường phố',
    content: 'Phở Hà Nội ngon lắm các bạn ơi!',
    author: { id: 2, full_name: 'Nguyễn Văn A', avatar_url: '', role_id: 1 },
    images: ['https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg'],
    likes_count: 42,
    comments_count: 15,
    is_liked: false,
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
];

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

  // Fetch places từ API, fallback to mock data
  useEffect(() => {
    const fetchPlaces = async () => {
      try {
        const response = await placeService.getPlaces({ page: 1, limit: 5 });
        if (response.success && response.data.length > 0) {
          setPlaces(response.data);
        } else {
          // API trả về empty, dùng mock
          setPlaces(MOCK_LOCATIONS as PlaceCompact[]);
        }
      } catch (error) {
        console.warn('Failed to fetch places, using mock data:', error);
        setPlaces(MOCK_LOCATIONS as PlaceCompact[]);
      } finally {
        setIsLoadingPlaces(false);
      }
    };

    fetchPlaces();
  }, []);

  // Fetch posts từ API, fallback to mock data
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await postService.getPosts(1, 5);
        if (response.success && response.data.length > 0) {
          setPosts(response.data);
        } else {
          // API trả về empty, dùng mock
          setPosts(MOCK_POSTS as PostDetail[]);
        }
      } catch (error) {
        console.warn('Failed to fetch posts, using mock data:', error);
        setPosts(MOCK_POSTS as PostDetail[]);
      } finally {
        setIsLoadingPosts(false);
      }
    };

    fetchPosts();
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        {/* Hero Section với hình ảnh */}
        <section className="relative h-96 bg-gray-100 w-screen -mx-4">
          <img
            src={homePhoto}
            alt="Du lịch Hà Nội"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center">
          </div>
        </section>

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
                  imageSrc={place.main_image_url}
                  title={place.name}
                  address={(place as typeof MOCK_LOCATIONS[0]).address || 'Hà Nội'}
                  tags={(place as typeof MOCK_LOCATIONS[0]).tags || ['Du lịch']}
                  rating={place.rating_average}
                  reviewCount="0"
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