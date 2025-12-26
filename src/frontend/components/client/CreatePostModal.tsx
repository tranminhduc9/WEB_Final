import React, { useState, useEffect } from 'react';
import { Icons } from '../../config/constants';
import { placeService } from '../../services';
import type { PlaceCompact } from '../../types/models';
import '../../assets/styles/components/CreatePostModal.css';

interface CreatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit?: (data: {
    location: string;
    related_place_id?: number;
    rating: number;
    content: string;
    images: File[];
  }) => void;
}

const CreatePostModal: React.FC<CreatePostModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [location, setLocation] = useState('');
  const [selectedPlaceId, setSelectedPlaceId] = useState<number | undefined>();
  const [rating, setRating] = useState<number | ''>('');
  const [content, setContent] = useState('');
  const [images, setImages] = useState<File[]>([]);

  // Location picker state
  const [showLocationPicker, setShowLocationPicker] = useState(false);
  const [places, setPlaces] = useState<PlaceCompact[]>([]);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isLoadingPlaces, setIsLoadingPlaces] = useState(false);

  // Fetch places when location picker opens
  useEffect(() => {
    if (showLocationPicker) {
      const fetchPlaces = async () => {
        setIsLoadingPlaces(true);
        try {
          const response = await placeService.getPlaces({ page: 1, limit: 20 });
          setPlaces(response.data || []);
        } catch (error) {
          console.error('Error fetching places:', error);
        } finally {
          setIsLoadingPlaces(false);
        }
      };
      fetchPlaces();
    }
  }, [showLocationPicker]);

  // Search places
  useEffect(() => {
    if (showLocationPicker && searchKeyword.trim()) {
      const searchPlaces = async () => {
        setIsLoadingPlaces(true);
        try {
          const response = await placeService.searchPlaces({ keyword: searchKeyword });
          setPlaces(response.data || []);
        } catch (error) {
          console.error('Error searching places:', error);
        } finally {
          setIsLoadingPlaces(false);
        }
      };
      const timeoutId = setTimeout(searchPlaces, 300);
      return () => clearTimeout(timeoutId);
    }
  }, [searchKeyword, showLocationPicker]);

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (onSubmit && content.trim()) {
      onSubmit({
        location,
        related_place_id: selectedPlaceId,
        rating: Number(rating) || 0,
        content,
        images,
      });
    }
    // Reset form
    setLocation('');
    setSelectedPlaceId(undefined);
    setRating('');
    setContent('');
    setImages([]);
    onClose();
  };

  const handleSelectPlace = (place: PlaceCompact) => {
    setLocation(place.name);
    setSelectedPlaceId(place.id);
    setShowLocationPicker(false);
    setSearchKeyword('');
  };

  const handleImageSelect = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.multiple = true;
    input.onchange = (e) => {
      const files = (e.target as HTMLInputElement).files;
      if (files) {
        setImages(Array.from(files));
      }
    };
    input.click();
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="create-post-overlay" onClick={handleOverlayClick}>
      <div className="create-post-modal">
        {/* Header */}
        <div className="create-post__header">
          <h2 className="create-post__title">Đăng bài viết</h2>
          <button className="create-post__close" onClick={onClose}>
            <Icons.Close />
          </button>
        </div>

        <div className="create-post__divider"></div>

        {/* Options bar */}
        <div className="create-post__options">
          <div
            className="create-post__option create-post__option--clickable"
            onClick={() => setShowLocationPicker(!showLocationPicker)}
          >
            <Icons.Location className="create-post__option-icon" />
            <span>{location || 'Chọn địa điểm'}</span>
            {location && (
              <button
                className="create-post__clear-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setLocation('');
                  setSelectedPlaceId(undefined);
                }}
              >
                ✕
              </button>
            )}
          </div>

          <div className="create-post__option">
            <span className="create-post__star">⭐</span>
            <span>Đánh giá:</span>
            <input
              type="number"
              min="1"
              max="5"
              value={rating}
              onChange={(e) => setRating(Number(e.target.value))}
              className="create-post__rating-input"
              placeholder=""
            />
            <span>/5</span>
          </div>

          <div className="create-post__option" onClick={handleImageSelect}>
            <span className="create-post__image-icon">🖼️</span>
            <span>Chọn ảnh</span>
            {images.length > 0 && (
              <span className="create-post__image-count">({images.length})</span>
            )}
          </div>
        </div>

        {/* Location Picker Dropdown */}
        {showLocationPicker && (
          <div className="create-post__location-picker">
            <input
              type="text"
              className="create-post__location-search"
              placeholder="Tìm kiếm địa điểm..."
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              autoFocus
            />
            <div className="create-post__location-list">
              {isLoadingPlaces ? (
                <div className="create-post__location-loading">Đang tải...</div>
              ) : places.length === 0 ? (
                <div className="create-post__location-empty">Không tìm thấy địa điểm</div>
              ) : (
                places.map((place) => (
                  <div
                    key={place.id}
                    className="create-post__location-item"
                    onClick={() => handleSelectPlace(place)}
                  >
                    <Icons.Location className="create-post__location-item-icon" />
                    <span>{place.name}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Content textarea */}
        <div className="create-post__content">
          <textarea
            className="create-post__textarea"
            placeholder="Chia sẻ trải nghiệm của bạn"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>

        {/* Submit button */}
        <button className="create-post__submit" onClick={handleSubmit}>
          Đăng bài
        </button>
      </div>
    </div>
  );
};

export default CreatePostModal;
