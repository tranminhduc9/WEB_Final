# Hanoivivu Frontend

Frontend application cho hệ thống du lịch Hà Nội, được xây dựng với React, TypeScript và Vite.

## Công nghệ sử dụng

- **React 19.1.1** - UI Framework
- **TypeScript ~5.9.3** - Type safety
- **Vite 7.1.7** - Build tool và dev server
- **React Router 7.9.4** - Client-side routing
- **Axios 1.13.2** - HTTP client
- **React Markdown 10.1.0** - Render markdown content
- **Vitest 3.2.4** - Testing framework

> [!NOTE]
> [Nguồn: package.json]

## 📁 Cấu trúc thư mục

```
src/frontend/
├── api/                    # API client configuration
│   ├── axiosClient.ts     # Axios instance với interceptors
│   ├── authApi.ts         # Auth API endpoints
│   ├── userApi.ts         # User API endpoints
│   ├── adminApi.ts        # Admin API endpoints
│   └── index.ts           # Re-exports
│
├── assets/                 # Static assets
│   ├── images/            # Hình ảnh
│   └── styles/            # CSS files
│       ├── components/    # Component styles
│       ├── pages/         # Page styles
│       └── variables.css  # CSS variables
│
├── components/             # React components
│   ├── admin/             # Admin components
│   │   └── AdminHeader.tsx
│   ├── client/            # Client components
│   │   ├── Header.tsx     # Header với responsive
│   │   ├── Footer.tsx     # Footer component
│   │   ├── Chatbot.tsx    # AI Chatbot
│   │   ├── HeroCarousel.tsx
│   │   ├── PostCard.tsx
│   │   ├── LocationCardHorizontal.tsx
│   │   └── CreatePostModal.tsx
│   └── common/            # Shared components
│       ├── LocationCard.tsx
│       └── BlogCard.tsx
│
├── config/                 # Configuration
│   └── constants.tsx      # App constants và icons
│
├── contexts/               # React Contexts
│   ├── AuthContext.tsx    # Authentication context
│   └── index.ts           # Re-exports
│
├── hooks/                  # Custom React hooks
│   ├── useAuth.ts
│   ├── useUser.ts
│   ├── useScrollToTop.ts
│   └── index.ts           # Re-exports
│
├── pages/                  # Page components
│   ├── admin/             # Admin pages (8 files)
│   │   ├── AdminHomePage.tsx
│   │   ├── AdminUsersPage.tsx
│   │   ├── AdminLocationsPage.tsx
│   │   ├── AdminPostsPage.tsx
│   │   ├── AdminReportsPage.tsx
│   │   ├── AdminLogPage.tsx
│   │   ├── AdminAddPlacePage.tsx
│   │   └── AdminEditPlacePage.tsx
│   ├── client/            # Client pages (13 files)
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── ForgotPassword.tsx
│   │   ├── ResetPassword.tsx
│   │   ├── PlacesPage.tsx
│   │   ├── TrendPlacesPage.tsx
│   │   ├── BlogPage.tsx
│   │   ├── BlogDetailPage.tsx
│   │   ├── SearchResultsPage.tsx
│   │   ├── UserProfilePage.tsx
│   │   ├── UserPostsPage.tsx
│   │   ├── FavoritePlacesPage.tsx
│   │   └── LocationInfoPage.tsx
│   └── ErrorPage.tsx      # Error page component
│
├── routes/                 # Route guards
│   ├── ProtectedRoute.tsx # Yêu cầu authentication
│   ├── AdminRoute.tsx     # Yêu cầu admin role
│   ├── PublicRoute.tsx    # Public routes
│   └── index.ts           # Re-exports
│
├── services/               # Business logic & API services
│   ├── authService.ts     # Authentication service
│   ├── userService.ts     # User service
│   ├── placeService.ts    # Place service
│   ├── postService.ts     # Post service
│   ├── chatbotService.ts  # Chatbot service
│   ├── adminService.ts    # Admin service
│   ├── uploadService.ts   # File upload service
│   ├── index.ts           # Re-exports
│   └── __tests__/         # Test files
│
├── utils/                  # Utility functions
│   └── timeUtils.ts       # Time formatting (formatTimeAgo)
│
├── types/                  # TypeScript type definitions
│   ├── auth.ts            # Auth types
│   ├── user.ts            # User types
│   ├── models.ts          # Data models
│   ├── admin.ts           # Admin types
│   ├── common.ts          # Common types
│   └── index.ts           # Re-exports
│
├── test/                   # Test utilities
│   └── setup.ts           # Test setup
│
├── App.tsx                 # Root component (Homepage)
├── App.css                 # Homepage styles
├── main.tsx                # Entry point với router
├── index.css               # Global styles
└── vite.config.ts          # Vite configuration
```

> [!NOTE]
> [Nguồn: Folder listing từ src/frontend/]

## Cách chạy

### Cài đặt dependencies

```bash
npm install
```

### Development server

```bash
npm run dev
```

Ứng dụng sẽ chạy tại `http://localhost:5173`

### Build production

```bash
npm run build
```

### Preview production build

```bash
npm run preview
```

### Testing

```bash
# Chạy tests trong watch mode
npm test

# Chạy tests một lần
npm run test:run
```

### Linting

```bash
npm run lint
```

> [!NOTE]
> [Nguồn: package.json scripts]

## Tính năng chính

### Authentication & Authorization

- **Đăng ký** (`/register`) - Form validation, error handling
- **Đăng nhập** (`/login`) - Email + password
- **Quên mật khẩu** (`/forgot-password`) - Gửi email reset
- **Đặt lại mật khẩu** (`/reset-password`) - Token-based reset
- **Protected routes** - Yêu cầu đăng nhập, tự động redirect về `/login`
- **Admin routes** - Yêu cầu admin role (role_id=1)
- **JWT token management** - Access token + refresh token trong localStorage
- **Auto-logout** - Khi token hết hạn

> [!NOTE]
> [Nguồn: authService.ts, main.tsx]

### Pages

#### Client Pages

| Route | Component | Mô tả | Protected |
|-------|-----------|-------|-----------|
| `/` | App.tsx | Trang chủ với hero carousel | ❌ |
| `/search` | SearchResultsPage | Tìm kiếm địa điểm | ❌ |
| `/places` | PlacesPage | Danh sách địa điểm | ❌ |
| `/trend-places` | TrendPlacesPage | Địa điểm phổ biến | ❌ |
| `/blogs` | BlogPage | Danh sách bài viết | ❌ |
| `/blog/:id` | BlogDetailPage | Chi tiết bài viết | ❌ |
| `/location/:id` | LocationInfoPage | Chi tiết địa điểm | ❌ |
| `/login` | Login | Đăng nhập | PublicRoute |
| `/register` | Register | Đăng ký | PublicRoute |
| `/forgot-password` | ForgotPassword | Quên mật khẩu | PublicRoute |
| `/reset-password` | ResetPassword | Đặt lại mật khẩu | PublicRoute |
| `/profile` | UserProfilePage | Hồ sơ người dùng | ✅ Protected |
| `/user/:id` | UserProfilePage | Xem profile người khác | ❌ |
| `/places/favourite` | FavoritePlacesPage | Địa điểm yêu thích | ✅ Protected |
| `/places/favourite/:userId` | FavoritePlacesPage | Xem favorites người khác | ❌ |
| `/posts/user` | UserPostsPage | Bài viết của mình | ✅ Protected |
| `/posts/user/:userId` | UserPostsPage | Xem posts người khác | ❌ |

> [!NOTE]
> [Nguồn: main.tsx]

#### Admin Pages

| Route | Component | Mô tả |
|-------|-----------|-------|
| `/admin` | AdminHomePage | Dashboard với thống kê |
| `/admin/users` | AdminUsersPage | Quản lý người dùng |
| `/admin/locations` | AdminLocationsPage | Quản lý địa điểm |
| `/admin/locations/add` | AdminAddPlacePage | Thêm địa điểm mới |
| `/admin/locations/edit/:id` | AdminEditPlacePage | Chỉnh sửa địa điểm |
| `/admin/posts` | AdminPostsPage | Quản lý bài viết |
| `/admin/reports` | AdminReportsPage | Quản lý báo cáo |
| `/admin/log` | AdminLogPage | Xem audit logs |

> [!NOTE]
> Tất cả admin routes yêu cầu quyền admin (AdminRoute)
> [Nguồn: main.tsx]

### Components

#### Admin Components
- **AdminHeader.tsx** - Header cho admin panel

#### Client Components
- **Header.tsx** - Header responsive với mobile menu, search bar, user dropdown
- **Footer.tsx** - Footer component
- **Chatbot.tsx** - AI chatbot tích hợp Google Gemini
- **HeroCarousel.tsx** - Carousel với search bar tích hợp
- **PostCard.tsx** - Card hiển thị bài viết
- **LocationCardHorizontal.tsx** - Card địa điểm horizontal
- **CreatePostModal.tsx** - Modal tạo bài viết với image upload

#### Common Components
- **LocationCard.tsx** - Card hiển thị địa điểm vertical
- **BlogCard.tsx** - Card hiển thị bài viết

> [!NOTE]
> [Nguồn: components/admin/, components/client/, components/common/]

### Services

#### authService
[Nguồn: authService.ts]

| Function | API Endpoint | Mô tả |
|----------|--------------|-------|
| `login(credentials)` | POST /auth/login | Đăng nhập |
| `register(data)` | POST /auth/register | Đăng ký |
| `logout(data?)` | POST /auth/logout | Đăng xuất |
| `refreshToken()` | POST /auth/refresh | Refresh access token |
| `getCurrentUser()` | - | Lấy user từ localStorage |
| `fetchCurrentUser()` | GET /auth/me | Fetch user từ server |
| `isAuthenticated()` | - | Kiểm tra đăng nhập |
| `isAdmin()` | - | Kiểm tra quyền admin |
| `isModerator()` | - | Kiểm tra quyền moderator |
| `forgotPassword(email)` | POST /auth/forgot-password | Gửi email reset |
| `resetPassword(data)` | POST /auth/reset-password | Đặt lại mật khẩu |
| `changePassword(data)` | PUT /users/change-password | Đổi mật khẩu |
| `verifyEmail(token)` | GET /auth/verify-email | Xác thực email |

#### userService
[Nguồn: userService.ts]

| Function | Mô tả |
|----------|-------|
| `getProfile()` | Lấy profile user hiện tại |
| `getUserProfile(userId)` | Lấy profile user khác |
| `updateProfile(data)` | Cập nhật profile |
| `uploadAvatar(file)` | Upload avatar (max 5MB) |
| `deleteAvatar()` | Xóa avatar |

#### placeService
[Nguồn: placeService.ts]

| Function | API Endpoint | Mô tả |
|----------|--------------|-------|
| `getPlaces(params?)` | GET /places | Danh sách địa điểm |
| `getPlaceById(id)` | GET /places/:id | Chi tiết địa điểm |
| `getPlaceTypes()` | GET /places/place-types | Loại địa điểm |
| `getDistricts()` | GET /places/districts | Danh sách quận |
| `getNearbyPlaces(params)` | GET /places/nearby | Địa điểm gần đây |
| `searchPlaces(params)` | GET /places/search | Tìm kiếm địa điểm |
| `getSuggestions(keyword)` | GET /places/suggest | Gợi ý tìm kiếm |
| `toggleFavoritePlace(id)` | POST /places/:id/favorite | Toggle yêu thích |
| `removeFavoritePlace(id)` | DELETE /users/me/favorites/places/:id | Xóa yêu thích |
| `getFavoritePlaces()` | GET /users/me/favorites/places | DS yêu thích |

#### postService
[Nguồn: postService.ts]

| Function | API Endpoint | Mô tả |
|----------|--------------|-------|
| `getPosts(page?, limit?, sort?)` | GET /posts | Danh sách bài viết |
| `getPostById(id)` | GET /posts/:id | Chi tiết bài viết |
| `createPost(data)` | POST /posts | Tạo bài viết |
| `uploadPostImages(files)` | POST /upload?upload_type=post | Upload ảnh |
| `toggleLike(id)` | POST /posts/:id/like | Like/Unlike |
| `toggleFavoritePost(id)` | POST /posts/:id/favorite | Toggle yêu thích |
| `addComment(postId, content, images?)` | POST /posts/:id/comments | Thêm comment |
| `replyToComment(commentId, content, images?)` | POST /comments/:id/reply | Reply comment |
| `reportPost(postId, reason, description?)` | POST /posts/:id/report | Báo cáo bài viết |
| `reportComment(commentId, reason, description?)` | POST /comments/:id/report | Báo cáo comment |
| `deleteOwnPost(postId)` | DELETE /posts/:id | Xóa bài viết của mình |
| `deleteOwnComment(commentId)` | DELETE /comments/:id | Xóa comment của mình |

> [!IMPORTANT]
> `getPosts` hỗ trợ tham số `sort: 'newest' | 'popular'`

#### uploadService
[Nguồn: uploadService.ts]

| Function | API Endpoint | Mô tả |
|----------|--------------|-------|
| `uploadFiles(files, folder?)` | POST /upload?upload_type=generic | Upload tổng quát |
| `uploadPlaceImages(files, placeId)` | POST /upload?upload_type=place&entity_id={placeId} | Upload ảnh địa điểm |
| `uploadAvatar(file, userId?)` | POST /upload?upload_type=avatar&entity_id={userId\|current} | Upload avatar |
| `uploadPostImages(files, postId?)` | POST /upload?upload_type=post&entity_id={postId} | Upload ảnh bài viết |

> [!IMPORTANT]
> Backend API format: `POST /upload?upload_type={type}&entity_id={id}`

#### adminService
[Nguồn: adminService.ts]

| Function | API Endpoint | Mô tả |
|----------|--------------|-------|
| `login(credentials)` | POST /admin/login | Admin đăng nhập |
| `logout(refreshToken)` | POST /admin/logout | Admin đăng xuất |
| `getDashboardStats()` | GET /admin/dashboard | Thống kê dashboard |
| `getUsers(params?)` | GET /admin/users | Danh sách users |
| `deleteUser(id)` | DELETE /admin/users/:id | Xóa user |
| `banUser(id, reason)` | PATCH /admin/users/:id/ban | Ban user |
| `unbanUser(id)` | PATCH /admin/users/:id/unban | Unban user |
| `getPosts(params?)` | GET /admin/posts | Danh sách posts |
| `createPost(data)` | POST /admin/posts | Tạo bài viết |
| `updatePost(id, data)` | PUT /admin/posts/:id | Cập nhật bài viết |
| `deletePost(id, reason?)` | DELETE /admin/posts/:id | Xóa bài viết |
| `updatePostStatus(id, status, reason?)` | PATCH /admin/posts/:id/status | Duyệt/Từ chối |
| `getComments()` | GET /admin/comments | Danh sách comments |
| `deleteComment(id)` | DELETE /admin/comments/:id | Xóa comment |
| `getReports(params?)` | GET /admin/reports | Danh sách reports |
| `dismissReport(id)` | DELETE /admin/reports/:id | Dismiss report |
| `getPlaces(params?)` | GET /admin/places | Danh sách places |
| `createPlace(data)` | POST /admin/places | Tạo địa điểm |
| `updatePlace(id, data)` | PUT /admin/places/:id | Cập nhật địa điểm |
| `deletePlace(id)` | DELETE /admin/places/:id | Xóa địa điểm |
| `getAuditLogs(params?)` | GET /logs/audit | Audit logs |
| `getVisitAnalytics(days?)` | GET /logs/analytics | Thống kê truy cập |

### Utils

#### timeUtils
[Nguồn: timeUtils.ts]

| Function | Mô tả |
|----------|-------|
| `formatTimeAgo(isoString?)` | Chuyển timestamp thành "X phút/giờ/ngày trước" |

**Behavior:**
- `undefined` → "Vừa xong"
- Invalid date → "Không rõ"
- < 1 phút (bao gồm tương lai) → "Vừa xong"
- < 1 giờ → "X phút trước"
- < 1 ngày → "X giờ trước"
- < 7 ngày → "X ngày trước"
- ≥ 7 ngày → "dd/MM/yyyy"

## Route Protection & Error Handling

### ProtectedRoute
Yêu cầu user phải đăng nhập, nếu chưa sẽ redirect về `/login`

```tsx
<ProtectedRoute>
  <UserProfilePage />
</ProtectedRoute>
```

### AdminRoute
Yêu cầu user phải có quyền admin (role_id=1), nếu không sẽ redirect về `/`

```tsx
<AdminRoute>
  <AdminHomePage />
</AdminRoute>
```

### PublicRoute
Chỉ cho phép truy cập khi chưa đăng nhập, đã đăng nhập sẽ redirect về `/`

```tsx
<PublicRoute>
  <Login />
</PublicRoute>
```

### Error Handling
- **ErrorPage** - Trang lỗi (404, 500, etc.)
- **errorElement** - Cấu hình trong React Router
- Chi tiết lỗi hiển thị trong development mode

> [!NOTE]
> [Nguồn: routes/ProtectedRoute.tsx, routes/AdminRoute.tsx, routes/PublicRoute.tsx, pages/ErrorPage.tsx]

## Styling

- Global CSS trong `index.css`, `App.css`
- CSS variables trong `assets/styles/variables.css`
- Component styles trong `assets/styles/components/`
- Page styles trong `assets/styles/pages/`
- Responsive với media queries

## 📱 Responsive Design

- **Desktop**: Full layout
- **Tablet** (≤1024px): Adjusted spacing
- **Mobile** (≤768px): Mobile menu, stacked layout
- **Small Mobile** (≤480px): Optimized for small screens

## Testing

```bash
npm test                 # Watch mode
npm run test:run         # Single run
```

Test files: `src/frontend/services/__tests__/`

## Environment Variables

Tạo file `.env` trong thư mục `src/frontend/`:

```env
VITE_API_URL=http://127.0.0.1:8080/api/v1
```

**Lưu ý**:
- Variable name: `VITE_API_URL` (không phải `VITE_API_BASE_URL`)
- Default: `http://127.0.0.1:8080/api/v1`
- Không commit `.env` vào git

## 🔗 API Integration

- Base URL: `http://127.0.0.1:8080/api/v1`
- Authentication: JWT (access_token + refresh_token)
- Axios interceptors cho token refresh và error handling

## 📝 Code Style

- TypeScript strict mode
- ESLint configuration
- Functional components với hooks
- Custom hooks cho reusable logic

---

## Các thay đổi đã thực hiện (Change Log)

| Mục | Trạng thái cũ | Trạng thái mới | Nguồn |
|-----|---------------|----------------|-------|
| api/ folder | Thiếu index.ts | Thêm index.ts | Folder listing |
| services/ folder | Thiếu index.ts, __tests__ | Thêm cả hai | Folder listing |
| types/ folder | Thiếu index.ts | Thêm index.ts | Folder listing |
| hooks/ folder | Thiếu index.ts | Thêm index.ts | Folder listing |
| contexts/ folder | Không thay đổi | Verified | Folder listing |
| Client pages | Không đầy đủ danh sách | Liệt kê đủ 13 files | pages/client/ |
| Routes | Thiếu `/forgot-password`, `/reset-password` | Thêm đầy đủ | main.tsx |
| postService | Chỉ ghi "CRUD operations" | Chi tiết 13 functions | postService.ts |
| uploadService | Mô tả chung chung | Chi tiết endpoint format | uploadService.ts |
| adminService | Chỉ ghi "admin operations" | Chi tiết 22 functions | adminService.ts |
| placeService | Chỉ ghi "search, get" | Chi tiết 10 functions | placeService.ts |
| authService | Thiếu một số functions | Chi tiết 13 functions | authService.ts |
| userService | Thiếu chi tiết | Chi tiết 5 functions | userService.ts |
| timeUtils | Đã có mô tả cơ bản | Thêm behavior details | timeUtils.ts |
| Package versions | Sai một số version | Cập nhật đúng | package.json |

---

## Tài liệu thêm

- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org)
- [Vite Documentation](https://vite.dev)
- [React Router Documentation](https://reactrouter.com)

## Contributors

Hanoivivu Development Team
