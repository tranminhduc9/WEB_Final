import React, { useState } from 'react';
import { Icons } from '../constants';
import '../../css/CreatePostModal.css';

interface CreatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit?: (data: {
    location: string;
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
  const [rating, setRating] = useState<number | ''>('');
  const [content, setContent] = useState('');
  const [images, setImages] = useState<File[]>([]);

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (onSubmit && content.trim()) {
      onSubmit({
        location,
        rating: Number(rating) || 0,
        content,
        images,
      });
    }
    // Reset form
    setLocation('');
    setRating('');
    setContent('');
    setImages([]);
    onClose();
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
          <div className="create-post__option">
            <Icons.Location className="create-post__option-icon" />
            <span>Chọn địa điểm</span>
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



