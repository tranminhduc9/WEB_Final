import React, { useState } from 'react';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import BlogCard from '../../components/client/BlogCard';
import CreatePostModal from '../../components/client/CreatePostModal';
import '../../assets/styles/pages/BlogPage.css';

const BlogPage: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const totalPages = 10;

  // Dữ liệu mẫu blog posts
  const blogPosts = [
    {
      id: 1,
      avatarSrc: 'https://i.pravatar.cc/88?img=1',
      username: 'user_name',
      timeAgo: '20 giờ',
      location: 'Hồ Gươm - Quận Hoàn Kiếm',
      rating: 3.6,
      imageSrc1: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      imageSrc2: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      likeCount: 36,
      commentCount: 36,
      description: 'Hồ Hoàn Kiếm còn được gọi là Hồ Gươm là một hồ nước ngọt tự nhiên nằm ở phường Hoàn Kiếm,'
    },
    {
      id: 2,
      avatarSrc: 'https://i.pravatar.cc/88?img=2',
      username: 'user_name',
      timeAgo: '20 giờ',
      location: 'Hồ Gươm - Quận Hoàn Kiếm',
      rating: 3.6,
      imageSrc1: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      imageSrc2: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      likeCount: 36,
      commentCount: 36,
      description: 'Hồ Hoàn Kiếm còn được gọi là Hồ Gươm là một hồ nước ngọt tự nhiên nằm ở phường Hoàn Kiếm,'
    },
    {
      id: 3,
      avatarSrc: 'https://i.pravatar.cc/88?img=3',
      username: 'user_name',
      timeAgo: '20 giờ',
      location: 'Hồ Gươm - Quận Hoàn Kiếm',
      rating: 3.6,
      imageSrc1: 'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg',
      imageSrc2: 'https://dulichnewtour.vn/ckfinder/images/Tours/langbac/lang-bac%20(2).jpg',
      likeCount: 36,
      commentCount: 36,
      description: 'Hồ Hoàn Kiếm còn được gọi là Hồ Gươm là một hồ nước ngọt tự nhiên nằm ở phường Hoàn Kiếm,'
    }
  ];

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <>
      <Header />
      <div className="blog-page">
        {/* Chia sẻ trải nghiệm Section */}
        <section className="blog-page__share-section">
          <h1 className="blog-page__title">Chia sẻ trải nghiệm</h1>
          <div 
            className="blog-page__input-box"
            onClick={() => setIsModalOpen(true)}
            style={{ cursor: 'pointer' }}
          >
            <span className="blog-page__input-placeholder">
              Hãy chia sẻ trải nghiệm của bạn!!
            </span>
          </div>
        </section>

        {/* Create Post Modal */}
        <CreatePostModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSubmit={(data) => {
            console.log('New post:', data);
            // TODO: Handle post submission
          }}
        />

        {/* Newfeed Section */}
        <section className="blog-page__newfeed-section">
          <h2 className="blog-page__section-title">Newfeed</h2>
          <div className="blog-page__posts">
            {blogPosts.map((post) => (
              <BlogCard
                key={post.id}
                id={post.id}
                avatarSrc={post.avatarSrc}
                username={post.username}
                timeAgo={post.timeAgo}
                location={post.location}
                rating={post.rating}
                imageSrc1={post.imageSrc1}
                imageSrc2={post.imageSrc2}
                likeCount={post.likeCount}
                commentCount={post.commentCount}
                description={post.description}
              />
            ))}
          </div>
        </section>

        {/* Pagination */}
        <div className="blog-page__pagination">
          <button 
            className="blog-page__pagination-arrow"
            onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
          >
            «
          </button>
          
          {[1, 2, 3].map((page) => (
            <button
              key={page}
              className={`blog-page__pagination-btn ${currentPage === page ? 'active' : ''}`}
              onClick={() => handlePageChange(page)}
            >
              {page}
            </button>
          ))}
          
          <span className="blog-page__pagination-ellipsis">...</span>
          
          <button
            className={`blog-page__pagination-btn ${currentPage === totalPages ? 'active' : ''}`}
            onClick={() => handlePageChange(totalPages)}
          >
            {totalPages}
          </button>
          
          <button 
            className="blog-page__pagination-arrow"
            onClick={() => handlePageChange(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
          >
            »
          </button>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default BlogPage;

