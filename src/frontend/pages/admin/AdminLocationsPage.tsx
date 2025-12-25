import { useState } from 'react';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { Icons } from '../../config/constants';
import '../../assets/styles/pages/AdminLocationsPage.css';

// Mock data for locations
const mockLocations = [
    { id: 1, name: 'Hồ Hoàn Kiếm', rating: 4.5, lat: 21.0285, lng: 105.8542, isHidden: false },
    { id: 2, name: 'Văn Miếu - Quốc Tử Giám', rating: 4.7, lat: 21.0267, lng: 105.8355, isHidden: false },
    { id: 3, name: 'Lăng Chủ Tịch Hồ Chí Minh', rating: 4.8, lat: 21.0369, lng: 105.8344, isHidden: false },
    { id: 4, name: 'Chùa Một Cột', rating: 4.3, lat: 21.0359, lng: 105.8334, isHidden: true },
    { id: 5, name: 'Hồ Tây', rating: 4.2, lat: 21.0538, lng: 105.8194, isHidden: false },
    { id: 6, name: 'Phố cổ Hà Nội', rating: 4.6, lat: 21.0333, lng: 105.8500, isHidden: false },
    { id: 7, name: 'Bảo tàng Dân tộc học', rating: 4.4, lat: 21.0401, lng: 105.7989, isHidden: false },
    { id: 8, name: 'Nhà hát lớn Hà Nội', rating: 4.5, lat: 21.0245, lng: 105.8570, isHidden: false },
    { id: 9, name: 'Cầu Long Biên', rating: 4.1, lat: 21.0436, lng: 105.8594, isHidden: false },
    { id: 10, name: 'Hoàng Thành Thăng Long', rating: 4.6, lat: 21.0354, lng: 105.8400, isHidden: false },
];

function AdminLocationsPage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [locations, setLocations] = useState(mockLocations);
    const itemsPerPage = 10;

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
        // TODO: Navigate to edit page or open modal
    };

    // Handle hide/show toggle
    const handleHideToggle = (locationId: number) => {
        setLocations(prevLocations =>
            prevLocations.map(loc =>
                loc.id === locationId ? { ...loc, isHidden: !loc.isHidden } : loc
            )
        );
    };

    // Handle delete
    const handleDelete = (locationId: number) => {
        if (window.confirm('Bạn có chắc chắn muốn xóa địa điểm này?')) {
            setLocations(prevLocations => prevLocations.filter(loc => loc.id !== locationId));
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

                {/* Results Count */}
                <p className="admin-locations-count">Có {filteredLocations.length} kết quả</p>

                {/* Locations Table */}
                <div className="admin-locations-table-container">
                    <table className="admin-locations-table">
                        <thead>
                            <tr>
                                <th>place_id</th>
                                <th>place_name</th>
                                <th>rating</th>
                                <th>long/lat</th>
                                <th colSpan={3}>Chức năng</th>
                            </tr>
                        </thead>
                        <tbody>
                            {paginatedLocations.map((location) => (
                                <tr key={location.id}>
                                    <td>{location.id}</td>
                                    <td>{location.name}</td>
                                    <td>{location.rating}</td>
                                    <td>{location.lng.toFixed(4)}/{location.lat.toFixed(4)}</td>
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
                                            className="admin-locations-action-btn"
                                            onClick={() => handleHideToggle(location.id)}
                                        >
                                            <Icons.Hide className="admin-locations-action-icon" />
                                            {location.isHidden ? 'Show' : 'Hide'}
                                        </button>
                                    </td>
                                    <td>
                                        <button
                                            className="admin-locations-action-btn admin-locations-action-btn--delete"
                                            onClick={() => handleDelete(location.id)}
                                        >
                                            <Icons.Ban className="admin-locations-action-icon" />
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {/* Empty rows to fill table */}
                            {Array.from({ length: Math.max(0, itemsPerPage - paginatedLocations.length) }).map((_, index) => (
                                <tr key={`empty-${index}`} className="admin-locations-table__empty-row">
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
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
            </main>

            <Footer />
        </div>
    );
}

export default AdminLocationsPage;
