import { Link } from 'react-router-dom';
import { Icons } from '../../config/constants';
import '../../assets/styles/components/LocationCard.css';

interface LocationCardProps {
  id?: string;
  imageSrc: string;
  title: string;
  address: string;
  tags: string[];
  rating: number;
  reviewCount: string;
}

export default function LocationCard({
  id,
  imageSrc,
  title,
  address,
  tags,
  rating,
  reviewCount,
}: LocationCardProps) {
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
          <div className="tags">
            {tags.map((tag, index) => (
              <span key={index} className="tag">{tag}</span>
            ))}
          </div>
        </div>
        <div className="place-rating">
          <span className="rating-value">⭐ {rating}</span>
          <span className="review-count"> – {reviewCount} reviews</span>
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