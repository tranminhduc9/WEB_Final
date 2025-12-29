import { Link } from 'react-router-dom';
import { Icons } from '../../config/constants';
import '../../assets/styles/components/LocationCard.css';

interface LocationCardProps {
  id?: string;
  imageSrc: string;
  title: string;
  address: string;
  priceMin?: number;
  priceMax?: number;
  rating: number;
  reviewCount?: number;  // Changed to optional number
}

// Format price VND
const formatPriceVND = (price: number): string => {
  if (price === 0) return '0 VNĐ';
  return `${price.toLocaleString('vi-VN')} VNĐ`;
};

// Format review count (e.g., 3600 -> "3.6K+")
const formatReviewCount = (count: number | undefined): string => {
  if (!count || count === 0) return '0';
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1).replace(/\.0$/, '')}K+`;
  }
  return count.toString();
};

export default function LocationCard({
  id,
  imageSrc,
  title,
  address,
  priceMin = 0,
  priceMax = 0,
  rating,
  reviewCount,
}: LocationCardProps) {
  // Hiển thị giá
  const renderPrice = () => {
    if (priceMin === 0 && priceMax === 0) {
      return <span className="price-text">Miễn phí</span>;
    }
    return (
      <span className="price-text">
        {formatPriceVND(priceMin)} - {formatPriceVND(priceMax)}
      </span>
    );
  };

  const cardContent = (
    <>
      <img src={imageSrc} alt={title} />
      <div className="place-info">
        <div className="place-info-top">
          <h3>{title}</h3>
          <p className="place-address">
            <Icons.Location className="place-address-icon" />
            {address}
          </p>
        </div>
        <div className="place-footer">
          {/* Price trước Rating */}
          <div className="place-price">
            {renderPrice()}
          </div>
          <div className="place-rating">
            <span className="rating-value">⭐ {rating.toFixed(1)}</span>
            <span className="review-count"> ~ {formatReviewCount(reviewCount)} reviews</span>
          </div>
        </div>
      </div>
    </>
  );

  if (id) {
    return (
      <Link to={`/location/${id}`} className="place-card place-card--link">
        {cardContent}
      </Link>
    );
  }

  return (
    <div className="place-card">
      {cardContent}
    </div>
  );
}