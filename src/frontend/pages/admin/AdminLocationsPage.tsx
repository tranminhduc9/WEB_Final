import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { Icons } from '../../config/constants';
import { adminService } from '../../services';
import type { PlaceDetail, Pagination } from '../../types/models';
import '../../assets/styles/pages/AdminLocationsPage.css';

// Format date helper
const formatDate = (dateString?: string | null): string => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('vi-VN');
};

// Format price helper
const formatPrice = (min?: number | null, max?: number | null): string => {
    if (!min && !max) return 'Miễn phí';
    if (min && max) return `${min.toLocaleString('vi-VN')} - ${max.toLocaleString('vi-VN')}đ`;
    if (min) return `Từ ${min.toLocaleString('vi-VN')}đ`;
    if (max) return `Đến ${max.toLocaleString('vi-VN')}đ`;
    return '-';
};

function AdminLocationsPage() {
    const navigate = useNavigate();
    const [locations, setLocations] = useState<PlaceDetail[]>([]);
    const [pagination, setPagination] = useState<Pagination | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<number | null>(null);

    const itemsPerPage = 10;

    // Fetch locations from API with server-side pagination
    const fetchLocations = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await adminService.getPlaces({
                page: currentPage,
                limit: itemsPerPage
            });
            if (response.success && response.data) {
                setLocations(response.data);
                if (response.pagination) {
                    setPagination(response.pagination);
                }
            } else {
                setLocations([]);
            }
        } catch (error) {
            console.error('Error fetching places:', error);
            setLocations([]);
        } finally {
            setIsLoading(false);
        }
    }, [currentPage]);

    useEffect(() => {
        fetchLocations();
    }, [fetchLocations]);

    // Client-side search (only within current page data)
    const filteredLocations = searchQuery
        ? locations.filter(location =>
            location.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            location.district_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            location.address?.toLowerCase().includes(searchQuery.toLowerCase())
        )
        : locations;

    // Use server pagination
    const totalPages = pagination?.total_pages || 1;
    const totalItems = pagination?.total_items || locations.length;

    // Handle edit
    const handleEdit = (locationId: number) => {
        navigate(`/admin/locations/edit/${locationId}`);
    };

    // Handle delete
    const handleDelete = async (locationId: number) => {
        if (!window.confirm('Bạn có chắc chắn muốn xóa địa điểm này?')) return;

        setActionLoading(locationId);
        try {
            const response = await adminService.deletePlace(locationId);
            if (response.success) {
                // Refresh list after delete
                fetchLocations();
                alert('Đã xóa địa điểm thành công!');
            } else {
                alert('Không thể xóa địa điểm');
            }
        } catch (error) {
            console.error('Error deleting place:', error);
            alert('Có lỗi xảy ra khi xóa địa điểm');
        } finally {
            setActionLoading(null);
        }
    };

    // Handle page change
    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Generate page numbers
    const getPageNumbers = () => {
        const pages: (number | string)[] = [];
        if (totalPages <= 5) {
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
        return pages;
    };

    return (
        <div className="admin-locations-page">
            <AdminHeader />

            <main className="admin-locations-main">
                {/* Title Section */}
                <div className="admin-locations-header">
                    <div className="admin-section__accent"></div>
                    <h1 className="admin-locations-title">Quản lý địa điểm</h1>
                </div>

                {/* Search Bar */}
                <div className="admin-locations-search">
                    <input
                        type="text"
                        placeholder="Tìm kiếm trong trang hiện tại..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="admin-locations-search__input"
                    />
                    <Icons.Search className="admin-locations-search__icon" />
                </div>

                {/* Results Count and Add Button */}
                <div className="admin-locations-toolbar">
                    <p className="admin-locations-count">
                        {isLoading ? 'Đang tải...' : `Có ${totalItems} địa điểm (Trang ${currentPage}/${totalPages})`}
                    </p>
                    <button
                        className="admin-locations-add-btn"
                        onClick={() => navigate('/admin/locations/add')}
                    >
                        Thêm địa điểm
                    </button>
                </div>

                {/* Locations Table */}
                <div className="admin-locations-table-container">
                    <table className="admin-locations-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Tên địa điểm</th>
                                <th>Quận/Huyện</th>
                                <th>Đánh giá</th>
                                <th>Giá</th>
                                <th>Ngày tạo</th>
                                <th colSpan={2}>Chức năng</th>
                            </tr>
                        </thead>
                        <tbody>
                            {isLoading ? (
                                <tr>
                                    <td colSpan={8} className="admin-locations-loading">Đang tải...</td>
                                </tr>
                            ) : filteredLocations.length === 0 ? (
                                <tr>
                                    <td colSpan={8} className="admin-locations-empty">Không có địa điểm nào</td>
                                </tr>
                            ) : (
                                filteredLocations.map((location) => (
                                    <tr key={location.id}>
                                        <td>{location.id}</td>
                                        <td>
                                            <div className="admin-locations__name-cell">
                                                {location.main_image_url && (
                                                    <img
                                                        src={location.main_image_url}
                                                        alt={location.name}
                                                        className="admin-locations__thumbnail"
                                                    />
                                                )}
                                                <span>{location.name}</span>
                                            </div>
                                        </td>
                                        <td>{location.district_name || '-'}</td>
                                        <td>
                                            <span className="admin-locations__rating">
                                                ⭐ {location.rating_average?.toFixed(1) || '0'}
                                                <small>({location.rating_count || 0})</small>
                                            </span>
                                        </td>
                                        <td>{formatPrice(location.price_min, location.price_max)}</td>
                                        <td>{formatDate(location.created_at)}</td>
                                        <td>
                                            <button
                                                className="admin-locations-action-btn"
                                                onClick={() => handleEdit(location.id)}
                                            >
                                                <Icons.Edit className="admin-locations-action-icon" />
                                                Sửa
                                            </button>
                                        </td>
                                        <td>
                                            <button
                                                className="admin-locations-action-btn admin-locations-action-btn--delete"
                                                onClick={() => handleDelete(location.id)}
                                                disabled={actionLoading === location.id}
                                            >
                                                <Icons.Trash className="admin-locations-action-icon" />
                                                {actionLoading === location.id ? '...' : 'Xóa'}
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="admin-locations-pagination">
                        <button
                            className="admin-locations-pagination__nav"
                            onClick={() => handlePageChange(1)}
                            disabled={currentPage === 1}
                        >
                            «
                        </button>
                        <button
                            className="admin-locations-pagination__nav"
                            onClick={() => handlePageChange(currentPage - 1)}
                            disabled={currentPage === 1}
                        >
                            ‹
                        </button>

                        {getPageNumbers().map((page, index) => (
                            <button
                                key={index}
                                className={`admin-locations-pagination__page ${page === currentPage ? 'active' : ''
                                    } ${page === '...' ? 'ellipsis' : ''}`}
                                onClick={() => typeof page === 'number' && handlePageChange(page)}
                                disabled={page === '...'}
                            >
                                {page}
                            </button>
                        ))}

                        <button
                            className="admin-locations-pagination__nav"
                            onClick={() => handlePageChange(currentPage + 1)}
                            disabled={currentPage === totalPages}
                        >
                            ›
                        </button>
                        <button
                            className="admin-locations-pagination__nav"
                            onClick={() => handlePageChange(totalPages)}
                            disabled={currentPage === totalPages}
                        >
                            »
                        </button>
                    </div>
                )}
            </main>

            <Footer />
        </div>
    );
}

export default AdminLocationsPage;
