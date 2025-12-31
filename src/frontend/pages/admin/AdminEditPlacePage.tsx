import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { adminService, placeService, uploadService } from '../../services';
import type { PlaceUpdateRequest } from '../../types/admin';
import type { District, PlaceType } from '../../types/models';
import '../../assets/styles/pages/AdminAddPlacePage.css';

function AdminEditPlacePage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const fileInputRef = useRef<HTMLInputElement>(null);

    // States
    const [isLoading, setIsLoading] = useState(true);
    const [isUpdating, setIsUpdating] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [districts, setDistricts] = useState<District[]>([]);
    const [placeTypes, setPlaceTypes] = useState<PlaceType[]>([]);
    const [images, setImages] = useState<string[]>([]);

    const [formData, setFormData] = useState<PlaceUpdateRequest>({
        name: '',
        district_id: 1,
        place_type_id: 1,
        description: '',
        address_detail: '',
        latitude: 21.0285,
        longitude: 105.8542,
        open_hour: '',
        close_hour: '',
        price_min: 0,
        price_max: 0,
        images: [],
    });

    // Fetch place data, districts and place types
    useEffect(() => {
        const fetchData = async () => {
            if (!id) {
                navigate('/admin/locations');
                return;
            }

            setIsLoading(true);
            try {
                // Fetch place details
                const placeResponse = await placeService.getPlaceById(parseInt(id));
                if (placeResponse.success && placeResponse.data) {
                    const place = placeResponse.data;
                    setFormData({
                        name: place.name || '',
                        district_id: place.district_id || 1,
                        place_type_id: place.place_type_id || 1,
                        description: place.description || '',
                        address_detail: place.address_detail || place.address || '',
                        latitude: place.latitude || 21.0285,
                        longitude: place.longitude || 105.8542,
                        open_hour: place.open_hour || '',
                        close_hour: place.close_hour || '',
                        price_min: place.price_min || 0,
                        price_max: place.price_max || 0,
                        images: place.images || [],
                    });
                    setImages(place.images || []);
                }

                // Fetch districts
                const districtsResponse = await placeService.getDistricts();
                if (districtsResponse.success && districtsResponse.data) {
                    setDistricts(districtsResponse.data);
                }

                // Fetch place types
                const placeTypesResponse = await placeService.getPlaceTypes();
                if (placeTypesResponse.success && placeTypesResponse.data) {
                    setPlaceTypes(placeTypesResponse.data);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
                alert('Không thể tải thông tin địa điểm');
                navigate('/admin/locations');
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, [id, navigate]);

    // Handle input change
    const handleChange = (field: keyof PlaceUpdateRequest, value: string | number) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    // Handle image upload
    const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0 && id) {
            setIsUploading(true);
            try {
                const response = await uploadService.uploadPlaceImages(
                    Array.from(files),
                    parseInt(id)
                );
                if (response.urls && response.urls.length > 0) {
                    setImages(prev => [...prev, ...response.urls]);
                }
            } catch (error) {
                console.error('Error uploading images:', error);
                alert('Có lỗi khi tải ảnh lên');
            } finally {
                setIsUploading(false);
            }
        }
    };

    // Handle form submit
    const handleSubmit = async () => {
        if (!formData.name.trim()) {
            alert('Vui lòng nhập tên địa điểm');
            return;
        }

        if (!id) return;

        setIsUpdating(true);
        try {
            const response = await adminService.updatePlace(parseInt(id), {
                ...formData,
                images: images,
            });

            if (response.success) {
                alert('Đã cập nhật địa điểm thành công!');
                navigate('/admin/locations');
            } else {
                alert('Không thể cập nhật địa điểm. Vui lòng thử lại.');
            }
        } catch (error) {
            console.error('Error updating place:', error);
            alert('Có lỗi xảy ra khi cập nhật địa điểm');
        } finally {
            setIsUpdating(false);
        }
    };

    if (isLoading) {
        return (
            <div className="admin-add-place-page">
                <AdminHeader />
                <main className="admin-add-place-main">
                    <div className="admin-add-place-loading">
                        <div className="loading-spinner"></div>
                        <p>Đang tải thông tin địa điểm...</p>
                    </div>
                </main>
                <Footer />
            </div>
        );
    }

    return (
        <div className="admin-add-place-page">
            <AdminHeader />

            <main className="admin-add-place-main">
                {/* Title Section */}
                <div className="admin-add-place-header">
                    <div className="admin-section__accent"></div>
                    <h1 className="admin-add-place-title">Sửa địa điểm</h1>
                </div>

                {/* Form Content */}
                <div className="admin-add-place-form">
                    {/* Left Column */}
                    <div className="admin-add-place-column">
                        {/* Tên địa điểm */}
                        <div className="admin-add-place-field">
                            <label>Tên địa điểm<span className="required">*</span> (Điền)</label>
                            <input
                                type="text"
                                value={formData.name}
                                onChange={(e) => handleChange('name', e.target.value)}
                                placeholder=""
                            />
                        </div>

                        {/* Quận/Phường */}
                        <div className="admin-add-place-field">
                            <label>Quận/Phường<span className="required">*</span> (Chọn 1)</label>
                            <select
                                value={formData.district_id}
                                onChange={(e) => handleChange('district_id', parseInt(e.target.value))}
                            >
                                {districts.length > 0 ? (
                                    districts.map(district => (
                                        <option key={district.id} value={district.id}>
                                            {district.name}
                                        </option>
                                    ))
                                ) : (
                                    <>
                                        <option value={1}>Quận Hoàn Kiếm</option>
                                        <option value={2}>Quận Ba Đình</option>
                                        <option value={3}>Quận Đống Đa</option>
                                        <option value={4}>Quận Hai Bà Trưng</option>
                                        <option value={5}>Quận Tây Hồ</option>
                                    </>
                                )}
                            </select>
                        </div>

                        {/* Loại hình */}
                        <div className="admin-add-place-field">
                            <label>Loại hình<span className="required">*</span> (Chọn 1)</label>
                            <select
                                value={formData.place_type_id}
                                onChange={(e) => handleChange('place_type_id', parseInt(e.target.value))}
                            >
                                {placeTypes.length > 0 ? (
                                    placeTypes.map(type => (
                                        <option key={type.id} value={type.id}>
                                            {type.name}
                                        </option>
                                    ))
                                ) : (
                                    <>
                                        <option value={1}>Di tích lịch sử</option>
                                        <option value={2}>Công viên</option>
                                        <option value={3}>Nhà hàng</option>
                                        <option value={4}>Quán cà phê</option>
                                    </>
                                )}
                            </select>
                        </div>

                        {/* Mô tả */}
                        <div className="admin-add-place-field">
                            <label>Mô tả (Điền)</label>
                            <input
                                type="text"
                                value={formData.description}
                                onChange={(e) => handleChange('description', e.target.value)}
                                placeholder=""
                            />
                        </div>

                        {/* Vị trí */}
                        <div className="admin-add-place-field">
                            <label>Vị trí (Điền)</label>
                            <div className="admin-add-place-row">
                                <input
                                    type="text"
                                    value={formData.longitude || ''}
                                    onChange={(e) => handleChange('longitude', parseFloat(e.target.value) || 0)}
                                    placeholder="Kinh độ"
                                    className="half-width"
                                />
                                <input
                                    type="text"
                                    value={formData.latitude || ''}
                                    onChange={(e) => handleChange('latitude', parseFloat(e.target.value) || 0)}
                                    placeholder="Vĩ độ"
                                    className="half-width"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Right Column */}
                    <div className="admin-add-place-column">
                        {/* Thời gian */}
                        <div className="admin-add-place-field">
                            <label>Thời gian (Điền)</label>
                            <div className="admin-add-place-row">
                                <input
                                    type="text"
                                    value={formData.open_hour || ''}
                                    onChange={(e) => handleChange('open_hour', e.target.value)}
                                    placeholder="Mở cửa"
                                    className="half-width"
                                />
                                <input
                                    type="text"
                                    value={formData.close_hour || ''}
                                    onChange={(e) => handleChange('close_hour', e.target.value)}
                                    placeholder="Đóng cửa"
                                    className="half-width"
                                />
                            </div>
                        </div>

                        {/* Khoảng giá */}
                        <div className="admin-add-place-field">
                            <label>Khoảng giá (Điền)</label>
                            <div className="admin-add-place-row">
                                <input
                                    type="number"
                                    value={formData.price_min || ''}
                                    onChange={(e) => handleChange('price_min', parseInt(e.target.value) || 0)}
                                    placeholder="Min"
                                    className="half-width"
                                />
                                <input
                                    type="number"
                                    value={formData.price_max || ''}
                                    onChange={(e) => handleChange('price_max', parseInt(e.target.value) || 0)}
                                    placeholder="Max"
                                    className="half-width"
                                />
                            </div>
                        </div>

                        {/* Ảnh */}
                        <div className="admin-add-place-field">
                            <label>Ảnh</label>
                            <button
                                type="button"
                                className="admin-add-place-upload-btn"
                                onClick={() => fileInputRef.current?.click()}
                                disabled={isUploading}
                            >
                                {isUploading ? 'Đang tải...' : 'Thêm ảnh'}
                            </button>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                multiple
                                onChange={handleImageUpload}
                                style={{ display: 'none' }}
                            />

                            {images.length > 0 && (
                                <div className="admin-add-place-images">
                                    {images.map((img, index) => (
                                        <div key={index} className="admin-add-place-image-preview">
                                            <img src={img} alt={`Preview ${index + 1}`} />
                                            <button
                                                type="button"
                                                className="admin-add-place-image-remove"
                                                onClick={() => setImages(prev => prev.filter((_, i) => i !== index))}
                                            >
                                                ×
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Submit Button */}
                <div className="admin-add-place-actions">
                    <button
                        type="button"
                        className="admin-add-place-submit-btn"
                        onClick={handleSubmit}
                        disabled={isUpdating || !formData.name.trim()}
                    >
                        {isUpdating ? 'Đang cập nhật...' : 'Sửa địa điểm'}
                    </button>
                </div>
            </main>

            <Footer />
        </div>
    );
}

export default AdminEditPlacePage;
