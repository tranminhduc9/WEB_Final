import React from 'react';
import '../../css/LocationCard.css';

interface LocationCardProps {
  imageSrc: string;
  title: string;
  address: string;
  tags: string[];
  rating: number;
  reviewCount: string;
}

export default function LocationCard({
  imageSrc,
  title,
  address,
  tags,
  rating,
  reviewCount,
}: LocationCardProps) {
  return (
    <div className="place-card">
      <img src={imageSrc} alt={title} />
      <div className="place-info">
        <div className="place-info-top">
          <h3>{title}</h3>
          <p>{address}</p>
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
    </div>
  );
}