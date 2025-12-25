/**
 * Place Service - API calls cho Places domain
 * Base URL: http://localhost:8080/api/v1
 * 
 * Endpoints theo API Spec:
 * - GET /places - List places with filters
 * - GET /places/:id - Place detail (includes related_posts)
 * - GET /places/place-types - List place types
 * - GET /places/districts - List districts
 * - GET /places/nearby - Nearby places by coordinates
 */

import axiosClient from '../api/axiosClient';
import type {
    ListResponse,
    PlaceCompact,
    PlaceDetail,
    PlaceType,
    District,
    PlaceQueryParams,
    NearbyQueryParams,
    SingleResponse,
} from '../types/models';

// ============================
// PLACE SERVICE
// ============================

export const placeService = {
    /**
     * Lấy danh sách địa điểm
     * GET /places
     * Params: page, limit, district_id, place_type_id, keyword
     * 
     * Để lấy địa điểm nổi bật cho homepage: getPlaces({ page: 1, limit: 5 })
     */
    getPlaces: async (params?: PlaceQueryParams): Promise<ListResponse<PlaceCompact>> => {
        const queryParams = new URLSearchParams();

        if (params?.page) queryParams.append('page', String(params.page));
        if (params?.limit) queryParams.append('limit', String(params.limit));
        if (params?.district_id) queryParams.append('district_id', String(params.district_id));
        if (params?.place_type_id) queryParams.append('place_type_id', String(params.place_type_id));
        if (params?.keyword) queryParams.append('keyword', params.keyword);

        const queryString = queryParams.toString();
        const url = queryString ? `/places?${queryString}` : '/places';

        const response = await axiosClient.get<never, ListResponse<PlaceCompact>>(url);
        return response;
    },

    /**
     * Lấy chi tiết một địa điểm
     * GET /places/:id
     * 
     * Response bao gồm: related_posts (bài viết liên quan đến địa điểm)
     */
    getPlaceById: async (id: number): Promise<SingleResponse<PlaceDetail>> => {
        const response = await axiosClient.get<never, SingleResponse<PlaceDetail>>(
            `/places/${id}`
        );
        return response;
    },

    /**
     * Lấy danh sách loại địa điểm (categories)
     * GET /places/place-types
     */
    getPlaceTypes: async (): Promise<ListResponse<PlaceType>> => {
        const response = await axiosClient.get<never, ListResponse<PlaceType>>(
            '/places/place-types'
        );
        return response;
    },

    /**
     * Lấy danh sách quận/huyện
     * GET /places/districts
     */
    getDistricts: async (): Promise<ListResponse<District>> => {
        const response = await axiosClient.get<never, ListResponse<District>>(
            '/places/districts'
        );
        return response;
    },

    /**
     * Lấy địa điểm gần đây theo tọa độ
     * GET /places/nearby
     * Params: lat, long, radius (optional)
     */
    getNearbyPlaces: async (params: NearbyQueryParams): Promise<ListResponse<PlaceCompact>> => {
        const queryParams = new URLSearchParams();
        queryParams.append('lat', String(params.lat));
        queryParams.append('long', String(params.long));
        if (params.radius) queryParams.append('radius', String(params.radius));

        const response = await axiosClient.get<never, ListResponse<PlaceCompact>>(
            `/places/nearby?${queryParams.toString()}`
        );
        return response;
    },

    /**
     * Tìm kiếm địa điểm
     * GET /places/search
     * Params: keyword, district_id, page
     */
    searchPlaces: async (params: { keyword?: string; district_id?: number; page?: number }): Promise<ListResponse<PlaceCompact>> => {
        const queryParams = new URLSearchParams();
        if (params.keyword) queryParams.append('keyword', params.keyword);
        if (params.district_id) queryParams.append('district_id', String(params.district_id));
        if (params.page) queryParams.append('page', String(params.page));

        const queryString = queryParams.toString();
        const url = queryString ? `/places/search?${queryString}` : '/places/search';

        const response = await axiosClient.get<never, ListResponse<PlaceCompact>>(url);
        return response;
    },

    /**
     * Gợi ý tìm kiếm
     * GET /places/suggest
     * Params: keyword (required)
     */
    getSuggestions: async (keyword: string): Promise<{ success: boolean; data: string[] }> => {
        const response = await axiosClient.get<never, { success: boolean; data: string[] }>(
            `/places/suggest?keyword=${encodeURIComponent(keyword)}`
        );
        return response;
    },

    /**
     * Toggle yêu thích địa điểm
     * POST /places/{id}/favorite
     * Requires authentication
     */
    toggleFavoritePlace: async (id: number): Promise<{ success: boolean; is_favorited: boolean }> => {
        const response = await axiosClient.post<never, { success: boolean; is_favorited: boolean }>(
            `/places/${id}/favorite`
        );
        return response;
    },
};

export default placeService;
