/**
 * Post Service - API calls cho Posts domain
 * Base URL: http://localhost:8080/api/v1
 * 
 * Endpoints theo API Spec:
 * - GET /posts - Community Feed (list all posts)
 * - GET /posts/:id - Post detail
 * - POST /posts - Create new post
 * - POST /posts/:id/like - Like/Unlike post
 * 
 * NOTE: 
 * - Không có endpoint riêng cho featured posts, dùng getPosts({ page: 1 })
 * - Không có endpoint lấy posts theo user ID
 * - Để lấy posts theo place, dùng placeService.getPlaceById() -> response.related_posts
 */

import axiosClient from '../api/axiosClient';
import type {
    ListResponse,
    PostDetail,
    CreatePostRequest,
    SingleResponse,
} from '../types/models';
import type { BaseResponse } from '../types/auth';

// ============================
// POST SERVICE
// ============================

export const postService = {
    /**
     * Lấy danh sách bài viết (Community Feed)
     * GET /posts
     * Params: page, limit
     * 
     * Để lấy bài viết nổi bật cho homepage: getPosts(1, 5)
     */
    getPosts: async (page?: number, limit?: number): Promise<ListResponse<PostDetail>> => {
        const queryParams = new URLSearchParams();

        if (page) queryParams.append('page', String(page));
        if (limit) queryParams.append('limit', String(limit));

        const queryString = queryParams.toString();
        const url = queryString ? `/posts?${queryString}` : '/posts';

        const response = await axiosClient.get<never, ListResponse<PostDetail>>(url);
        return response;
    },

    /**
     * Lấy chi tiết một bài viết
     * GET /posts/:id
     */
    getPostById: async (id: string): Promise<SingleResponse<PostDetail>> => {
        const response = await axiosClient.get<never, SingleResponse<PostDetail>>(
            `/posts/${id}`
        );
        return response;
    },

    /**
     * Tạo bài viết mới
     * POST /posts
     */
    createPost: async (data: CreatePostRequest): Promise<SingleResponse<PostDetail>> => {
        const response = await axiosClient.post<CreatePostRequest, SingleResponse<PostDetail>>(
            '/posts',
            data
        );
        return response;
    },

    /**
     * Like/Unlike bài viết
     * POST /posts/:id/like
     */
    toggleLike: async (id: string): Promise<BaseResponse> => {
        const response = await axiosClient.post<never, BaseResponse>(
            `/posts/${id}/like`
        );
        return response;
    },
};

export default postService;
