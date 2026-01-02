# Hanoivivu Frontend

Frontend application cho hệ thống du lịch Hà Nội, được xây dựng với React, TypeScript và Vite.

## Công nghệ sử dụng

- **React 19.1.1** - UI Framework
- **TypeScript** - Type safety
- **Vite 7.1.7** - Build tool và dev server
- **React Router 7.9.4** - Client-side routing
- **Axios** - HTTP client
- **React Markdown** - Render markdown content
- **Vitest** - Testing framework

## 📁 Cấu trúc thư mục

```
src/frontend/
├── api/                    # API client configuration
│   ├── axiosClient.ts     # Axios instance với interceptors
│   ├── authApi.ts         # Auth API endpoints
│   ├── userApi.ts         # User API endpoints
│   └── adminApi.ts        # Admin API endpoints
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
│   │   ├── LocationCardHorizontal.tsx # Horizontal location card
│   │   └── CreatePostModal.tsx # Modal để tạo post mới
│   └── common/            # Shared components
│       ├── LocationCard.tsx
│       └── BlogCard.tsx
│
├── config/                 # Configuration
│   └── constants.tsx      # App constants và icons
│
├── contexts/               # React Contexts
│   ├── AuthContext.tsx    # Authentication context
│   └── index.ts
│
├── hooks/                  # Custom React hooks
│   ├── useAuth.ts
│   ├── useUser.ts
│   └── useScrollToTop.ts
│
├── pages/                  # Page components
│   ├── admin/             # Admin pages
│   │   ├── AdminHomePage.tsx
│   │   ├── AdminUsersPage.tsx
│   │   ├── AdminLocationsPage.tsx
│   │   ├── AdminPostsPage.tsx
│   │   ├── AdminReportsPage.tsx
│   │   ├── AdminLogPage.tsx
│   │   ├── AdminAddPlacePage.tsx
│   │   └── AdminEditPlacePage.tsx
│   └── client/            # Client pages
│       ├── Login.tsx
│       ├── Register.tsx
│       ├── PlacesPage.tsx
│       ├── BlogPage.tsx
│       ├── SearchResultsPage.tsx
│       ├── UserProfilePage.tsx
│       └── ...
│
├── routes/                 # Route guards
│   ├── ProtectedRoute.tsx # Yêu cầu authentication
│   ├── AdminRoute.tsx     # Yêu cầu admin role
│   ├── PublicRoute.tsx    # Public routes
│   └── index.ts
│
├── services/               # Business logic & API services
│   ├── authService.ts     # Authentication service
│   ├── userService.ts     # User service
│   ├── placeService.ts    # Place service
│   ├── postService.ts     # Post service
│   ├── chatbotService.ts # Chatbot service
│   ├── adminService.ts    # Admin service
│   └── uploadService.ts   # File upload service
│
├── types/                  # TypeScript type definitions
│   ├── auth.ts            # Auth types
│   ├── user.ts            # User types
│   ├── models.ts          # Data models
│   ├── admin.ts           # Admin types
│   └── common.ts          # Common types
│
├── test/                   # Test utilities
│   └── setup.ts           # Test setup
│
├── App.tsx                 # Root component
├── main.tsx                # Entry point
└── vite.config.ts          # Vite configuration
```

##  Cách chạy

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

##  Tính năng chính

### Authentication & Authorization
- **Đăng ký / Đăng nhập** - Form validation, error handling
- **Quên mật khẩu / Đặt lại mật khẩu** - Email link-based password reset flow (gửi link reset qua email)
- **Protected routes** - Yêu cầu đăng nhập, tự động redirect về `/login`
- **Admin routes** - Yêu cầu quyền admin, redirect nếu không đủ quyền
- **JWT token management** - Tự động refresh token, lưu trong localStorage
- **Auto-logout** - Tự động đăng xuất khi token hết hạn

### Pages

#### Client Pages
- **Homepage** (`/`) - Trang chủ với hero carousel và search bar
- **Search** (`/search`) - Tìm kiếm địa điểm với filters, auto-scroll to top
- **Places** (`/places`) - Danh sách địa điểm với pagination
- **Trend Places** (`/trend-places`) - Địa điểm phổ biến
- **Blogs** (`/blogs`) - Danh sách bài viết
- **Blog Detail** (`/blog/:id`) - Chi tiết bài viết
- **Location Info** (`/location/:id`) - Chi tiết địa điểm với nearby places và suggestions
- **User Profile** (`/profile`) - Hồ sơ người dùng (protected), có thể xem profile người khác (`/user/:id`)
- **Favorite Places** (`/places/favourite`) - Địa điểm yêu thích (protected), có thể xem của người khác (`/places/favourite/:userId`)
- **User Posts** (`/posts/user`) - Bài viết của user (protected), có thể xem của người khác (`/posts/user/:userId`)

#### Admin Pages
- **Admin Dashboard** (`/admin`) - Trang quản trị với thống kê
- **Users Management** (`/admin/users`) - Quản lý người dùng (CRUD)
- **Locations Management** (`/admin/locations`) - Quản lý địa điểm
  - **Add Location** (`/admin/locations/add`) - Thêm địa điểm mới
  - **Edit Location** (`/admin/locations/edit/:id`) - Chỉnh sửa địa điểm
- **Posts Management** (`/admin/posts`) - Quản lý bài viết
- **Reports** (`/admin/reports`) - Quản lý báo cáo
- **Logs** (`/admin/log`) - Xem logs hệ thống (audit logs, application logs, visit logs)

### Components

#### Header
- Responsive design với mobile menu (hamburger icon)
- Search bar với auto-scroll to top khi submit
- User menu dropdown với avatar
- Navigation links (ẩn trên mobile, hiện trong mobile menu)
- Click outside để đóng menu

#### Chatbot
- AI chatbot tích hợp Google Gemini
- Conversation history lưu trong localStorage (15 phút expiry)
- Reset chat functionality (xóa toàn bộ lịch sử)
- Suggested places từ AI response
- Markdown rendering cho bot messages
- User avatar hiển thị trong chat
- Loading indicator khi đang xử lý
- Auto-scroll to bottom khi có tin nhắn mới

#### Common Components
- **LocationCard** - Card hiển thị địa điểm (vertical layout, dùng trong danh sách)
- **BlogCard** - Card hiển thị bài viết

#### Client Components
- **LocationCardHorizontal** - Card hiển thị địa điểm (horizontal layout, dùng trong sidebar của LocationInfoPage)
- **CreatePostModal** - Modal component để tạo bài viết mới với image upload
- **Footer** - Footer component cho các pages
- **HeroCarousel** - Carousel component cho homepage với search bar tích hợp
- **PostCard** - Card hiển thị bài viết (có thể khác với BlogCard)

### Services

- **authService** - Xử lý authentication (login, register, logout, refresh token, forgot/reset password)
- **userService** - Quản lý user profile (fetch, update, upload avatar, delete avatar)
- **placeService** - Tìm kiếm và quản lý địa điểm (search, get details, get nearby, get favorites)
- **postService** - Quản lý bài viết (CRUD operations, get user posts)
- **chatbotService** - Tích hợp AI chatbot (send message, get conversation history)
- **adminService** - Admin operations (users, locations, posts, reports, logs management)
- **uploadService** - Upload files (images, avatars) lên server với folder organization

##  Route Protection

### ProtectedRoute
Yêu cầu user phải đăng nhập, nếu chưa sẽ redirect về `/login`

```tsx
<ProtectedRoute>
  <UserProfilePage />
</ProtectedRoute>
```

### AdminRoute
Yêu cầu user phải có quyền admin, nếu không sẽ redirect về `/`

```tsx
<AdminRoute>
  <AdminHomePage />
</AdminRoute>
```

### PublicRoute
Chỉ cho phép truy cập khi chưa đăng nhập, nếu đã đăng nhập sẽ redirect về `/`

```tsx
<PublicRoute>
  <Login />
</PublicRoute>
```

##  Styling

- Global CSS files cho từng component/page
- CSS variables trong `variables.css`
- Responsive design với media queries

## 📱 Responsive Design

- **Desktop**: Full layout với horizontal navigation
- **Tablet** (≤1024px): Adjusted spacing và font sizes
- **Mobile** (≤768px): Mobile menu, stacked layout
- **Small Mobile** (≤480px): Optimized for small screens

**Lưu ý**: Một số pages như `LocationInfoPage` có sidebar sections (địa điểm lân cận, gợi ý) nhưng không có global sidebar navigation.

## Testing

Tests được viết với Vitest và React Testing Library:

```bash
# Chạy tests
npm test

# Test files location
src/frontend/services/__tests__/
```

## Build & Deploy

### Build Production

```bash
npm run build
```

Sau khi build, files sẽ được output vào thư mục `dist/`:
- `dist/index.html` - Entry point
- `dist/assets/` - JavaScript, CSS, và images đã được optimize

### Preview Production Build

```bash
npm run preview
```

Chạy local server để preview production build trước khi deploy.

### Environment Variables

Tạo file `.env` trong thư mục root của frontend project (`src/frontend/`):

```env
VITE_API_URL=http://127.0.0.1:8080/api/v1
```

**Lưu ý**: 
- Environment variable là `VITE_API_URL` (không phải `VITE_API_BASE_URL`)
- Default value là `http://127.0.0.1:8080/api/v1` (nếu không set `VITE_API_URL`)
- File `.env` sẽ được Vite tự động load khi chạy `npm run dev` hoặc `npm run build`
- Không commit file `.env` vào git (đã có trong `.gitignore`)

### Deploy

#### Static Hosting (Vercel, Netlify, GitHub Pages)

1. **Build project**:
   ```bash
   npm run build
   ```

2. **Deploy folder `dist/`** lên hosting service của bạn

3. **Set environment variables** trên hosting platform:
   - `VITE_API_URL`: URL của backend API

#### Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

#### Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

#### Manual Deploy (Nginx, Apache)

1. Build project: `npm run build`
2. Copy folder `dist/` lên server
3. Configure web server (Nginx/Apache) để serve static files từ `dist/`
4. Set environment variables trên server hoặc trong build process

## 🔗 API Integration

Frontend giao tiếp với backend qua REST API:

- Base URL: `http://127.0.0.1:8080/api/v1` (default, có thể config qua `VITE_API_URL`)
- Authentication: JWT tokens
- Axios interceptors cho token refresh
- Error handling: Axios interceptors xử lý HTTP errors, try-catch ở component level

## 📝 Code Style

- TypeScript strict mode
- ESLint configuration
- Functional components với hooks
- Custom hooks cho reusable logic
- Type-safe API calls

## Performance

### Tự động (Vite mặc định)
- ✅ **CSS optimization** - Vite tự động minify và optimize CSS khi build
- ✅ **Tree shaking** - Vite tự động loại bỏ code không sử dụng với ES modules
- ✅ **Code minification** - Tự động minify JavaScript và CSS





## Tài liệu thêm

- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org)
- [Vite Documentation](https://vite.dev)
- [React Router Documentation](https://reactrouter.com)

## Contributors

Hanoivivu Development Team
