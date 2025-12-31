/**
 * Upload Service - Xử lý upload file lên server
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

    const response = await axiosClient.post<never, UploadResponse>('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response;
};

/**
 * Upload ảnh địa điểm
 */
const uploadPlaceImages = async (files: File[], placeId: number): Promise<UploadResponse> => {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });
    formData.append('place_id', placeId.toString());

    const response = await axiosClient.post<never, UploadResponse>('/upload/place-images', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response;
};

/**
 * Upload avatar người dùng
 */
const uploadAvatar = async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axiosClient.post<never, UploadResponse>('/upload/avatar', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response;
};

/**
 * Upload ảnh bài viết
 */
const uploadPostImages = async (files: File[], postId?: number): Promise<UploadResponse> => {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });
    if (postId) {
        formData.append('post_id', postId.toString());
    }

    const response = await axiosClient.post<never, UploadResponse>('/upload/post-images', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response;
};

const uploadService = {
    uploadFiles,
    uploadPlaceImages,
    uploadAvatar,
    uploadPostImages,
};

export default uploadService;
