import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import Header from '../../components/client/Header';
import Footer from '../../components/client/Footer';
import LocationCard from '../../components/common/LocationCard';
import { placeService } from '../../services';
import type { PlaceCompact, District, PlaceType } from '../../types/models';
import '../../assets/styles/pages/PlacesPage.css';

const PlacesPage: React.FC = () => {
    const [searchParams, setSearchParams] = useSearchParams();

    // State cho data
    const [places, setPlaces] = useState<PlaceCompact[]>([]);
    const [districts, setDistricts] = useState<District[]>([]);
    const [placeTypes, setPlaceTypes] = useState<PlaceType[]>([]);

    // State cho filter
    const [selectedDistrict, setSelectedDistrict] = useState<number | null>(null);
    const [selectedType, setSelectedType] = useState<number | null>(null);
    const [showFilters, setShowFilters] = useState(false);

    // State cho pagination
    const [currentPage, setCurrentPage] = useState(1);
    const [totalItems, setTotalItems] = useState(0);
    const itemsPerPage = 9;

    // Loading states
    const [isLoading, setIsLoading] = useState(true);
    const [isFiltersLoading, setIsFiltersLoading] = useState(true);

    // Tổng số trang
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    // Fetch districts và place types (chỉ 1 lần)
    useEffect(() => {
        const fetchFilters = async () => {
            setIsFiltersLoading(true);
            try {
                const [districtsRes, typesRes] = await Promise.all([
                    placeService.getDistricts(),
                    placeService.getPlaceTypes()
                ]);
                setDistricts(districtsRes.data || []);
                setPlaceTypes(typesRes.data || []);
            } catch (error) {
                console.error('Error loading filters:', error);
            } finally {
                setIsFiltersLoading(false);
            }
        };
        fetchFilters();
    }, []);

    // Fetch places với filter và pagination
    const fetchPlaces = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await placeService.getPlaces({
                page: currentPage,
                limit: itemsPerPage,
                district_id: selectedDistrict || undefined,
                place_type_id: selectedType || undefined
            });

            setPlaces(response.data || []);
            setTotalItems(response.pagination?.total_items || 0);
        } catch (error) {
            console.error('Error fetching places:', error);
            setPlaces([]);
        } finally {
            setIsLoading(false);
        }
    }, [currentPage, selectedDistrict, selectedType]);

    // Gọi fetch khi filter/page thay đổi
    useEffect(() => {
        fetchPlaces();
    }, [fetchPlaces]);

    // Sync URL params
    useEffect(() => {
        const page = searchParams.get('page');
        if (page) setCurrentPage(Number(page));

        const district = searchParams.get('district');
        if (district) setSelectedDistrict(Number(district));

        const type = searchParams.get('type');
        if (type) setSelectedType(Number(type));
    }, []);

    // Update URL khi filter thay đổi
    const updateFilters = (district: number | null, type: number | null) => {
        setSelectedDistrict(district);
        setSelectedType(type);
        setCurrentPage(1);

        const params = new URLSearchParams();
        if (district) params.set('district', String(district));
        if (type) params.set('type', String(type));
        setSearchParams(params);
    };

    // Render pagination
    const renderPagination = () => {
        if (totalPages <= 1) return null;

        const pages: (number | string)[] = [];

        // Logic hiển thị pagination
        if (totalPages <= 7) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else {
            pages.push(1);
            if (currentPage > 3) pages.push('...');

            const start = Math.max(2, currentPage - 1);
            const end = Math.min(totalPages - 1, currentPage + 1);

            for (let i = start; i <= end; i++) pages.push(i);

            if (currentPage < totalPages - 2) pages.push('...');
            pages.push(totalPages);
        }

        return (
            <div className="places-pagination">
                {/* Prev buttons */}
                <button
                    className="pagination-nav"
                    onClick={() => setCurrentPage(1)}
                    disabled={currentPage === 1}
                >
                    «
                </button>
                <button
                    className="pagination-nav"
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                >
                    ‹
                </button>

                {/* Page numbers */}
                {pages.map((page, idx) => (
                    typeof page === 'number' ? (
                        <button
                            key={idx}
                            className={`pagination-btn ${currentPage === page ? 'active' : ''}`}
                            onClick={() => setCurrentPage(page)}
                        >
                            {page}
                        </button>
                    ) : (
                        <span key={idx} className="pagination-ellipsis">{page}</span>
                    )
                ))}

                {/* Next buttons */}
                <button
                    className="pagination-nav"
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                >
                    ›
                </button>
                <button
                    className="pagination-nav"
                    onClick={() => setCurrentPage(totalPages)}
                    disabled={currentPage === totalPages}
                >
                    »
                </button>
            </div>
        );
    };

    return (
        <>
            <Header />
            <main className="places-page">
                {/* Hero Section */}
                <section className="places-hero">
                    <div className="places-hero__container">
                        <div className="places-hero__image places-hero__image--left">
                            <img
                                src="https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=600"
                                alt="Phố cổ Hà Nội"
                            />
                        </div>
                        <div className="places-hero__image places-hero__image--right">
                            <img
                                src="https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/07/ho-hoan-kiem-1.jpg"
                                alt="Hồ Hoàn Kiếm"
                            />
                        </div>
                    </div>
                </section>

                {/* Header Section */}
                <section className="places-header">
                    <div className="places-title-row">
                        <span className="places-title-accent"></span>
                        <h1 className="places-title">Tất cả địa điểm</h1>
                        <svg className="places-title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                            <circle cx="12" cy="10" r="3" />
                        </svg>
                    </div>

                    {/* Filter Toggle */}
                    <button
                        className="places-filter-toggle"
                        onClick={() => setShowFilters(!showFilters)}
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
                        </svg>
                        Bộ lọc (Phường, tags)
                    </button>

                    {/* Filter Panel */}
                    {showFilters && (
                        <div className="places-filter-panel">
                            <div className="filter-group">
                                <label>Quận/Huyện:</label>
                                <select
                                    value={selectedDistrict || ''}
                                    onChange={(e) => updateFilters(e.target.value ? Number(e.target.value) : null, selectedType)}
                                    disabled={isFiltersLoading}
                                >
                                    <option value="">Tất cả</option>
                                    {districts.map(d => (
                                        <option key={d.id} value={d.id}>{d.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="filter-group">
                                <label>Loại địa điểm:</label>
                                <select
                                    value={selectedType || ''}
                                    onChange={(e) => updateFilters(selectedDistrict, e.target.value ? Number(e.target.value) : null)}
                                    disabled={isFiltersLoading}
                                >
                                    <option value="">Tất cả</option>
                                    {placeTypes.map(t => (
                                        <option key={t.id} value={t.id}>{t.name}</option>
                                    ))}
                                </select>
                            </div>

                            {(selectedDistrict || selectedType) && (
                                <button
                                    className="filter-clear"
                                    onClick={() => updateFilters(null, null)}
                                >
                                    Xóa bộ lọc
                                </button>
                            )}
                        </div>
                    )}

                    {/* Results count */}
                    <p className="places-count">
                        Tìm được <strong>{totalItems}</strong> kết quả
                    </p>
                </section>

                {/* Places Grid */}
                <section className="places-grid-section">
                    {isLoading ? (
                        <div className="places-loading">
                            <div className="loading-spinner"></div>
                            <p>Đang tải địa điểm...</p>
                        </div>
                    ) : places.length === 0 ? (
                        <div className="places-empty">
                            <p>Không tìm thấy địa điểm nào</p>
                        </div>
                    ) : (
                        <div className="places-grid">
                            {places.map((place) => (
                                <LocationCard
                                    key={place.id}
                                    id={String(place.id)}
                                    imageSrc={place.main_image_url || 'https://via.placeholder.com/400x300'}
                                    title={place.name}
                                    address={place.address || place.district_name || ''}
                                    priceMin={place.price_min}
                                    priceMax={place.price_max}
                                    rating={place.rating_average || 0}
                                    reviewCount={place.rating_count || 0}
                                />
                            ))}
                        </div>
                    )}
                </section>

                {/* Pagination */}
                {!isLoading && places.length > 0 && renderPagination()}
            </main>
            <Footer />
        </>
    );
};

export default PlacesPage;
