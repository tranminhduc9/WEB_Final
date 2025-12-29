import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { Icons } from '../../config/constants';
import { adminService } from '../../services';
import type { PlaceDetail } from '../../types/models';
import '../../assets/styles/pages/AdminLocationsPage.css';

// Mock data fallback
const mockLocations = [
    { id: 1, name: 'Hồ Hoàn Kiếm', rating_average: 4.5, latitude: 21.0285, longitude: 105.8542 },
    { id: 2, name: 'Văn Miếu - Quốc Tử Giám', rating_average: 4.7, latitude: 21.0267, longitude: 105.8355 },
    { id: 3, name: 'Lăng Chủ Tịch Hồ Chí Minh', rating_average: 4.8, latitude: 21.0369, longitude: 105.8344 },
    { id: 4, name: 'Chùa Một Cột', rating_average: 4.3, latitude: 21.0359, longitude: 105.8334 },
    { id: 5, name: 'Hồ Tây', rating_average: 4.2, latitude: 21.0538, longitude: 105.8194 },
];

function AdminLocationsPage() {
    const navigate = useNavigate();
    const [locations, setLocations] = useState<PlaceDetail[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<number | null>(null);

    const itemsPerPage = 10;

    // Fetch locations from API
    useEffect(() => {
        const fetchLocations = async () => {
            setIsLoading(true);
            try {
                const response = await adminService.getPlaces();
                if (response.success && response.data && response.data.length > 0) {
                    setLocations(response.data);
                } else {
                    console.log('No places from API, using mock data');
                    setLocations(mockLocations as any);
                }
            } catch (error) {
                console.error('Error fetching places:', error);
                setLocations(mockLocations as any);
            } finally {
                setIsLoading(false);
            }
        };

        fetchLocations();
    }, []);

    // Filter locations based on search
    const filteredLocations = locations.filter(location =>
        location.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Pagination
    const totalPages = Math.ceil(filteredLocations.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginatedLocations = filteredLocations.slice(startIndex, startIndex + itemsPerPage);

    // Handle edit
    const handleEdit = (locationId: number) => {
        console.log('Edit location:', locationId);
        alert('Chức năng chỉnh sửa đang được phát triển');
    };

    // Handle delete
    const handleDelete = async (locationId: number) => {
        if (!window.confirm('Bạn có chắc chắn muốn xóa địa điểm này?')) return;

        setActionLoading(locationId);
        try {
            const response = await adminService.deletePlace(locationId);
            if (response.success) {
                setLocations(prev => prev.filter(loc => loc.id !== locationId));
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

    // Generate page numbers
    const getPageNumbers = () => {
        const pages: (number | string)[] = [];
        if (totalPages <= 5) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else {
            pages.push(1, 2, 3);
            if (totalPages > 4) pages.push('...');
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
                        placeholder="Tìm kiếm Địa điểm"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="admin-locations-search__input"
                    />
                    <Icons.Search className="admin-locations-search__icon" />
                </div>

                {/* Results Count and Add Button */}
                <div className="admin-locations-toolbar">
                    <p className="admin-locations-count">
                        {isLoading ? 'Đang tải...' : `Có ${filteredLocations.length} kết quả`}
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
                                <th>place_id</th>
                                <th>place_name</th>
                                <th>rating</th>
                                <th>long/lat</th>
                                <th colSpan={2}>Chức năng</th>
                            </tr>
                        </thead>
                        <tbody>
                            {isLoading ? (
                                <tr>
                                    <td colSpan={6} className="admin-locations-loading">Đang tải...</td>
                                </tr>
                            ) : paginatedLocations.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="admin-locations-empty">Không có địa điểm nào</td>
                                </tr>
                            ) : (
                                paginatedLocations.map((location) => (
                                    <tr key={location.id}>
                                        <td>{location.id}</td>
                                        <td>{location.name}</td>
                                        <td>{location.rating_average?.toFixed(1) || 'N/A'}</td>
                                        <td>{location.longitude?.toFixed(4)}/{location.latitude?.toFixed(4)}</td>
                                        <td>
                                            <button
                                                className="admin-locations-action-btn"
                                                onClick={() => handleEdit(location.id)}
                                            >
                                                <Icons.Edit className="admin-locations-action-icon" />
                                                Chỉnh sửa
                                            </button>
                                        </td>
                                        <td>
                                            <button
                                                className="admin-locations-action-btn admin-locations-action-btn--delete"
                                                onClick={() => handleDelete(location.id)}
                                                disabled={actionLoading === location.id}
                                            >
                                                <Icons.Trash className="admin-locations-action-icon" />
                                                {actionLoading === location.id ? 'Đang xóa...' : 'Xóa'}
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
                            onClick={() => setCurrentPage(1)}
                            disabled={currentPage === 1}
                        >
                            «
                        </button>

                        {getPageNumbers().map((page, index) => (
                            <button
                                key={index}
                                className={`admin-locations-pagination__page ${page === currentPage ? 'active' : ''
                                    } ${page === '...' ? 'ellipsis' : ''}`}
                                onClick={() => typeof page === 'number' && setCurrentPage(page)}
                                disabled={page === '...'}
                            >
                                {page}
                            </button>
                        ))}

                        <button
                            className="admin-locations-pagination__nav"
                            onClick={() => setCurrentPage(totalPages)}
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
