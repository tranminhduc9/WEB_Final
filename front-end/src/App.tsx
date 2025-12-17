import Header from './components/Header';
import homePhoto from './assets/images/home_photo_1.png';
import FeaturedPlaces from './components/FeaturedPlaces'
import Footer from './components/Footer'
import PostCard from './components/PostCard'
import './App.css'

export default function App() {
  // Dữ liệu mẫu cho bài viết nổi bật
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
    }
  ];

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
        <FeaturedPlaces />

        {/* Bài viết nổi bật */}
        <section className="featured-posts-section">
          <h3 className="featured-posts-title">Bài viết nổi bật</h3>
          <p className="featured-posts-subtitle">Đố anh biết em đang nghĩ gì??</p>
          <div className="featured-posts-grid">
            {featuredPosts.map((post, index) => (
              <PostCard
                key={index}
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

        {/* Vì sao bạn nên chọn Hanoivivu? */}
        <section className="why-choose-section">
          <h2 className="why-choose-title">Vì sao bạn nên chọn Hanoivivu?</h2>
          <div className="why-choose-grid">
            <div className="why-choose-item">
              <div className="why-choose-icon">🍊</div>
              <h3 className="why-choose-item-title">Vô vàn lựa chọn</h3>
              <p className="why-choose-item-desc">Với hàng trăm ngàn điểm tham quan, khách sạn & nhiều hơn nữa, chắc chắn bạn sẽ tìm thấy niềm vui.</p>
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