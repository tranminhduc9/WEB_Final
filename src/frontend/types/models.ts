/**
 * Model Types - Domain models theo API Spec
 * Base URL: http://localhost:8080/api/v1
 */

// ============================
// PAGINATION
// ============================

export interface Pagination {
    page: number;
    limit: number;
    total_items: number;
    total_pages: number;
}

// ============================
// GENERIC RESPONSE TYPES
// ============================

export interface ListResponse<T> {
    success: boolean;
    data: T[];
    pagination?: Pagination;
    message?: string;
}

export interface SingleResponse<T> {
    success: boolean;
    data: T;
    message?: string;
}

// ============================
// PLACES DOMAIN
// ============================

// District
export interface District {
    id: number;
    name: string;
}

// Place Type (Category)
export interface PlaceType {
    id: number;
    name: string;
}

// Place Compact (for lists)
export interface PlaceCompact {
    id: number;
    name: string;
    district_id: number;
    place_type_id: number;
    rating_average: number;
    price_min: number;
    price_max: number;
    main_image_url: string;
}

// Place Detail (full info) - includes related_posts
export interface PlaceDetail extends PlaceCompact {
    address?: string;
    description?: string;
    latitude?: number;
    longitude?: number;
    phone?: string;
    website?: string;
    opening_hours?: string;
    images?: string[];
    reviews_count?: number;
    related_posts?: PostDetail[];  // Bài viết liên quan đến địa điểm
    created_at?: string;
    updated_at?: string;
}

// ============================
// USERS DOMAIN
// ============================

// User Compact (for nested objects)
export interface UserCompact {
    id: number;
    full_name: string;
    avatar_url: string;
    role_id: number;
}

// User Detail Response (from /users/me)
export interface UserDetailResponse {
    id: number;
    email: string;
    full_name: string;
    avatar_url: string;
    phone?: string;
    role_id: number;
    recent_posts?: PostDetail[];  // Bài viết gần đây của user
    created_at?: string;
    updated_at?: string;
}

// ============================
// POSTS DOMAIN
// ============================

// Post Detail (Community Feed Item)
export interface PostDetail {
    _id: string;                    // MongoDB ID (string, starts with underscore)
    author: UserCompact;
    title: string;
    content: string;
    rating?: number;
    related_place?: PlaceCompact;
    images: string[];
    likes_count: number;
    comments_count: number;
    is_liked: boolean;
    created_at?: string;
    updated_at?: string;
}

// Post Create Request
export interface CreatePostRequest {
    title: string;
    content: string;
    rating?: number;
    related_place_id?: number;
    images?: string[];
}

// ============================
// QUERY PARAMS
// ============================

export interface PlaceQueryParams {
    page?: number;
    limit?: number;
    district_id?: number;
    place_type_id?: number;
    keyword?: string;
}

export interface PostQueryParams {
    page?: number;
    limit?: number;
}

export interface NearbyQueryParams {
    lat: number;
    long: number;
    radius?: number;
}
