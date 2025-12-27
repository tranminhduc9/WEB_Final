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

// Toggle Like Response - per WEB_CK.md spec
export interface ToggleLikeResponse {
    success: boolean;
    likes_count: number;
    is_liked: boolean;
}

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
     * Returns: BaseResponse per WEB_CK.md (201 Created)
     */
    createPost: async (data: CreatePostRequest): Promise<BaseResponse> => {
        const response = await axiosClient.post<CreatePostRequest, BaseResponse>(
            '/posts',
            data
        );
        return response;
    },

    /**
     * Like/Unlike bài viết
     * POST /posts/:id/like
     * Returns: { success, likes_count, is_liked } per WEB_CK.md
     */
    toggleLike: async (id: string): Promise<ToggleLikeResponse> => {
        const response = await axiosClient.post<never, ToggleLikeResponse>(
            `/posts/${id}/like`
        );
        return response;
    },

    /**
     * Toggle favorite bài viết
     * POST /posts/{id}/favorite
     * Returns: { success, is_favorited } per WEB_CK.md
     */
    toggleFavoritePost: async (id: string): Promise<{ success: boolean; is_favorited: boolean }> => {
        const response = await axiosClient.post<never, { success: boolean; is_favorited: boolean }>(
            `/posts/${id}/favorite`
        );
        return response;
    },

    /**
     * Add root comment to post
     * POST /posts/{id}/comments
     * Body: { content, images? }
     */
    addComment: async (postId: string, content: string, images?: string[]): Promise<BaseResponse> => {
        const response = await axiosClient.post<{ content: string; images?: string[] }, BaseResponse>(
            `/posts/${postId}/comments`,
            { content, images }
        );
        return response;
    },

    /**
     * Reply to a comment
     * POST /comments/{id}/reply
     * Body: { content, images? }
     */
    replyToComment: async (commentId: string, content: string, images?: string[]): Promise<BaseResponse> => {
        const response = await axiosClient.post<{ content: string; images?: string[] }, BaseResponse>(
            `/comments/${commentId}/reply`,
            { content, images }
        );
        return response;
    },

    /**
     * Report post
     * POST /posts/{id}/report
     * Body: { reason, description? }
     */
    reportPost: async (postId: string, reason: string, description?: string): Promise<BaseResponse> => {
        const response = await axiosClient.post<{ reason: string; description?: string }, BaseResponse>(
            `/posts/${postId}/report`,
            { reason, description }
        );
        return response;
    },

    /**
     * Report comment
     * POST /comments/{id}/report
     * Body: { reason, description? }
     */
    reportComment: async (commentId: string, reason: string, description?: string): Promise<BaseResponse> => {
        const response = await axiosClient.post<{ reason: string; description?: string }, BaseResponse>(
            `/comments/${commentId}/report`,
            { reason, description }
        );
        return response;
    },
};

export default postService;
