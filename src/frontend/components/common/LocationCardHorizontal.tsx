import React from 'react';
import { Link } from 'react-router-dom';
import { Icons } from '../../config/constants';
import '../../assets/styles/components/LocationCardHorizontal.css';

interface LocationCardHorizontalProps {
    id: string;
    imageSrc: string;
    title: string;
    description: string;
    rating: number;
    likeCount: string;
    distance: string;
}

const LocationCardHorizontal: React.FC<LocationCardHorizontalProps> = ({
    id,
    imageSrc,
    title,
    description,
    rating,
    likeCount,
    distance,
}) => {
    return (
        <Link to={`/location/${id}`} className="location-card-h">
            <div className="location-card-h__image">
                <img src={imageSrc} alt={title} />
            </div>
            <div className="location-card-h__content">
                <div className="location-card-h__header">
                    <h4 className="location-card-h__title">{title}</h4>
                    <div className="location-card-h__rating">
                        <span>{rating}/5</span>
                    </div>
                </div>
                <p className="location-card-h__description">{description}</p>
                <div className="location-card-h__footer">
                    <div className="location-card-h__stat">
                        <Icons.Heart className="location-card-h__icon" />
                        <span>{likeCount}</span>
                    </div>
                    <div className="location-card-h__stat">
                        <Icons.Location className="location-card-h__icon" />
                        <span>{distance}</span>
                    </div>
                </div>
            </div>
        </Link>
    );
};

export default LocationCardHorizontal;
