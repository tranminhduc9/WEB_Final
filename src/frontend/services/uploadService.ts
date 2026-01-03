/**
 * Upload Service - Xử lý upload file lên server
 * 
 * Backend API: POST /upload?upload_type={type}&entity_id={id}
 * - upload_type: 'generic' | 'place' | 'avatar' | 'post'
 * - entity_id: ID của entity (required cho typed uploads)
 */

import axiosClient from '../api/axiosClient';

interface UploadResponse {
    success: boolean;
    urls: string[];
    message?: string;
}

/**
 * Upload files tổng quát
 */
const uploadFiles = async (files: File[], folder?: string): Promise<UploadResponse> => {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });
    if (folder) {
        formData.append('folder', folder);
    }

    const response = await axiosClient.post<never, UploadResponse>(
        '/upload?upload_type=generic',
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        }
    );

    return response;
};

/**
 * Upload ảnh địa điểm
 * @param files - Danh sách file ảnh
 * @param placeId - ID của place (optional, use 'temp' for new places before creation)
 */
const uploadPlaceImages = async (files: File[], placeId?: number): Promise<UploadResponse> => {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    const response = await axiosClient.post<never, UploadResponse>(
        `/upload?upload_type=place&entity_id=${placeId}`,
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        }
    );

    return response;
};

/**
 * Upload avatar người dùng
 * @param file - File ảnh avatar
 * @param userId - ID của user (optional, backend sẽ lấy từ token nếu không truyền)
 */
const uploadAvatar = async (file: File, userId?: number | string): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('files', file);  // Backend expects 'files' field

    // Sử dụng 'current' nếu không có userId (backend sẽ lấy từ token)
    const entityId = userId || 'current';

    const response = await axiosClient.post<never, UploadResponse>(
        `/upload?upload_type=avatar&entity_id=${entityId}`,
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        }
    );

    return response;
};

/**
 * Upload ảnh bài viết
 * @param files - Danh sách file ảnh
 * @param postId - ID của post (optional, có thể upload trước khi tạo post)
 */
const uploadPostImages = async (files: File[], postId?: string): Promise<UploadResponse> => {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    // Nếu có postId thì gắn entity_id, nếu không thì dùng generic
    const endpoint = postId
        ? `/upload?upload_type=post&entity_id=${postId}`
        : '/upload?upload_type=generic';

    const response = await axiosClient.post<never, UploadResponse>(
        endpoint,
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        }
    );

    return response;
};

const uploadService = {
    uploadFiles,
    uploadPlaceImages,
    uploadAvatar,
    uploadPostImages,
};

export default uploadService;
