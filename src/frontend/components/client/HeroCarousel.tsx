import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../assets/styles/components/HeroCarousel.css';

// Default images for homepage carousel
const DEFAULT_IMAGES = [
    'https://images.unsplash.com/photo-1710141968276-1461538e8bc9?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    'https://images.unsplash.com/photo-1599708153386-62bf3f035c78?w=1920&q=80',
    'https://images.unsplash.com/photo-1601108644994-1e450e786d3d?q=80&w=1200&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    'https://images.unsplash.com/photo-1702118937156-d8f4d86076ac?q=80&w=1074&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
];

interface HeroCarouselProps {
    title?: string;
    subtitle?: string;
    images?: string[];
    showSearchBar?: boolean;
    autoPlayInterval?: number;
}

export default function HeroCarousel({
    title = 'Gói trọn tinh hoa Hà Nội',
    subtitle = 'Từ phố cổ thâm trầm đến những vùng ngoại ô xanh mát, hãy để mỗi bước chân là một hành trình chạm vào hạnh phúc',
    images = DEFAULT_IMAGES,
    showSearchBar = true,
    autoPlayInterval = 5000
}: HeroCarouselProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [searchQuery, setSearchQuery] = useState('');
    const navigate = useNavigate();

    const goToNext = useCallback(() => {
        setCurrentIndex((prev) => (prev + 1) % images.length);
    }, [images.length]);

    const goToPrev = useCallback(() => {
        setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
    }, [images.length]);

    // Auto-play
    useEffect(() => {
        if (autoPlayInterval <= 0) return;

        const timer = setInterval(goToNext, autoPlayInterval);
        return () => clearInterval(timer);
    }, [autoPlayInterval, goToNext]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
            // Scroll to top khi search
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    return (
        <section className="hero-carousel">
            {/* Background Images */}
            <div className="hero-carousel__slides">
                {images.map((image: string, index: number) => (
                    <div
                        key={index}
                        className={`hero-carousel__slide ${index === currentIndex ? 'active' : ''}`}
                        style={{ backgroundImage: `url(${image})` }}
                    />
                ))}
            </div>

            {/* Content Overlay */}
            <div className="hero-carousel__content">
                <h1 className="hero-carousel__title">
                    {title}
                </h1>
                <p className="hero-carousel__subtitle">
                    {subtitle}
                </p>

                {/* Search Bar */}
                {showSearchBar && (
                    <form className="hero-carousel__search" onSubmit={handleSearch}>
                        <div className="hero-carousel__search-container">
                            <span className="hero-carousel__search-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <circle cx="11" cy="11" r="8" />
                                    <path d="M21 21l-4.35-4.35" />
                                </svg>
                            </span>
                            <input
                                type="text"
                                className="hero-carousel__search-input"
                                placeholder="Bạn muốn tìm kiếm địa điểm nào?"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                            <button type="submit" className="hero-carousel__search-btn">
                                Tìm kiếm
                            </button>
                        </div>
                    </form>
                )}
            </div>

            {/* Navigation Arrows */}
            <button
                className="hero-carousel__nav hero-carousel__nav--prev"
                onClick={goToPrev}
                aria-label="Previous slide"
            >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="15,18 9,12 15,6" />
                </svg>
            </button>
            <button
                className="hero-carousel__nav hero-carousel__nav--next"
                onClick={goToNext}
                aria-label="Next slide"
            >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="9,6 15,12 9,18" />
                </svg>
            </button>

            {/* Dots Indicator */}
            <div className="hero-carousel__dots">
                {images.map((_: string, index: number) => (
                    <button
                        key={index}
                        className={`hero-carousel__dot ${index === currentIndex ? 'active' : ''}`}
                        onClick={() => setCurrentIndex(index)}
                        aria-label={`Go to slide ${index + 1}`}
                    />
                ))}
            </div>
        </section>
    );
}
