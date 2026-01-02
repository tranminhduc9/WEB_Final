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
│   │   ├── Footer.tsx
│   │   ├── Chatbot.tsx    # AI Chatbot
│   │   ├── HeroCarousel.tsx
│   │   ├── PostCard.tsx
│   │   └── LocationCardHorizontal.tsx
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

## 🏃 Cách chạy

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

## 🎯 Tính năng chính

### Authentication & Authorization
- Đăng ký / Đăng nhập
- Quên mật khẩu / Đặt lại mật khẩu
- Protected routes (yêu cầu đăng nhập)
- Admin routes (yêu cầu quyền admin)
- JWT token management

### Pages

#### Client Pages
- **Homepage** (`/`) - Trang chủ với hero carousel
- **Search** (`/search`) - Tìm kiếm địa điểm
- **Places** (`/places`) - Danh sách địa điểm
- **Trend Places** (`/trend-places`) - Địa điểm phổ biến
- **Blogs** (`/blogs`) - Danh sách bài viết
- **Blog Detail** (`/blog/:id`) - Chi tiết bài viết
- **Location Info** (`/location/:id`) - Chi tiết địa điểm
- **User Profile** (`/profile`) - Hồ sơ người dùng
- **Favorite Places** (`/places/favourite`) - Địa điểm yêu thích
- **User Posts** (`/posts/user`) - Bài viết của user

#### Admin Pages
- **Admin Dashboard** (`/admin`) - Trang quản trị
- **Users Management** (`/admin/users`) - Quản lý người dùng
- **Locations Management** (`/admin/locations`) - Quản lý địa điểm
- **Posts Management** (`/admin/posts`) - Quản lý bài viết
- **Reports** (`/admin/reports`) - Quản lý báo cáo
- **Logs** (`/admin/log`) - Xem logs hệ thống

### Components

#### Header
- Responsive design với mobile menu
- Search bar với auto-scroll to top
- User menu dropdown
- Navigation links

#### Chatbot
- AI chatbot với Gemini integration
- Conversation history
- Reset chat functionality
- Suggested places

#### Common Components
- **LocationCard** - Card hiển thị địa điểm
- **BlogCard** - Card hiển thị bài viết
- **PostCard** - Card hiển thị post

### Services

- **authService** - Xử lý authentication
- **userService** - Quản lý user profile
- **placeService** - Tìm kiếm và quản lý địa điểm
- **postService** - Quản lý bài viết
- **chatbotService** - Tích hợp AI chatbot
- **adminService** - Admin operations
- **uploadService** - Upload files

## 🔐 Route Protection

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

## 🎨 Styling

- CSS modules cho từng component/page
- CSS variables trong `variables.css`
- Responsive design với media queries
- Mobile-first approach

## 📱 Responsive Design

- **Desktop**: Full layout với sidebar navigation
- **Tablet** (≤1024px): Adjusted spacing và font sizes
- **Mobile** (≤768px): Mobile menu, stacked layout
- **Small Mobile** (≤480px): Optimized for small screens

## 🧪 Testing

Tests được viết với Vitest và React Testing Library:

```bash
# Chạy tests
npm test

# Test files location
src/frontend/services/__tests__/
```

## 📦 Build & Deploy

### Build output
Sau khi build, files sẽ được output vào thư mục `dist/`

### Environment Variables
Tạo file `.env` trong thư mục `src/frontend/`:

```env
VITE_API_BASE_URL=http://localhost:8080/api/v1
```

## 🔗 API Integration

Frontend giao tiếp với backend qua REST API:

- Base URL: `http://localhost:8080/api/v1`
- Authentication: JWT tokens
- Axios interceptors cho token refresh
- Error handling với try-catch

## 📝 Code Style

- TypeScript strict mode
- ESLint configuration
- Functional components với hooks
- Custom hooks cho reusable logic
- Type-safe API calls

## 🚀 Performance

### Tự động (Vite mặc định)
- ✅ **CSS optimization** - Vite tự động minify và optimize CSS khi build
- ✅ **Tree shaking** - Vite tự động loại bỏ code không sử dụng với ES modules
- ✅ **Code minification** - Tự động minify JavaScript và CSS



### Lưu ý
- Build warning: Một số chunks lớn hơn 500KB
- Khuyến nghị: Sử dụng lazy loading cho admin pages để giảm bundle size ban đầu

## 📚 Tài liệu thêm

- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org)
- [Vite Documentation](https://vite.dev)
- [React Router Documentation](https://reactrouter.com)

## 👥 Contributors

Hanoivivu Development Team
