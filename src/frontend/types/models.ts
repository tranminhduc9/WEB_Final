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

// Place Compact (for lists) - Synced with db.md
export interface PlaceCompact {
    id: number;
    name: string;
    district_id: number;
    place_type_id: number;
    rating_average: number;
    rating_count?: number;
    price_min: number;
    price_max: number;
    main_image_url?: string;  // From place_images where is_main=true
}

// Place Detail (full info) - Synced with db.md places table
export interface PlaceDetail extends PlaceCompact {
    // From db: address_detail (not address)
    address_detail?: string;
    description?: string;
    latitude: number;
    longitude: number;

    // Business hours - from db: open_hour, close_hour
    open_hour?: string;   // Time format "HH:MM"
    close_hour?: string;  // Time format "HH:MM"

    // Rating details
    rating_total?: number;

    // Images array (from place_images table)
    images?: string[];

    // Related data
    related_posts?: PostDetail[];

    // Soft delete
    deleted_at?: string | null;

    // Timestamps
    created_at?: string;
    updated_at?: string;

    // Legacy fields for backward compatibility
    address?: string;        // Alias for address_detail
    opening_hours?: string;  // Legacy: will be computed from open_hour + close_hour
    reviews_count?: number;  // Alias for rating_count
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

// User Detail Response (from /users/me) - Synced with database.py
export interface UserDetailResponse {
    id: number;
    email: string;
    full_name: string;
    avatar_url?: string | null;
    bio?: string | null;
    role_id: number;  // 1=admin, 2=moderator, 3=user
    reputation_score?: number;
    is_active?: boolean;
    ban_reason?: string | null;
    deleted_at?: string | null;
    last_login_at?: string | null;
    recent_posts?: PostDetail[];  // Bài viết gần đây của user
    created_at?: string;
    updated_at?: string;
}

// ============================
// POSTS DOMAIN - Synced with posts_mongo from db.md
// ============================

// Post type enum
export type PostType = 'post' | 'review';

// Post status enum
export type PostStatus = 'pending' | 'approved' | 'rejected';

// Post Comment in PostDetail - Synced with WEB_CK.md
export interface PostCommentInDetail {
    _id: string;
    user: UserCompact;
    content: string;
    parent_id?: string | null;  // null = root comment
    images?: string[];
    created_at?: string;
}

// Post Detail (Community Feed Item) - Synced with WEB_CK.md PostDetail schema
export interface PostDetail {
    _id: string;                      // MongoDB ObjectId as string
    type?: PostType;                  // 'post' or 'review'
    author_id?: number;               // FK to users.id
    author: UserCompact;              // Populated author data
    related_place_id?: number;        // FK to places.id
    related_place?: PlaceCompact;     // Populated place data
    title?: string;
    content: string;
    rating?: number;                  // For reviews (1-5)
    tags?: string[];                  // JSON array
    images: string[];                 // JSON array of image URLs
    likes_count: number;
    comments_count: number;
    status?: PostStatus;              // 'pending', 'approved', 'rejected'
    is_liked?: boolean;               // Computed: current user liked?
    comments?: PostCommentInDetail[]; // Comments array from WEB_CK.md
    created_at?: string;
    updated_at?: string;
}

// Post Create Request - Synced with WEB_CK.md (title is required)
export interface CreatePostRequest {
    type?: PostType;          // 'post' or 'review'
    title: string;            // Required per WEB_CK.md spec
    content: string;
    rating?: number;          // Required for reviews
    related_place_id?: number;
    tags?: string[];
    images?: string[];
}

// Post Comment - Synced with post_comments_mongo from db.md
export interface PostComment {
    _id: string;              // MongoDB ObjectId
    post_id: string;          // FK to posts._id
    user_id: number;          // FK to users.id
    author?: UserCompact;     // Populated author data
    content: string;
    parent_id?: string | null; // null = root comment, has ID = reply
    created_at?: string;
}

// Post Like - Synced with post_likes_mongo from db.md
export interface PostLike {
    _id: string;
    post_id: string;
    user_id: number;
    created_at?: string;
}

// ============================
// PLACE SUBTYPES - Synced with db.md
// ============================

// Place Image - from place_images table
export interface PlaceImage {
    id: number;
    place_id: number;
    image_url: string;
    is_main: boolean;
    created_at?: string;
}

// Restaurant subtype - from restaurants table
export interface Restaurant {
    place_id: number;
    cuisine_type?: string;
    avg_price_per_person?: number;
}

// Hotel subtype - from hotels table
export interface Hotel {
    place_id: number;
    star_rating?: number;
    price_per_night?: number;
    check_in_time?: string;   // Time format "HH:MM"
    check_out_time?: string;  // Time format "HH:MM"
}

// Tourist Attraction subtype - from tourist_attractions table
export interface TouristAttraction {
    place_id: number;
    ticket_price?: number;
    is_ticket_required?: boolean;
}

// PlaceDetail with subtype info
export interface PlaceDetailFull extends PlaceDetail {
    restaurant?: Restaurant;
    hotel?: Hotel;
    tourist_attraction?: TouristAttraction;
    place_images?: PlaceImage[];
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
