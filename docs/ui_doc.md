# Tài liệu Mô tả Giao diện (UI Documentation)

> **Dự án:** WEB_Final  
> **Ngày tạo:** 2026-01-03  
> **Phiên bản:** 1.0

---

# PHẦN 1: CLIENT PAGES - AUTHENTICATION

---

## 1. Login (Đăng nhập)

**File:** `src/frontend/pages/client/Login.tsx`

### 1.1 Tổng quan
Module này cung cấp giao diện đăng nhập cho người dùng. Cho phép người dùng nhập thông tin tài khoản (email và mật khẩu) để xác thực và truy cập vào hệ thống.

### 1.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Logo | Image + Link | Logo ứng dụng, click để quay về trang chủ (`/`) |
| Tiêu đề | Heading (h2) | Text: "ĐĂNG NHẬP TÀI KHOẢN" |
| Email Input | Input (type="email") | Placeholder: "example@email.com", có autocomplete="email" |
| Password Input | Input (type="password") | Placeholder: "••••••••", có autocomplete="current-password" |
| Error Message | Div | Hiển thị thông báo lỗi (class: `error-message`) |
| Login Button | Button (submit) | Text mặc định: "Đăng nhập" |
| Forgot Password Link | Link | Text: "Quên mật khẩu?" → điều hướng đến `/forgot-password` |
| Register Link | Link | Text: "Chưa có tài khoản? Đăng ký ngay" → điều hướng đến `/register` |
| Hình minh họa | Image | Ảnh trang trí bên phải form (file: `login-register-image.png`) |

### 1.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `email` | string | Giá trị email người dùng nhập |
| `password` | string | Giá trị mật khẩu người dùng nhập |
| `localError` | string \| null | Lỗi validation cục bộ |
| `error` | string (từ AuthContext) | Lỗi từ API/server |
| `isLoading` | boolean (từ AuthContext) | Trạng thái đang xử lý đăng nhập |
| `isAuthenticated` | boolean (từ AuthContext) | Trạng thái đã đăng nhập thành công |

**Trạng thái Button:**
- **Disabled:** Khi `isLoading = true`
- **Text thay đổi:** 
  - Loading: "Đang đăng nhập..."
  - Mặc định: "Đăng nhập"

**Trạng thái Input:**
- **Disabled:** Khi `isLoading = true`

### 1.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Nhập Email | `onChange` | Cập nhật state `email`, xóa error nếu có |
| Nhập Password | `onChange` | Cập nhật state `password`, xóa error nếu có |
| Submit Form | `onSubmit` | Gọi hàm `onSubmit()` → validate → gọi `login()` từ AuthContext |
| Click Logo | Click | Điều hướng về trang chủ `/` |
| Click "Quên mật khẩu?" | Click | Điều hướng đến `/forgot-password` |
| Click "Đăng ký ngay" | Click | Điều hướng đến `/register` |

### 1.5 Validation (Kiểm tra dữ liệu)

| Điều kiện | Thông báo lỗi |
|-----------|---------------|
| Email trống | "Vui lòng nhập email" |
| Password trống | "Vui lòng nhập mật khẩu" |
| Email không đúng định dạng | "Email không hợp lệ" |

**Regex kiểm tra email:** `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`

### 1.6 Điều hướng (Navigation)

- **Sau đăng nhập thành công:** Redirect đến URL được lưu trong `location.state.from` (nếu có), mặc định là `/`
- **Điều hướng tự động:** Sử dụng `useEffect` để theo dõi `isAuthenticated`, khi = true thì tự động redirect

### 1.7 Dữ liệu hiển thị

Module này không hiển thị dữ liệu từ API, chỉ thu thập thông tin đầu vào từ người dùng.

---

## 2. Register (Đăng ký)

**File:** `src/frontend/pages/client/Register.tsx`

### 2.1 Tổng quan
Module này cung cấp giao diện đăng ký tài khoản mới cho người dùng. Sau khi đăng ký thành công, hiển thị thông báo và tự động chuyển đến trang đăng nhập.

### 2.2 Thành phần giao diện (UI Components)

#### Trạng thái Form (success = false):

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Logo | Image + Link | Logo ứng dụng, click để quay về trang chủ (`/`) |
| Tiêu đề | Heading (h2) | Text: "ĐĂNG KÝ TÀI KHOẢN" |
| Email Input | Input (type="email") | Placeholder: "example@email.com", Label: "Email *" |
| Name Input | Input (type="text") | Placeholder: "Nguyễn Văn A", Label: "Họ và tên *" |
| Password Input | Input (type="password") | Placeholder: "Tối thiểu 6 ký tự", Label: "Mật khẩu *" |
| Confirm Password Input | Input (type="password") | Placeholder: "Nhập lại mật khẩu", Label: "Xác nhận mật khẩu *" |
| Error Message | Div | Hiển thị thông báo lỗi (class: `error-message`) |
| Register Button | Button (submit) | Text mặc định: "Đăng ký" |
| Login Link | Link | Text: "Đã có tài khoản? Đăng nhập" → điều hướng đến `/login` |
| Hình minh họa | Image | Ảnh trang trí bên phải form |

#### Trạng thái Thành công (success = true):

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Tiêu đề | Heading (h2) | Text: "ĐĂNG KÝ THÀNH CÔNG!" |
| Logo | Image + Link | Logo ứng dụng |
| Success Message | Paragraph | Text: "Tài khoản của bạn đã được tạo thành công." (màu #4CAF50) |
| Redirect Notice | Paragraph | Text: "Đang chuyển hướng đến trang đăng nhập..." |

### 2.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `email` | string | Giá trị email |
| `name` | string | Giá trị họ tên |
| `password` | string | Giá trị mật khẩu |
| `confirmPassword` | string | Giá trị xác nhận mật khẩu |
| `localError` | string | Lỗi validation cục bộ |
| `isSubmitting` | boolean | Đang gửi request |
| `success` | boolean | Đăng ký thành công |
| `error` | string (từ AuthContext) | Lỗi từ API/server |
| `isLoading` | boolean (từ AuthContext) | Trạng thái loading từ context |

**Trạng thái Button:**
- **Disabled:** Khi `isLoading = true` HOẶC `isSubmitting = true`
- **Text thay đổi:** 
  - Loading: "Đang đăng ký..."
  - Mặc định: "Đăng ký"

### 2.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Nhập các field | `onChange` | Cập nhật state tương ứng, xóa error nếu có |
| Submit Form | `onSubmit` | Validate → Gọi `register()` từ AuthContext → Set `success = true` nếu thành công |
| Đăng ký thành công | Tự động | Sau 2 giây, redirect đến `/login` với message |

### 2.5 Validation (Kiểm tra dữ liệu)

| Điều kiện | Thông báo lỗi |
|-----------|---------------|
| Email trống | "Vui lòng nhập email" |
| Họ tên trống | "Vui lòng nhập họ và tên" |
| Password trống | "Vui lòng nhập mật khẩu" |
| Confirm Password trống | "Vui lòng xác nhận mật khẩu" |
| Email không đúng định dạng | "Email không hợp lệ" |
| Password < 6 ký tự | "Mật khẩu phải có ít nhất 6 ký tự" |
| Password không khớp | "Mật khẩu xác nhận không khớp" |

### 2.6 Điều hướng (Navigation)

- **Sau đăng ký thành công:** Sau 2 giây tự động redirect đến `/login` kèm message: "Đăng ký thành công! Vui lòng đăng nhập."

### 2.7 Dữ liệu gửi đi

```typescript
{
  email: string,      // Email đã trim
  password: string,   // Mật khẩu
  full_name: string   // Họ tên đã trim
}
```

---

## 3. ForgotPassword (Quên mật khẩu)

**File:** `src/frontend/pages/client/ForgotPassword.tsx`

### 3.1 Tổng quan
Module này cho phép người dùng yêu cầu link đặt lại mật khẩu qua email. Sau khi gửi thành công, hiển thị thông báo xác nhận.

### 3.2 Thành phần giao diện (UI Components)

#### Trạng thái Form (success = false):

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Logo | Image + Link | Logo ứng dụng, click để quay về trang chủ (`/`) |
| Tiêu đề | Heading (h2) | Text: "QUÊN MẬT KHẨU" |
| Email Input | Input (type="email") | Placeholder: "example@email.com", Label: "E-mail đăng nhập" |
| Error Message | Div | Hiển thị thông báo lỗi |
| Submit Button | Button (submit) | Text mặc định: "Quên mật khẩu" |
| Back to Login Link | Link | Text: "← Quay lại đăng nhập" → điều hướng đến `/login` |
| Hình minh họa | Image | Ảnh trang trí bên phải form |

#### Trạng thái Thành công (success = true):

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Success Message | Div | Thông báo: "Chúng tôi đã gửi email hướng dẫn đặt lại mật khẩu đến: [email]. Vui lòng kiểm tra hộp thư của bạn." |
| Back Button | Button | Text: "Quay lại đăng nhập" → click để navigate về `/login` |

### 3.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `email` | string | Email người dùng nhập |
| `isLoading` | boolean | Đang gửi request |
| `error` | string \| null | Thông báo lỗi |
| `success` | boolean | Gửi email thành công |

**Trạng thái Button:**
- **Disabled:** Khi `isLoading = true`
- **Text thay đổi:**
  - Loading: "Đang xử lý..."
  - Mặc định: "Quên mật khẩu"

### 3.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Nhập Email | `onChange` | Cập nhật state `email`, xóa error nếu có |
| Submit Form | `onSubmit` | Validate → Gọi `authService.forgotPassword(email)` |
| Click "Quay lại đăng nhập" (form) | Click | Điều hướng đến `/login` |
| Click "Quay lại đăng nhập" (success) | Click | Điều hướng đến `/login` |

### 3.5 Validation (Kiểm tra dữ liệu)

| Điều kiện | Thông báo lỗi |
|-----------|---------------|
| Email trống | "Vui lòng nhập email" |
| Email không đúng định dạng | "Email không hợp lệ" |

### 3.6 API Service

- **Hàm gọi:** `authService.forgotPassword(email.trim())`
- **Lỗi mặc định:** "Có lỗi xảy ra. Vui lòng thử lại."

---

## 4. ResetPassword (Đổi mật khẩu)

**File:** `src/frontend/pages/client/ResetPassword.tsx`

### 4.1 Tổng quan
Module này cho phép người dùng đặt mật khẩu mới thông qua link được gửi qua email. Yêu cầu token và email từ URL params để xác thực.

### 4.2 Thành phần giao diện (UI Components)

#### Trạng thái Token không hợp lệ (tokenValid = false):

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Logo | Image + Link | Logo ứng dụng |
| Tiêu đề | Heading (h2) | Text: "ĐỔI MẬT KHẨU" |
| Error Message | Div | Text: "Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn." |
| Request New Link | Link (styled as button) | Text: "Yêu cầu link mới" → điều hướng đến `/forgot-password` |

#### Trạng thái Form (tokenValid = true, success = false):

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Logo | Image + Link | Logo ứng dụng |
| Tiêu đề | Heading (h2) | Text: "ĐỔI MẬT KHẨU" |
| New Password Input | Input (type="password") | Placeholder: "••••••••", Label: "Mật khẩu mới" |
| Confirm Password Input | Input (type="password") | Placeholder: "••••••••", Label: "Xác nhận mật khẩu" |
| Error Message | Div | Hiển thị thông báo lỗi |
| Submit Button | Button (submit) | Text mặc định: "Đổi mật khẩu" |
| Back to Login Link | Link | Text: "← Quay lại đăng nhập" |

#### Trạng thái Thành công (success = true):

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Success Message | Div | Text: "Mật khẩu của bạn đã được đổi thành công! Bạn có thể đăng nhập với mật khẩu mới." |
| Login Button | Button | Text: "Đăng nhập ngay" → click để navigate về `/login` |

### 4.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `newPassword` | string | Mật khẩu mới |
| `confirmPassword` | string | Xác nhận mật khẩu |
| `isLoading` | boolean | Đang gửi request |
| `error` | string \| null | Thông báo lỗi |
| `success` | boolean | Đổi mật khẩu thành công |
| `tokenValid` | boolean | Token từ URL có hợp lệ không |

**URL Params (từ useSearchParams):**
- `token`: Token xác thực
- `email`: Email của người dùng

### 4.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Load trang | `useEffect` | Kiểm tra `token` và `email` từ URL, nếu thiếu thì set `tokenValid = false` |
| Nhập mật khẩu mới | `onChange` | Cập nhật state `newPassword`, xóa error nếu có |
| Nhập xác nhận mật khẩu | `onChange` | Cập nhật state `confirmPassword`, xóa error nếu có |
| Submit Form | `onSubmit` | Validate → Gọi `authService.resetPassword()` |
| Click "Đăng nhập ngay" | Click | Điều hướng đến `/login` |

### 4.5 Validation (Kiểm tra dữ liệu)

| Điều kiện | Thông báo lỗi |
|-----------|---------------|
| Mật khẩu mới trống | "Vui lòng nhập mật khẩu mới" |
| Mật khẩu < 6 ký tự | "Mật khẩu phải có ít nhất 6 ký tự" |
| Xác nhận mật khẩu trống | "Vui lòng xác nhận mật khẩu" |
| Mật khẩu không khớp | "Mật khẩu xác nhận không khớp" |
| Token/Email không có trong URL | "Link đặt lại mật khẩu không hợp lệ" |

### 4.6 API Service

- **Hàm gọi:** `authService.resetPassword({ email, token, new_password })`
- **Dữ liệu gửi đi:**
```typescript
{
  email: string,        // Từ URL params
  token: string,        // Từ URL params
  new_password: string  // Mật khẩu mới người dùng nhập
}
```

---

# PHẦN 2: CLIENT PAGES - BLOG + COMPONENTS

---

## 5. BlogPage (Trang Blog/Newfeed)

**File:** `src/frontend/pages/client/BlogPage.tsx`

### 5.1 Tổng quan
Module này hiển thị danh sách các bài viết (newfeed) của người dùng, cho phép tạo bài viết mới và phân trang. Bài viết được sắp xếp theo thời gian mới nhất.

### 5.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Header | Component | Header chung của client |
| Footer | Component | Footer chung của client |
| Page Title | Heading (h1) | Text: "Chia sẻ trải nghiệm" |
| Input Box (Trigger) | Div (clickable) | Text: "Hãy chia sẻ trải nghiệm của bạn!!" - Click để mở modal tạo bài |
| CreatePostModal | Modal Component | Modal để tạo bài viết mới |
| Section Title | Heading (h2) | Text: "Newfeed" |
| Loading Spinner | Div | Hiển thị khi đang tải bài viết |
| BlogCard List | Component List | Danh sách các BlogCard hiển thị bài viết |
| Pagination | Div | Phân trang với nút «, số trang, và » |

### 5.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `currentPage` | number | Trang hiện tại (mặc định: 1) |
| `isModalOpen` | boolean | Trạng thái modal tạo bài viết |
| `posts` | PostDetail[] | Danh sách bài viết từ API |
| `pagination` | Pagination \| null | Thông tin phân trang từ API |
| `isLoading` | boolean | Đang tải dữ liệu |

**Cấu hình:**
- `itemsPerPage`: 10 bài/trang

### 5.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Click Input Box | `onClick` | Mở `CreatePostModal` (`setIsModalOpen(true)`) |
| Đóng Modal | `onClose` | Đóng modal (`setIsModalOpen(false)`) |
| Submit bài viết | `onSubmit` | Gọi `handleCreatePost()` → Upload ảnh → Tạo bài → Refresh danh sách |
| Click số trang | `onClick` | Gọi `handlePageChange(page)` → Scroll lên đầu trang |
| Click « | `onClick` | Chuyển về trang trước |
| Click » | `onClick` | Chuyển sang trang sau |

### 5.5 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchPosts()` | `postService.getPosts(currentPage, itemsPerPage, 'newest')` | Lấy danh sách bài viết |
| `handleCreatePost()` | `postService.uploadPostImages()` + `postService.createPost()` | Upload ảnh và tạo bài mới |

### 5.6 Dữ liệu hiển thị (mapPostToCard)

Chuyển đổi `PostDetail` sang props của `BlogCard`:

```typescript
{
  id: post._id,
  authorId: post.author?.id,
  avatarSrc: post.author?.avatar_url || defaultAvatar,
  username: post.author?.full_name || 'Người dùng',
  timeAgo: formatTimeAgo(post.created_at),
  location: post.related_place?.name || 'Hà Nội',
  rating: post.rating || 0,
  imageSrc1: post.images?.[0] || placeholderImage,
  imageSrc2: post.images?.[1] || post.images?.[0] || placeholderImage,
  likeCount: post.likes_count || 0,
  commentCount: post.comments_count || 0,
  description: post.content?.slice(0, 150) || '',
  isLiked: post.is_liked || false,
  isBanned: post.author?.is_banned
}
```

### 5.7 Logic Phân trang

- Hiển thị tối đa 5 số trang
- Nếu > 5 trang: hiển thị dạng `1 ... 3 4 5 ... 10`
- Nút « disabled khi `currentPage === 1`
- Nút » disabled khi `currentPage === totalPages`

---

## 6. BlogDetailPage (Trang Chi tiết Bài viết)

**File:** `src/frontend/pages/client/BlogDetailPage.tsx`

### 6.1 Tổng quan
Module này hiển thị chi tiết một bài viết, bao gồm nội dung, hình ảnh (carousel), tương tác (like, comment), báo cáo, và quản lý bình luận.

### 6.2 Thành phần giao diện (UI Components)

#### Trạng thái Loading:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Loading Spinner | Div | Text: "Đang tải bài viết..." |

#### Trạng thái Error:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Error Message | Heading (h2) | Text: "😕 [error message]" |
| Back Link | Link | Text: "← Quay lại danh sách bài viết" → `/blogs` |

#### Trạng thái Thành công - Post Section:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Rating Badge | Div | Hiển thị rating dạng "[rating]/5" (nếu có) |
| Delete Button | Button | Hiển thị cho chủ bài viết - Text: "Xóa bài viết" |
| Report Button | Div | Hiển thị cho người khác - Text: "Báo cáo" |
| User Info | Link | Avatar + Username + TimeAgo → Link đến profile `/user/{id}` |
| Location | Link | Icon + Tên địa điểm → Link đến `/location/{id}` |
| Image Carousel | Div | Carousel ảnh với nút prev/next và dots indicator |
| Actions | Div | Nút Like (với số lượng) + Comment count |
| Description | Paragraph | Nội dung bài viết đầy đủ |

#### Comments Section:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Comments Title | Heading (h2) | Text: "Bình luận" |
| Comment Input | Textarea + Button | Cho người dùng đã đăng nhập nhập bình luận |
| Login Prompt | Div | Text: "Đăng nhập để bình luận" cho guest |
| Comments List | Div | Danh sách bình luận với replies |
| No Comments | Paragraph | Text: "Chưa có bình luận nào. Hãy là người đầu tiên!" |

#### Report Modal:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Modal Title | Heading (h3) | Text: "Báo cáo [bài viết/bình luận]" |
| Reason Select | Select | Options: Spam, Quấy rối, Nội dung không phù hợp, Thông tin sai lệch, Khác |
| Cancel Button | Button | Text: "Hủy" |
| Submit Button | Button | Text: "Gửi báo cáo" |

### 6.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `post` | PostDetail \| null | Dữ liệu bài viết |
| `isLoading` | boolean | Đang tải bài viết |
| `error` | string \| null | Lỗi khi tải |
| `isLiked` | boolean | Trạng thái đã like |
| `likesCount` | number | Số lượng likes |
| `isLiking` | boolean | Đang xử lý like |
| `newComment` | string | Nội dung bình luận mới |
| `replyingTo` | string \| null | ID comment đang reply |
| `replyContent` | string | Nội dung reply |
| `isSubmitting` | boolean | Đang gửi comment/reply |
| `deletingCommentId` | string \| null | ID comment đang xóa |
| `showReportModal` | boolean | Hiển thị modal báo cáo |
| `reportTarget` | { type, id } \| null | Đối tượng đang báo cáo |
| `reportReason` | string | Lý do báo cáo |
| `isReporting` | boolean | Đang gửi báo cáo |
| `currentImageSlide` | number | Index ảnh hiện tại trong carousel |
| `isDeletingPost` | boolean | Đang xóa bài viết |

### 6.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Load trang | `useEffect` | Gọi `fetchPost()` |
| Click Like | `onClick` | Gọi `handleLike()` → `postService.toggleLike()` |
| Gửi Comment | `onClick` | Gọi `handleAddComment()` → `postService.addComment()` |
| Trả lời Comment | Click "Trả lời" | Mở reply input, gọi `handleReply()` |
| Xóa Comment (owner) | Click "Xóa" | Confirm → `postService.deleteOwnComment()` |
| Báo cáo | Click "Báo cáo" | Mở modal → Chọn lý do → `postService.reportPost/Comment()` |
| Xóa bài (owner) | Click "Xóa bài viết" | Confirm → `postService.deleteOwnPost()` → Navigate `/blogs` |
| Carousel Prev | Click ‹ | `setCurrentImageSlide(prev - 1)` (wrap around) |
| Carousel Next | Click › | `setCurrentImageSlide(prev + 1)` (wrap around) |
| Carousel Dot | Click dot | `setCurrentImageSlide(index)` |

### 6.5 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchPost()` | `postService.getPostById(id)` | Lấy chi tiết bài viết |
| `handleLike()` | `postService.toggleLike(id)` | Toggle like bài viết |
| `handleAddComment()` | `postService.addComment(id, content)` | Thêm bình luận |
| `handleReply()` | `postService.replyToComment(commentId, content)` | Trả lời bình luận |
| `handleDeleteComment()` | `postService.deleteOwnComment(commentId)` | Xóa bình luận của mình |
| `handleDeletePost()` | `postService.deleteOwnPost(id)` | Xóa bài viết của mình |
| `handleReport()` | `postService.reportPost/Comment()` | Báo cáo bài viết/bình luận |

### 6.6 Điều hướng

- **Click avatar/username:** Navigate đến `/user/{authorId}`
- **Click địa điểm:** Navigate đến `/location/{placeId}`
- **Sau xóa bài:** Navigate đến `/blogs`
- **Back link (error):** Navigate đến `/blogs`

---

## 7. BlogCard (Component hiển thị bài viết dạng card)

**File:** `src/frontend/components/common/BlogCard.tsx`

### 7.1 Tổng quan
Component hiển thị tóm tắt một bài viết dưới dạng card, bao gồm thông tin tác giả, hình ảnh, rating, like/comment count, và các action buttons.

### 7.2 Props Interface

```typescript
interface BlogCardProps {
  id: string | number;
  authorId?: number;
  avatarSrc: string;
  username: string;
  timeAgo: string;
  location: string;
  rating: number;
  imageSrc1: string;
  imageSrc2: string;
  likeCount: number;
  commentCount: number;
  description: string;
  isLiked?: boolean;
  onDeleted?: () => void;
  onLikeChanged?: (isLiked: boolean, newCount: number) => void;
  isBanned?: boolean;
}
```

### 7.3 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Card Container | Div | Clickable, navigate đến `/blog/{id}` |
| Avatar | Image | Ảnh đại diện tác giả (clickable nếu có authorId) |
| Username | Span | Tên + TimeAgo, có style `--banned` nếu bị ban |
| Location | Div | Icon Location + Tên địa điểm |
| Rating Badge | Div | Hiển thị "[rating]/5" |
| Delete Button | Button | Cho owner - Icon Trash |
| Report Button | Button | Cho người khác - Icon Flag |
| Images | Div | 2 hình ảnh song song |
| Like Button | Button | Icon Heart + count, có class `--liked` khi đã like |
| Comment Count | Div | Icon Comment + count |
| Description | Paragraph | Nội dung truncated + "xem toàn bộ bài viết..." |

#### Report Modal (trong component):
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Modal Title | Heading (h3) | Text: "Báo cáo bài viết" |
| Reason Textarea | Textarea | Placeholder: "Nhập lý do báo cáo..." |
| Cancel/Submit Buttons | Buttons | Hủy và Gửi báo cáo |

### 7.4 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `isDeleting` | boolean | Đang xóa bài viết |
| `showReportModal` | boolean | Hiển thị modal báo cáo |
| `reportReason` | string | Lý do báo cáo |
| `isReporting` | boolean | Đang gửi báo cáo |
| `liked` | boolean | Trạng thái đã like (local) |
| `currentLikeCount` | number | Số like hiện tại (local) |
| `isLiking` | boolean | Đang xử lý like |

### 7.5 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Click Card | `onClick` | Navigate đến `/blog/{id}` |
| Click Avatar/Username | `onClick` | Navigate đến `/user/{authorId}` (stopPropagation) |
| Click Like | `onClick` | Gọi `handleLikeClick()` → Toggle like + update UI |
| Click Delete (owner) | `onClick` | Confirm → `postService.deleteOwnPost()` → call `onDeleted()` |
| Click Report | `onClick` | Mở modal báo cáo |
| Submit Report | `onClick` | `postService.reportPost()` → Đóng modal |

### 7.6 Điều kiện hiển thị

- **Delete Button:** Chỉ hiển thị khi `isOwner = true` (user.id === authorId)
- **Report Button:** Chỉ hiển thị khi đã đăng nhập và không phải owner
- **Username style `--banned`:** Khi `isBanned = true`
- **Like style `--liked`:** Khi `liked = true`

---

## 8. PostCard (Component bài viết compact)

**File:** `src/frontend/components/client/PostCard.tsx`

### 8.1 Tổng quan
Component hiển thị bài viết dạng compact (ngang), với ảnh bên trái và nội dung bên phải. Thường được sử dụng trong danh sách bài viết gợi ý hoặc trang cá nhân.

### 8.2 Props Interface

```typescript
interface PostCardProps {
  id?: string | number;
  imageSrc: string;
  authorName: string;
  timeAgo: string;
  content: string;
  likeCount: number;
  commentCount: number;
  isLiked?: boolean;
  isBanned?: boolean;
}
```

### 8.3 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Card Container | Link/Div | Nếu có `id` → Link đến `/blog/{id}`, không thì Div thường |
| Image | Div + Img | Ảnh bài viết bên trái |
| Author Name | Span | Tên tác giả, có style `--banned` nếu bị ban |
| Time | Span | Thời gian đăng |
| Content | Paragraph | Nội dung bài viết |
| Like Button | Button | Icon Heart + count, có class `--liked` khi đã like |
| Comment Count | Div | Icon Comment + count |

### 8.4 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `liked` | boolean | Trạng thái đã like |
| `currentLikeCount` | number | Số like hiện tại |
| `isLiking` | boolean | Đang xử lý like |

### 8.5 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Click Card | Navigation | Nếu có id → Navigate đến `/blog/{id}` |
| Click Like | `onClick` | `e.preventDefault()` + `e.stopPropagation()` → Toggle like |

### 8.6 Logic đặc biệt

- **Conditional Rendering:** Component render `<Link>` nếu có `id`, render `<div>` nếu không có
- **Like interaction:** Yêu cầu đăng nhập, nếu chưa đăng nhập → alert + navigate `/login`
- **Stop Propagation:** Click Like không trigger navigation của card

---

## Dependencies chung Phần 2:

- **postService:** API calls cho posts (`getPosts`, `getPostById`, `createPost`, `toggleLike`, `addComment`, `replyToComment`, `deleteOwnPost`, `deleteOwnComment`, `reportPost`, `reportComment`, `uploadPostImages`)
- **AuthContext:** Kiểm tra `isAuthenticated`, lấy `user` info
- **react-router-dom:** Navigation (`useNavigate`, `Link`, `useParams`)
- **Icons:** Heart, Comment, Location, Flag, Trash từ config/constants
- **formatTimeAgo:** Utility format thời gian

### CSS Files:
- `BlogPage.css`
- `BlogDetailPage.css`
- `BlogCard.css`
- `PostCard.css`

---

# PHẦN 3: CLIENT PAGES - PLACES + COMPONENTS

---

## 9. PlacesPage (Trang Tất cả Địa điểm)

**File:** `src/frontend/pages/client/PlacesPage.tsx`

### 9.1 Tổng quan
Module này hiển thị danh sách tất cả địa điểm với bộ lọc theo Quận/Huyện và Loại địa điểm. Hỗ trợ phân trang và đồng bộ filter với URL params.

### 9.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Header | Component | Header chung |
| Footer | Component | Footer chung |
| HeroCarousel | Component | Banner với title: "Mỗi địa danh, một câu chuyện" |
| Page Title | Heading (h1) | Text: "Tất cả địa điểm" với icon location |
| Filter Toggle | Button | Text: "Bộ lọc (Phường, tags)" - Toggle hiển thị filter panel |
| Filter Panel | Div | 2 dropdown: Quận/Huyện và Loại địa điểm + nút Xóa bộ lọc |
| Results Count | Paragraph | Text: "Tìm được [X] kết quả" |
| Loading Spinner | Div | Text: "Đang tải địa điểm..." |
| Empty State | Div | Text: "Không tìm thấy địa điểm nào" |
| Places Grid | Div | Grid hiển thị LocationCard components |
| Pagination | Div | Nút «, ‹, số trang, ›, » |

### 9.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `places` | PlaceCompact[] | Danh sách địa điểm từ API |
| `districts` | District[] | Danh sách quận/huyện để filter |
| `placeTypes` | PlaceType[] | Danh sách loại địa điểm để filter |
| `selectedDistrict` | number \| null | ID quận/huyện đã chọn |
| `selectedType` | number \| null | ID loại địa điểm đã chọn |
| `showFilters` | boolean | Hiển thị/ẩn filter panel |
| `currentPage` | number | Trang hiện tại (mặc định: 1) |
| `totalItems` | number | Tổng số địa điểm |
| `isLoading` | boolean | Đang tải địa điểm |
| `isFiltersLoading` | boolean | Đang tải dữ liệu filter |

**Cấu hình:**
- `itemsPerPage`: 9 địa điểm/trang

### 9.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Click "Bộ lọc" | `onClick` | Toggle `showFilters` |
| Chọn Quận/Huyện | `onChange` | Gọi `updateFilters()` → Reset về trang 1 → Cập nhật URL |
| Chọn Loại địa điểm | `onChange` | Gọi `updateFilters()` → Reset về trang 1 → Cập nhật URL |
| Click "Xóa bộ lọc" | `onClick` | Gọi `updateFilters(null, null)` |
| Click số trang | `onClick` | `setCurrentPage(page)` |
| Click « | `onClick` | Về trang đầu tiên |
| Click ‹ | `onClick` | Về trang trước |
| Click › | `onClick` | Sang trang sau |
| Click » | `onClick` | Đến trang cuối |

### 9.5 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchFilters()` | `placeService.getDistricts()` + `placeService.getPlaceTypes()` | Lấy dữ liệu filter (chạy 1 lần) |
| `fetchPlaces()` | `placeService.getPlaces({ page, limit, district_id, place_type_id })` | Lấy danh sách địa điểm với filter |

### 9.6 URL Params Sync

- Đọc params khi load: `page`, `district`, `type`
- Cập nhật URL khi thay đổi filter

### 9.7 Logic Phân trang

- Hiển thị tối đa 7 số trang
- Nếu > 7 trang: hiển thị dạng `1 ... 3 4 5 ... 10`
- Có 4 nút điều hướng: «, ‹, ›, »

---

## 10. LocationInfoPage (Trang Chi tiết Địa điểm)

**File:** `src/frontend/pages/client/LocationInfoPage.tsx`

### 10.1 Tổng quan
Module hiển thị chi tiết thông tin một địa điểm, bao gồm gallery ảnh (carousel), thông tin chung, giờ mở cửa, giá, bài viết liên quan, địa điểm lân cận và gợi ý.

### 10.2 Thành phần giao diện (UI Components)

#### Header Section:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Title | Heading (h1) | Tên địa điểm |
| Rating Box | Div | Hiển thị "[rating]/5" |
| Reviews Link | Anchor | Link đến section #reviews |
| Address | Div | Icon + Địa chỉ |
| Favorite Button | Button | Text: "Lưu vào yêu thích" / "Đã lưu" |

#### Gallery Section:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Image Carousel | Div | Ảnh chính với viewport |
| Prev/Next Arrows | Buttons | Điều hướng carousel (hiển thị khi > 1 ảnh) |
| Dots Indicator | Div | Các dot chỉ vị trí ảnh |

#### Left Column (Content):
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Opening Hours Section | Section | Tiêu đề + Thời gian mở cửa |
| General Info Section | Section | Tiêu đề + Mô tả (có thể expand) + Nút "Xem thêm..." |
| Price Section | Section | Tiêu đề + Giá (hoặc "Miễn phí") |
| Posts Section | Section | Tiêu đề "Posts" + Danh sách BlogCard |

#### Right Column (Sidebar):
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Nearby Section | Section | Tiêu đề "Địa điểm lân cận" + LocationCardHorizontal list |
| Suggestions Section | Section | Tiêu đề "Có thể bạn sẽ thích" + LocationCardHorizontal list |

### 10.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `place` | PlaceDetail \| null | Dữ liệu địa điểm |
| `isLoading` | boolean | Đang tải địa điểm |
| `error` | string \| null | Lỗi khi tải |
| `isFavorite` | boolean | Trạng thái yêu thích |
| `isFavoriteLoading` | boolean | Đang xử lý toggle favorite |
| `favoriteIds` | number[] | Danh sách ID địa điểm đã yêu thích (để check sidebar) |
| `nearbyPlaces` | PlaceCompact[] | Địa điểm lân cận |
| `suggestions` | PlaceCompact[] | Địa điểm gợi ý |
| `isLoadingNearby` | boolean | Đang tải nearby |
| `isLoadingSuggestions` | boolean | Đang tải suggestions |
| `isDescriptionExpanded` | boolean | Mở rộng mô tả |
| `currentSlide` | number | Index ảnh hiện tại |

### 10.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Load trang | `useEffect` | Gọi `fetchPlaceDetails()` |
| Click Favorite | `onClick` | Gọi `handleToggleFavorite()` → Toggle yêu thích |
| Click Carousel Prev | `onClick` | `setCurrentSlide(prev - 1)` (wrap around) |
| Click Carousel Next | `onClick` | `setCurrentSlide(prev + 1)` (wrap around) |
| Click Carousel Dot | `onClick` | `setCurrentSlide(index)` |
| Click "Xem thêm..." | `onClick` | Toggle `isDescriptionExpanded` |
| Click Reviews Link | `onClick` | Scroll đến section #reviews |

### 10.5 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchPlaceDetails()` | `placeService.getPlaceById(id)` | Lấy chi tiết địa điểm |
| `fetchNearbyPlaces()` | `placeService.getNearbyPlaces({ lat, long })` | Lấy địa điểm lân cận |
| `fetchSuggestions()` | `placeService.getNearbyPlaces({ lat, long })` | Lấy gợi ý (filter khác nearby) |
| `handleToggleFavorite()` | `placeService.toggleFavoritePlace(id)` | Toggle yêu thích |
| `checkFavoriteStatus()` | `userService.getProfile()` | Kiểm tra trạng thái yêu thích từ profile |

### 10.6 Dữ liệu hiển thị

- **Tên địa điểm:** `place.name`
- **Rating:** `place.rating_average` (format: X/5)
- **Reviews count:** `place.reviews_count`
- **Địa chỉ:** `place.address`
- **Giờ mở cửa:** `place.opening_hours`
- **Mô tả:** `place.description`
- **Giá:** `place.price_min` - `place.price_max` (hoặc "Miễn phí")
- **Ảnh:** `place.images[]` hoặc `place.main_image_url`
- **Bài viết liên quan:** `place.related_posts[]`

---

## 11. FavoritePlacesPage (Trang Địa điểm Yêu thích)

**File:** `src/frontend/pages/client/FavoritePlacesPage.tsx`

### 11.1 Tổng quan
Module hiển thị danh sách địa điểm yêu thích của người dùng. Hỗ trợ xem yêu thích của mình hoặc của người dùng khác thông qua URL params.

### 11.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Header | Component | Header chung |
| Footer | Component | Footer chung |
| Page Title | Heading (h1) | Text: "Địa điểm yêu thích" với icon Location |
| Loading State | Div | Text: "Đang tải địa điểm yêu thích..." |
| Favorites Grid | Section | Grid 9 items/page với LocationCard |
| Empty State | Div | Text: "Bạn chưa có địa điểm yêu thích nào." + Link "Khám phá địa điểm →" |
| Pagination | Div | Nút «, ‹, số trang, ›, » |

### 11.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `favorites` | PlaceCompact[] | Danh sách địa điểm yêu thích |
| `isLoading` | boolean | Đang tải dữ liệu |
| `currentPage` | number | Trang hiện tại |

**Từ AuthContext:**
- `isAuthenticated`: Đã đăng nhập chưa
- `isLoading` (authLoading): Đang kiểm tra auth
- `user` (currentUser): Thông tin user hiện tại

**URL Params:**
- `userId`: ID người dùng (optional) - nếu có thì xem favorites của user đó

**Derived:**
- `isOwnProfile`: `!userId || currentUser.id === userId`

**Cấu hình:**
- `ITEMS_PER_PAGE`: 9

### 11.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Load trang (chưa đăng nhập) | `useEffect` | Redirect đến `/login` nếu xem của mình và chưa đăng nhập |
| Load trang (đã đăng nhập) | `useEffect` | Fetch favorites từ profile API |
| Click số trang | `onClick` | `handlePageChange(page)` → Scroll lên đầu |
| Click "Khám phá địa điểm" | Click | Navigate đến `/places` |

### 11.5 API Calls

| Điều kiện | API Service | Mô tả |
|-----------|-------------|-------|
| `isOwnProfile = true` | `userService.getProfile()` | Lấy favorites của mình từ `recent_favorites` |
| `isOwnProfile = false` | `userService.getUserProfile(userId)` | Lấy favorites của user khác |

### 11.6 Routes

- `/places/favourite` - Xem yêu thích của mình (yêu cầu đăng nhập)
- `/places/favourite/:userId` - Xem yêu thích của người khác

---

## 12. TrendPlacesPage (Trang Địa điểm Trending)

**File:** `src/frontend/pages/client/TrendPlacesPage.tsx`

### 12.1 Tổng quan
Module hiển thị các địa điểm trending và địa điểm "phải đến". Có fallback mock data khi API lỗi.

### 12.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Header | Component | Header chung |
| Footer | Component | Footer chung |
| HeroCarousel | Component | Banner với title: "Bắt trọn từng khoảnh khắc" |
| Section 1 Title | Heading (h2) | Text: "Địa điểm trending (Trend theo mùa)" |
| Section 1 Content | Div (scroll-container) | Horizontal scroll với LocationCard |
| Section 2 Title | Heading (h2) | Text: "Những nơi bạn phải đến (Mọi lúc mọi nơi)" |
| Section 2 Content | Div (scroll-container) | Horizontal scroll với LocationCard |
| Loading State | Div | Loading spinner với text "Đang tải..." |

### 12.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `trendingPlaces` | PlaceCompact[] | Địa điểm trending từ API |
| `mustVisitPlaces` | PlaceCompact[] | Địa điểm "phải đến" từ API |
| `isTrendingLoading` | boolean | Đang tải trending |
| `isMustVisitLoading` | boolean | Đang tải must-visit |
| `trendingError` | boolean | Lỗi khi tải trending (dùng mock) |
| `mustVisitError` | boolean | Lỗi khi tải must-visit (dùng mock) |

### 12.4 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchTrending()` | `placeService.getPlaces({ page: 1, limit: 5 })` | Lấy 5 địa điểm trang 1 |
| `fetchMustVisit()` | `placeService.getPlaces({ page: 2, limit: 5 })` | Lấy 5 địa điểm trang 2 |

### 12.5 Fallback Mock Data

Khi API lỗi, sử dụng mock data:

**mockTrendingLocations:** 3 địa điểm (Hồ Gươm, Văn Miếu, Lăng Bác)
**mockMustVisitLocations:** 2 địa điểm (Phố cổ, Chùa Một Cột)

### 12.6 Data Mapping (mapPlaceToCard)

```typescript
{
  id: String(place.id),
  imageSrc: place.main_image_url || placeholder,
  title: place.name,
  address: place.address || place.district_name || 'Hà Nội',
  priceMin: place.price_min || 0,
  priceMax: place.price_max || 0,
  rating: place.rating_average || 0,
  reviewCount: place.rating_count || 0
}
```

---

## 13. LocationCard (Component Card Địa điểm)

**File:** `src/frontend/components/common/LocationCard.tsx`

### 13.1 Tổng quan
Component hiển thị thông tin địa điểm dưới dạng card dọc, bao gồm ảnh, tên, địa chỉ, giá và rating.

### 13.2 Props Interface

```typescript
interface LocationCardProps {
  id?: string;
  imageSrc: string;
  title: string;
  address: string;
  priceMin?: number;
  priceMax?: number;
  rating: number;
  reviewCount?: number;
}
```

### 13.3 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Card Container | Link/Div | Nếu có `id` → Link đến `/location/{id}` |
| Image | Img | Ảnh đại diện địa điểm |
| Title | Heading (h3) | Tên địa điểm |
| Address | Paragraph | Icon Location + Địa chỉ |
| Price | Div | Hiển thị khoảng giá hoặc "Miễn phí" |
| Rating | Div | ⭐ Rating + "~ [X]K+ reviews" |

### 13.4 Helper Functions

**formatPriceVND(price):**
- Input: number
- Output: "X VNĐ" hoặc "0 VNĐ"
- Format: `price.toLocaleString('vi-VN')`

**formatReviewCount(count):**
- Input: number | undefined
- Output: "0", "123", hoặc "3.6K+"
- Logic: Nếu >= 1000 thì format thành "XK+"

### 13.5 Logic hiển thị giá

- Nếu `priceMin === 0 && priceMax === 0`: Hiển thị "Miễn phí"
- Ngược lại: Hiển thị "[priceMin] VNĐ - [priceMax] VNĐ"

### 13.6 Conditional Rendering

- Có `id`: Render `<Link to={/location/${id}}>` với class `place-card--link`
- Không có `id`: Render `<div>` với class `place-card`

---

## 14. LocationCardHorizontal (Component Card Địa điểm Ngang)

**File:** `src/frontend/components/client/LocationCardHorizontal.tsx`

### 14.1 Tổng quan
Component hiển thị thông tin địa điểm dạng card ngang (horizontal), thường dùng trong sidebar hiển thị địa điểm lân cận hoặc gợi ý.

### 14.2 Props Interface

```typescript
interface LocationCardHorizontalProps {
  id: string;
  imageSrc: string;
  title: string;
  description: string;
  rating: number;
  likeCount: string;
  distance: string;
  isFavorite?: boolean;
}
```

### 14.3 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Card Container | Link | Link đến `/location/{id}` |
| Image | Div + Img | Ảnh thumbnail bên trái |
| Title | Heading (h4) | Tên địa điểm |
| Rating | Div | Hiển thị "[rating]/5" |
| Description | Paragraph | Địa chỉ hoặc mô tả ngắn |
| Like Count | Div | Icon Heart + số lượng yêu thích |
| Distance | Div | Icon Location + khoảng cách |

### 14.4 Điều kiện hiển thị

- **Heart Icon đỏ:** Khi `isFavorite = true`
  - Class: `location-card-h__stat--favorited` cho container
  - Class: `location-card-h__icon--red` cho icon

### 14.5 Dữ liệu liên quan

Thường được sử dụng với dữ liệu từ `PlaceCompact`:
- `id`: `place.id`
- `imageSrc`: `place.main_image_url`
- `title`: `place.name`
- `description`: `place.address` hoặc `place.district_name`
- `rating`: `place.rating_average`
- `likeCount`: `place.favorites_count`
- `distance`: `place.distance` (từ API nearby)

---

## Dependencies chung Phần 3:

- **placeService:** API calls cho places (`getPlaces`, `getPlaceById`, `getDistricts`, `getPlaceTypes`, `getNearbyPlaces`, `toggleFavoritePlace`)
- **userService:** Lấy profile để check favorites (`getProfile`, `getUserProfile`)
- **AuthContext:** Kiểm tra `isAuthenticated`, lấy `user` info
- **react-router-dom:** Navigation (`useNavigate`, `Link`, `useParams`, `useSearchParams`)
- **Icons:** Heart, Location từ config/constants
- **useScrollToTop:** Custom hook scroll lên đầu trang

### CSS Files:
- `PlacesPage.css`
- `LocationInfoPage.css`
- `FavoritePlacesPage.css`
- `TrendPlacesPage.css`
- `LocationCard.css`
- `LocationCardHorizontal.css`

---

# PHẦN 4: CLIENT PAGES - USER

---

## 15. UserProfilePage (Trang Hồ sơ Người dùng)

**File:** `src/frontend/pages/client/UserProfilePage.tsx`

### 15.1 Tổng quan
Module hiển thị trang hồ sơ người dùng, bao gồm thông tin cá nhân, avatar, địa điểm yêu thích, bài viết nổi bật. Hỗ trợ xem profile của mình hoặc người khác, chỉnh sửa thông tin và đổi mật khẩu (cho profile của mình).

### 15.2 Thành phần giao diện (UI Components)

#### Hero Section:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Avatar | Div + Img | Ảnh đại diện, clickable để upload (chỉ own profile) |
| Avatar Overlay | Div | Icon 📷 hiển thị khi hover (chỉ own profile) |
| Avatar Uploading | Div | Text: "Đang tải..." khi đang upload |
| File Input | Input (hidden) | File picker cho avatar |
| Username | Heading (h1) | Tên người dùng |
| Bio | Paragraph | Giới thiệu (nếu có) |
| Reputation | Paragraph | Text: "Điểm danh tiếng: [X]" |
| Edit Button | Button | Icon Settings + "Chỉnh sửa thông tin cá nhân" (chỉ own profile) |

#### Favorite Places Section:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Section Title | Heading (h2) | "Địa điểm yêu thích" với icon Location |
| View All Link | Link | "Xem tất cả →" → `/places/favourite` hoặc `/places/favourite/:id` |
| Locations Scroll | Div | Horizontal scroll với LocationCard |
| Empty State | Paragraph | "Chưa có địa điểm yêu thích nào" |

#### Posts Section:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Section Title | Heading (h2) | "Bài viết nổi bật" với icon Comment |
| View All Link | Link | "Xem tất cả →" → `/posts/user` hoặc `/posts/user/:id` |
| Posts Grid | Div | Grid PostCard wrapped trong Link |
| Empty State | Paragraph | "Chưa có bài viết nào" |

#### Edit Modal (Tabs):
| Tab | Thành phần | Mô tả |
|-----|------------|-------|
| **Tab "Thông tin cá nhân"** | | |
| | Name Input | Label: "Tên người dùng", Placeholder: "Nhập tên người dùng..." |
| | Bio Input | Label: "Sửa giới thiệu", Placeholder: "Giới thiệu về bản thân..." |
| | Submit Button | Text: "Xác nhận" |
| **Tab "Mật khẩu"** | | |
| | Error/Success Message | Thông báo lỗi hoặc thành công |
| | Old Password Input | Label: "Mật khẩu cũ" |
| | New Password Input | Label: "Mật khẩu mới" |
| | Confirm Password Input | Label: "Xác nhận mật khẩu" |
| | Submit Button | Text: "Xác nhận" |

### 15.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `profile` | UserDetailResponse \| null | Dữ liệu profile |
| `favoritePlaces` | PlaceCompact[] | Địa điểm yêu thích |
| `userPosts` | PostDetail[] | Bài viết của user |
| `isLoading` | boolean | Đang tải profile |
| `error` | string \| null | Lỗi khi tải |
| `isUploading` | boolean | Đang upload avatar |
| `showEditModal` | boolean | Hiển thị modal chỉnh sửa |
| `editName` | string | Giá trị tên đang chỉnh sửa |
| `editBio` | string | Giá trị bio đang chỉnh sửa |
| `isUpdating` | boolean | Đang cập nhật profile |
| `activeTab` | 'info' \| 'password' | Tab active trong modal |
| `oldPassword` | string | Mật khẩu cũ |
| `newPassword` | string | Mật khẩu mới |
| `confirmPassword` | string | Xác nhận mật khẩu |
| `passwordError` | string \| null | Lỗi đổi mật khẩu |
| `passwordSuccess` | boolean | Đổi mật khẩu thành công |

**Derived:**
- `isOwnProfile`: `!id || currentUser.id === id`

### 15.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Load trang | `useEffect` | Gọi `fetchProfile()` |
| Click Avatar (own) | `onClick` | Mở file picker |
| Chọn file avatar | `onChange` | Validate (5MB, image types) → `userService.uploadAvatar()` |
| Click Edit Button | `onClick` | Mở modal (`setShowEditModal(true)`) |
| Click Tab | `onClick` | `setActiveTab('info' | 'password')` |
| Submit Profile | `onClick` | Validate → `userService.updateProfile()` |
| Submit Password | `onClick` | Validate → `authService.changePassword()` |
| Close Modal | `onClick` | `resetEditModal()` - reset tất cả state |

### 15.5 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchProfile()` (own) | `userService.getProfile()` | Lấy profile của mình |
| `fetchProfile()` (other) | `userService.getUserProfile(id)` | Lấy profile người khác |
| `handleAvatarChange()` | `userService.uploadAvatar(file)` | Upload avatar |
| `handleUpdateProfile()` | `userService.updateProfile({ full_name, bio })` | Cập nhật thông tin |
| `handleChangePassword()` | `authService.changePassword({ current_password, new_password })` | Đổi mật khẩu |

### 15.6 Validation

**Avatar:**
- Max size: 5MB
- Allowed types: image/jpeg, image/png, image/gif, image/webp

**Profile Update:**
- `editName` không được trống

**Change Password:**
- Mật khẩu cũ không được trống
- Mật khẩu mới không được trống
- Mật khẩu mới >= 6 ký tự
- Xác nhận mật khẩu phải khớp

### 15.7 Reputation Score Logic

```typescript
// Nếu có reputation_score từ API
if (profile?.reputation_score) return profile.reputation_score;

// Tính toán từ posts: (totalLikes + totalComments) / postCount
const totalLikes = userPosts.reduce((sum, p) => sum + (p.likes_count || 0), 0);
const totalComments = userPosts.reduce((sum, p) => sum + (p.comments_count || 0), 0);
const postCount = userPosts.length || 1;
return Math.round((totalLikes + totalComments) / postCount);
```

### 15.8 Routes

- `/user/:id` - Profile của người khác
- `/profile` hoặc không có id - Profile của mình

---

## 16. UserPostsPage (Trang Bài viết của Người dùng)

**File:** `src/frontend/pages/client/UserPostsPage.tsx`

### 16.1 Tổng quan
Module hiển thị danh sách tất cả bài viết của một người dùng với phân trang. Hỗ trợ xem bài viết của mình hoặc người khác.

### 16.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Header | Component | Header chung |
| Footer | Component | Footer chung |
| Page Title | Heading (h1) | Text: "Bài viết của '[userName]'" |
| Loading State | Div | Text: "Đang tải bài viết..." |
| Posts List | Section | Danh sách BlogCard với pagination |
| Empty State | Div | Text: "Bạn chưa có bài viết nào." + Link "Khám phá bài viết →" |
| Pagination | Div | Nút «, ‹, số trang, ›, » |

### 16.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `posts` | PostDetail[] | Danh sách bài viết |
| `isLoading` | boolean | Đang tải dữ liệu |
| `currentPage` | number | Trang hiện tại |
| `userName` | string | Tên người dùng (để hiển thị title) |

**Từ AuthContext:**
- `isAuthenticated` / `isLoading` (authLoading) / `user` (currentUser)

**URL Params:**
- `userId`: ID người dùng (optional)

**Derived:**
- `isOwnProfile`: `!userId || currentUser.id === userId`

**Cấu hình:**
- `ITEMS_PER_PAGE`: 3

### 16.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Load trang (chưa đăng nhập) | `useEffect` | Redirect `/login` nếu xem của mình và chưa đăng nhập |
| Load trang | `useEffect` | Fetch posts từ profile API |
| Click số trang | `onClick` | `handlePageChange(page)` → Scroll lên đầu |
| Delete post | `onDeleted` callback | Remove post từ local state |

### 16.5 API Calls

| Điều kiện | API Service | Mô tả |
|-----------|-------------|-------|
| `isOwnProfile = true` | `userService.getProfile()` | Lấy posts của mình từ `recent_posts` |
| `isOwnProfile = false` | `userService.getUserProfile(userId)` | Lấy posts của user khác |

### 16.6 BlogCard Props Mapping

```typescript
{
  id: post._id,
  authorId: post.author?.id,
  avatarSrc: post.author?.avatar_url || '/default-avatar.png',
  username: post.author?.full_name || 'Ẩn danh',
  timeAgo: formatTimeAgo(post.created_at),
  location: post.related_place?.name || 'Hà Nội',
  rating: post.rating || 0,
  imageSrc1: post.images?.[0] || '/placeholder.jpg',
  imageSrc2: post.images?.[1] || post.images?.[0] || '/placeholder.jpg',
  likeCount: post.likes_count || 0,
  commentCount: post.comments_count || 0,
  description: post.content?.slice(0, 100) || '',
  isLiked: post.is_liked || false,
  onDeleted: () => { /* Remove from local state */ },
  isBanned: post.author?.is_banned
}
```

### 16.7 Routes

- `/posts/user` - Bài viết của mình (yêu cầu đăng nhập)
- `/posts/user/:userId` - Bài viết của người khác

---

## 17. SearchResultsPage (Trang Kết quả Tìm kiếm)

**File:** `src/frontend/pages/client/SearchResultsPage.tsx`

### 17.1 Tổng quan
Module hiển thị kết quả tìm kiếm địa điểm, kết hợp với địa điểm lân cận (dựa trên geolocation) và gợi ý địa điểm.

### 17.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Header | Component | Header chung |
| Footer | Component | Footer chung |
| **Section 1: Kết quả tìm kiếm** | | |
| Section Title | Heading (h2) | Text: "Kết quả tìm kiếm cho: '[query]'" hoặc "Tất cả địa điểm" |
| Results Count | Span | Text: "([X] kết quả)" |
| Results Cards | Div (scroll-container) | Horizontal scroll với LocationCard |
| Empty State | Paragraph | Text: "Không tìm thấy kết quả nào cho '[query]'" |
| **Section 2: Địa điểm lân cận** | | |
| Section Title | Heading (h2) | Text: "Địa điểm lân cận" với icon Location |
| Nearby Cards | Div (scroll-container) | Horizontal scroll với LocationCard |
| **Section 3: Có thể bạn sẽ thích** | | |
| Section Title | Heading (h2) | Text: "Có thể bạn sẽ thích" với icon Location |
| Suggestions Cards | Div (scroll-container) | Horizontal scroll với LocationCard |
| **Loading State** | | |
| Skeleton Cards | Div | 5 skeleton cards placeholder |

### 17.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `searchResults` | PlaceCompact[] | Kết quả tìm kiếm |
| `nearbyPlaces` | PlaceCompact[] | Địa điểm lân cận |
| `suggestions` | PlaceCompact[] | Địa điểm gợi ý |
| `isLoadingSearch` | boolean | Đang tải kết quả tìm kiếm |
| `isLoadingNearby` | boolean | Đang tải nearby |
| `isLoadingSuggestions` | boolean | Đang tải suggestions |

**URL Params:**
- `q`: Từ khóa tìm kiếm (từ searchParams)

### 17.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Load trang | `useEffect` | Fetch search + nearby + suggestions |
| Query thay đổi | `useEffect` | Re-fetch search results, scroll lên đầu |

### 17.5 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchSearchResults()` | `placeService.searchPlaces({ keyword: query, page: 1 })` | Tìm kiếm địa điểm |
| `fetchNearbyPlaces()` | `placeService.getNearbyPlaces({ lat, long })` | Lấy địa điểm lân cận |
| `fetchSuggestions()` | `placeService.getPlaces({ page: 1, limit: 5 })` | Lấy gợi ý địa điểm |

### 17.6 Geolocation Logic

```typescript
// 1. Kiểm tra browser hỗ trợ geolocation
if ('geolocation' in navigator) {
  // 2. Thử lấy vị trí người dùng
  navigator.geolocation.getCurrentPosition(
    // Success: Sử dụng vị trí thực
    (position) => {
      fetchNearbyPlaces(position.coords.latitude, position.coords.longitude);
    },
    // Error: Sử dụng vị trí mặc định Hà Nội
    () => {
      fetchNearbyPlaces(21.0285, 105.8542);
    }
  );
} else {
  // Không hỗ trợ: Sử dụng vị trí mặc định Hà Nội
  fetchNearbyPlaces(21.0285, 105.8542);
}
```

### 17.7 Route

- `/search?q=[keyword]` - Kết quả tìm kiếm

---

## Dependencies chung Phần 4:

- **userService:** API calls cho user (`getProfile`, `getUserProfile`, `uploadAvatar`, `updateProfile`)
- **authService:** Đổi mật khẩu (`changePassword`)
- **placeService:** Tìm kiếm và nearby (`searchPlaces`, `getNearbyPlaces`, `getPlaces`)
- **AuthContext:** Kiểm tra `isAuthenticated`, lấy `user`, `refreshUser`
- **react-router-dom:** Navigation (`useNavigate`, `Link`, `useParams`, `useSearchParams`)
- **Icons:** Settings, Location, Comment từ config/constants
- **formatTimeAgo:** Utility format thời gian

### CSS Files:
- `UserProfilePage.css`
- `UserPostsPage.css`
- `SearchResultsPage.css`

---

# PHẦN 5: CLIENT COMPONENTS

---

## 18. Header (Component Header)

**File:** `src/frontend/components/client/Header.tsx`

### 18.1 Tổng quan
Component Header chung cho tất cả trang client, bao gồm logo, search bar, navigation links, và user menu.

### 18.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Logo | Link + Img | Logo → Link đến `/` |
| Search Bar | Form | Input tìm kiếm + nút submit với icon Search |
| Mobile Menu Toggle | Button | Icon hamburger/close - Toggle mobile nav |
| Navigation Links | Nav | Links: Blog trải nghiệm, Khám phá địa điểm, Điểm đến phổ biến |
| Loading Spinner | Div | Hiển thị khi đang check auth |
| **User Menu (đã đăng nhập):** | | |
| User Avatar | Div + Img | Avatar + Dropdown icon |
| Dropdown Menu | Div | Items: Hồ sơ, Quản trị (admin only), Đăng xuất |
| **Auth Links (chưa đăng nhập):** | | |
| Register Link | Link | Text: "Đăng ký" |
| Login Button | Link | Text: "Đăng nhập" (styled as button) |

### 18.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `searchQuery` | string | Từ khóa tìm kiếm |
| `showUserMenu` | boolean | Hiển thị dropdown user menu |
| `showMobileMenu` | boolean | Hiển thị mobile navigation |

**Từ AuthContext:**
- `user`, `isAuthenticated`, `logout`, `isLoading`

### 18.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Submit Search | `onSubmit` | Navigate đến `/search?q=[query]`, scroll lên đầu |
| Click Mobile Toggle | `onClick` | Toggle `showMobileMenu` |
| Click Avatar | `onClick` | Toggle `showUserMenu` |
| Click Outside | `mousedown` | Đóng menus |
| Click Đăng xuất | `onClick` | `logout()` → Navigate đến `/` |
| Click nav link | `onClick` | Đóng mobile menu |

### 18.5 Điều kiện hiển thị

- **Loading Spinner:** Khi `isLoading = true`
- **User Menu:** Khi `isAuthenticated && user`
- **"Quản trị" link:** Khi `user.role === 'admin'`
- **Auth Links:** Khi chưa đăng nhập

### 18.6 Navigation Links

| Text | Route |
|------|-------|
| Blog trải nghiệm | `/blogs` |
| Khám phá địa điểm | `/places` |
| Điểm đến phổ biến | `/trend-places` |
| Hồ sơ | `/profile` |
| Quản trị | `/admin` |
| Đăng ký | `/register` |
| Đăng nhập | `/login` |

---

## 19. Footer (Component Footer)

**File:** `src/frontend/components/client/Footer.tsx`

### 19.1 Tổng quan
Component Footer chung cho tất cả trang client, hiển thị thông tin thương hiệu, social links, và navigation links.

### 19.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| **Brand Column:** | | |
| Logo | Img | Logo thương hiệu |
| Social Buttons | Buttons | Icons: X (Twitter), Instagram, Youtube |
| **Column "Về Hanoivivu":** | | |
| Title | Heading (h3) | Text: "VỀ Hanoivivu" |
| Links | List | "Về chúng tôi", "Du lịch bền vững" |
| **Column "Đối tác":** | | |
| Title | Heading (h3) | Text: "Đối tác" |
| Links | List | "Đăng ký đối tác", "Đối tác liên kết" |
| **Column "Điều khoản":** | | |
| Title | Heading (h3) | Text: "Điều khoản sử dụng" |
| Links | List | "Chính sách bảo mật", "Chính sách cookie" |
| **Copyright:** | | |
| Text | Paragraph | "© 2014-2025 hanoivivu. All Rights Reserved." |

### 19.3 Không có State

Footer là component tĩnh, không quản lý state.

---

## 20. Chatbot (Component Chatbot AI)

**File:** `src/frontend/components/client/Chatbot.tsx`

### 20.1 Tổng quan
Component chatbot AI floating, cho phép người dùng chat với trợ lý du lịch Hà Nội. Có tính năng lưu lịch sử chat vào localStorage với thời gian hết hạn 15 phút.

### 20.2 Thành phần giao diện (UI Components)

#### Floating Button:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Toggle Button | Button | Icon chatbot/close - Toggle chat window |

#### Chat Window:
| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Header | Div | Avatar + "Trợ lý Hanoivivu" + "● Online" + Reset/Close buttons |
| Messages Container | Div | Danh sách tin nhắn với scroll |
| Message (Bot) | Div | Avatar bot + Markdown content + Suggested places |
| Message (User) | Div | User avatar + Text content |
| Loading Indicator | Div | 3 dots animation khi đang gửi |
| Suggested Places | Div | Cards gợi ý địa điểm từ bot response |
| Input | Div | Text input + Send button |

### 20.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `isOpen` | boolean | Chat window đang mở |
| `messages` | Message[] | Danh sách tin nhắn |
| `inputValue` | string | Giá trị input hiện tại |
| `userAvatar` | string \| null | Avatar người dùng |
| `conversationId` | string \| null | ID conversation từ API |
| `isLoading` | boolean | Đang gửi tin nhắn |

### 20.4 Message Interface

```typescript
interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  suggestedPlaces?: PlaceCompact[];
}
```

### 20.5 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Click Toggle | `onClick` | Toggle `isOpen` |
| Enter / Click Send | `onKeyPress` / `onClick` | `handleSendMessage()` → Call API → Add response |
| Click Reset | `onClick` | `handleResetMessages()` → Clear localStorage + Reset state |
| Click Close | `onClick` | `setIsOpen(false)` |
| Click Suggested Place | `onClick` | Navigate đến `/location/{id}` |

### 20.6 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `handleSendMessage()` | `chatbotService.sendMessage(message, conversationId)` | Gửi tin nhắn cho chatbot |

### 20.7 LocalStorage

**Key:** `hanoivivu_chat_history`

**Data:**
```typescript
{
  messages: Message[],
  conversationId: string | null,
  lastMessageTime: string // ISO timestamp
}
```

**Expiry:** 15 phút - Nếu `lastMessageTime` > 15 phút trước → Clear storage

### 20.8 Fallback Responses

Khi API fail, sử dụng fallback responses cho các keywords:
- Hồ Gươm, Hồ Hoàn Kiếm
- Phố cổ
- Ăn gì, đồ ăn
- Khách sạn, ở đâu
- Cảm ơn, thank

---

## 21. CreatePostModal (Component Modal Tạo Bài viết)

**File:** `src/frontend/components/client/CreatePostModal.tsx`

### 21.1 Tổng quan
Component modal cho phép người dùng tạo bài viết mới với location picker, rating input, và image upload.

### 21.2 Props Interface

```typescript
interface CreatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit?: (data: {
    location: string;
    related_place_id?: number;
    rating: number;
    content: string;
    images: File[];
  }) => void;
}
```

### 21.3 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Overlay | Div | Click outside để close |
| Header | Div | Title: "Đăng bài viết" + Close button |
| **Options Bar:** | | |
| Location Picker | Div | Icon + "Chọn địa điểm" + Clear button |
| Rating Input | Div | ⭐ + "Đánh giá:" + Number input (1-5) + "/5" |
| Image Selector | Div | 🖼️ + "Chọn ảnh" + count |
| **Location Picker Dropdown:** | | |
| Search Input | Input | Placeholder: "Tìm kiếm địa điểm..." |
| Places List | Div | Danh sách địa điểm từ API |
| **Image Preview:** | | |
| Preview Items | Div | Thumbnail + Remove button |
| Content Textarea | Textarea | Placeholder: "Chia sẻ trải nghiệm của bạn" |
| Submit Button | Button | Text: "Đăng bài" |

### 21.4 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `location` | string | Tên địa điểm đã chọn |
| `selectedPlaceId` | number \| undefined | ID địa điểm |
| `rating` | number \| '' | Rating (1-5) |
| `content` | string | Nội dung bài viết |
| `images` | File[] | Ảnh đã chọn |
| `showLocationPicker` | boolean | Hiển thị location dropdown |
| `places` | PlaceCompact[] | Danh sách địa điểm |
| `searchKeyword` | string | Từ khóa tìm địa điểm |
| `isLoadingPlaces` | boolean | Đang tải danh sách địa điểm |

### 21.5 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Click Location Option | `onClick` | Toggle `showLocationPicker` |
| Search Location | `onChange` | Debounce 300ms → `placeService.searchPlaces()` |
| Select Place | `onClick` | Set `location` + `selectedPlaceId`, close picker |
| Clear Location | `onClick` | Reset location fields |
| Change Rating | `onChange` | Validate 1-5 integer → `setRating()` |
| Click "Chọn ảnh" | `onClick` | Create file input → Open file picker |
| Remove Image | `onClick` | Filter out image from array |
| Click Overlay | `onClick` | `onClose()` |
| Click Submit | `onClick` | Validate → `onSubmit(data)` → Reset form |

### 21.6 Validation

- `content` không được trống
- `location` không được trống
- `rating` phải là số nguyên từ 1-5

### 21.7 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| (on picker open) | `placeService.getPlaces({ page: 1, limit: 20 })` | Lấy danh sách địa điểm |
| (on search) | `placeService.searchPlaces({ keyword })` | Tìm kiếm địa điểm |

---

## 22. HeroCarousel (Component Carousel Banner)

**File:** `src/frontend/components/client/HeroCarousel.tsx`

### 22.1 Tổng quan
Component carousel banner cho homepage và các trang khác, với auto-play, navigation arrows, dots indicator, và optional search bar.

### 22.2 Props Interface

```typescript
interface HeroCarouselProps {
    title?: string;             // Default: "Gói trọn tinh hoa Hà Nội"
    subtitle?: string;          // Default: "Từ phố cổ thâm trầm..."
    images?: string[];          // Default: DEFAULT_IMAGES (4 images)
    showSearchBar?: boolean;    // Default: true
    autoPlayInterval?: number;  // Default: 5000 (ms)
}
```

### 22.3 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Slides Container | Div | Danh sách background images |
| Slide | Div | Background image với class `active` cho slide hiện tại |
| Content Overlay | Div | Title + Subtitle |
| Title | Heading (h1) | Tiêu đề carousel |
| Subtitle | Paragraph | Phụ đề |
| Search Bar | Form | Icon + Input + Button "Tìm kiếm" (optional) |
| Prev Arrow | Button | Icon ◂ - Chuyển slide trước |
| Next Arrow | Button | Icon ▸ - Chuyển slide sau |
| Dots Indicator | Div | Dots cho mỗi slide, active dot highlighted |

### 22.4 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `currentIndex` | number | Index slide hiện tại |
| `searchQuery` | string | Từ khóa tìm kiếm |

### 22.5 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Auto-play | `useEffect` interval | `goToNext()` mỗi 5 giây |
| Click Prev | `onClick` | `goToPrev()` - Wrap around |
| Click Next | `onClick` | `goToNext()` - Wrap around |
| Click Dot | `onClick` | `setCurrentIndex(index)` |
| Submit Search | `onSubmit` | Navigate `/search?q=[query]`, scroll lên đầu |

### 22.6 Default Images

4 ảnh Unsplash mặc định (Hà Nội):
1. https://images.unsplash.com/photo-1710141968276-...
2. https://images.unsplash.com/photo-1599708153386-...
3. https://images.unsplash.com/photo-1601108644994-...
4. https://images.unsplash.com/photo-1702118937156-...

### 22.7 Auto-play Logic

```typescript
useEffect(() => {
    if (autoPlayInterval <= 0) return; // Disable if 0 or negative

    const timer = setInterval(goToNext, autoPlayInterval);
    return () => clearInterval(timer); // Cleanup on unmount
}, [autoPlayInterval, goToNext]);
```

---

## Dependencies chung Phần 5:

- **AuthContext:** `user`, `isAuthenticated`, `logout`, `isLoading`
- **chatbotService:** `sendMessage(message, conversationId)`
- **placeService:** `getPlaces()`, `searchPlaces()`
- **react-router-dom:** `useNavigate`, `Link`
- **Icons:** Search, Close, Location, Send, Trash, Instagram, Youtube từ config/constants
- **ReactMarkdown:** Render markdown cho chatbot responses

### CSS Files:
- `Header.css`
- `Footer.css`
- `Chatbot.css`
- `CreatePostModal.css`
- `HeroCarousel.css`

---

# PHẦN 6: ADMIN PAGES

---

## 23. AdminHomePage (Trang Chủ Admin)

**File:** `src/frontend/pages/admin/AdminHomePage.tsx`

### 23.1 Tổng quan
Trang dashboard quản trị, hiển thị thống kê số liệu (users, posts, reports), biểu đồ lượt truy cập 7 ngày gần đây, và danh sách địa điểm nổi bật.

### 23.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| AdminHeader | Component | Header admin |
| **Section 1: Thống kê số liệu** | | |
| Section Title | Heading (h2) | "Thống kê số liệu" với icon Graph |
| Stats Grid | Div | 4 stat items |
| Stat Item | Div | Label + Value + Change description |
| **Section 2: Lượt truy cập** | | |
| Section Title | Heading (h2) | "Lượt truy cập (7 ngày gần đây)" |
| Summary Stats | Div | Tổng lượt truy cập + Khách truy cập |
| Line Chart | SVG | Chart hiển thị visits_trend |
| **Section 3: Địa điểm nổi bật** | | |
| Section Title | Heading (h2) | "Địa điểm nổi bật" |
| Location Rows | Div | LocationCard + Stats (alternating layout) |

### 23.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `stats` | DashboardStats \| null | Thống kê dashboard |
| `featuredPlaces` | PlaceCompact[] | Địa điểm nổi bật |
| `isLoading` | boolean | Đang tải dữ liệu |
| `visitAnalytics` | { visits_trend, summary } \| null | Dữ liệu lượt truy cập |

### 23.4 Stats hiển thị

| Label | Value Source | Change |
|-------|--------------|--------|
| Số người hoạt động | `total_users` | Hôm nay: +`new_users_today` |
| Số bài viết | `total_posts` | Hôm nay: +`new_posts_today` |
| Chờ duyệt | `pending_posts` | Bài viết cần xử lý |
| Báo cáo | `total_reports` | Cần xem xét |

### 23.5 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| (on load) | `adminService.getDashboardStats()` | Lấy thống kê dashboard |
| (on load) | `placeService.getPlaces({ page: 1, limit: 3 })` | Lấy featured places |
| (on load) | `adminService.getVisitAnalytics(7)` | Lấy lượt truy cập 7 ngày |

### 23.6 Fallback Mock Data

Có sẵn `mockStats` và `mockFeaturedLocations` nếu API fail.

---

## 24. AdminUsersPage (Quản lý Người dùng)

**File:** `src/frontend/pages/admin/AdminUsersPage.tsx`

### 24.1 Tổng quan
Trang quản lý danh sách người dùng, hỗ trợ lọc theo trạng thái (all/active/banned), tìm kiếm, phân trang, ban/unban/delete users.

### 24.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Title | Heading (h1) | "Quản lý người dùng" |
| Search Bar | Input | Placeholder: "Tìm trong trang hiện tại..." |
| Status Filter | Select | Options: Tất cả, Đang hoạt động, Đã bị cấm |
| Results Count | Paragraph | Text: "Có X người dùng (Trang Y/Z)" |
| Users Table | Table | Columns: ID, Họ tên, Email, Vai trò, Trạng thái, Độ uy tín, Chức năng |
| Pagination | Div | Nút «, số trang, » |
| **Ban Modal** | | |
| Modal Overlay | Div | Click outside để close |
| Modal Title | Heading (h3) | "Ban người dùng" |
| Description | Paragraph | "Bạn đang ban: [userName]" |
| Reason Input | Textarea | Placeholder: "Nhập lý do ban (bắt buộc)" |
| Actions | Div | Nút Hủy + Xác nhận Ban |

### 24.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `users` | AdminUser[] | Danh sách users |
| `searchQuery` | string | Từ khóa tìm kiếm |
| `statusFilter` | 'all' \| 'active' \| 'banned' | Lọc trạng thái |
| `currentPage` | number | Trang hiện tại |
| `totalItems` | number | Tổng số users |
| `isLoading` | boolean | Đang tải |
| `banModal` | { open, userId, userName } | State modal ban |
| `banReason` | string | Lý do ban |
| `actionLoading` | number \| null | ID user đang xử lý |

### 24.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Click Ban | `onClick` | Mở ban modal |
| Click Unban | `onClick` | `handleUnban(userId)` → Update local state |
| Click Delete | `onClick` | Confirm → `handleDelete(userId)` |
| Submit Ban | `onClick` | `handleBan()` → Update local state |
| Change Filter | `onChange` | Reset page = 1, re-fetch |

### 24.5 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchUsers()` | `adminService.getUsers({ status, page })` | Lấy danh sách users |
| `handleBan()` | `adminService.banUser(userId, reason)` | Ban user |
| `handleUnban()` | `adminService.unbanUser(userId)` | Unban user |
| `handleDelete()` | `adminService.deleteUser(userId)` | Xóa user |

### 24.6 Role Mapping

| role_id | Role Name |
|---------|-----------|
| 1 | Admin |
| 2 | Moderator |
| 3 | User |

**Lưu ý:** Không hiển thị nút Ban/Unban/Delete cho users có `role_id = 1` (Admin).

---

## 25. AdminPostsPage (Duyệt Bài viết)

**File:** `src/frontend/pages/admin/AdminPostsPage.tsx`

### 25.1 Tổng quan
Trang duyệt bài viết pending, cho phép admin chấp nhận hoặc từ chối bài viết.

### 25.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Title | Heading (h1) | "Duyệt bài" |
| Loading State | Div | Spinner + "Đang tải bài viết..." |
| Empty State | Div | "Không có bài viết nào đang chờ duyệt." |
| **Post Card** | | |
| Header | Div | Avatar + Username + Time + Rating |
| Location | Div | Icon + Place name |
| Images | Div | 2 images |
| Description | Paragraph | Content truncated 200 chars |
| Actions | Div | Nút "Từ chối" + "Chấp nhận" |
| Pagination | Div | Nút «, ‹, số trang, ›, » |

### 25.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `posts` | PostDetail[] | Danh sách posts pending |
| `pagination` | Pagination \| null | Pagination info |
| `currentPage` | number | Trang hiện tại |
| `isLoading` | boolean | Đang tải |
| `processingIds` | Set<string> | IDs đang xử lý |

### 25.4 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchPosts()` | `adminService.getPosts({ status: 'pending', page })` | Lấy posts pending |
| `handleApprove()` | `adminService.updatePostStatus(postId, 'published')` | Duyệt bài |
| `handleReject()` | `adminService.updatePostStatus(postId, 'rejected')` | Từ chối bài |

---

## 26. AdminLocationsPage (Quản lý Địa điểm)

**File:** `src/frontend/pages/admin/AdminLocationsPage.tsx`

### 26.1 Tổng quan
Trang quản lý danh sách địa điểm, hỗ trợ tìm kiếm, phân trang, thêm/sửa/xóa địa điểm.

### 26.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Title | Heading (h1) | "Quản lý địa điểm" |
| Search Bar | Input | Placeholder: "Tìm kiếm trong trang hiện tại..." |
| Toolbar | Div | Results count + "Thêm địa điểm" button |
| Locations Table | Table | Columns: ID, Tên, Quận, Đánh giá, Giá, Ngày tạo, Chức năng |
| Pagination | Div | Nút điều hướng |

### 26.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `locations` | PlaceDetail[] | Danh sách địa điểm |
| `pagination` | Pagination \| null | Pagination info |
| `searchQuery` | string | Từ khóa tìm kiếm |
| `currentPage` | number | Trang hiện tại |
| `isLoading` | boolean | Đang tải |
| `actionLoading` | number \| null | ID đang xử lý |

### 26.4 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchLocations()` | `adminService.getPlaces({ page, limit: 10 })` | Lấy danh sách |
| `handleDelete()` | `adminService.deletePlace(locationId)` | Xóa địa điểm |

### 26.5 Navigation

- Click "Thêm địa điểm" → `/admin/locations/add`
- Click "Sửa" → `/admin/locations/edit/:id`

---

## 27. AdminReportsPage (Quản lý Báo cáo)

**File:** `src/frontend/pages/admin/AdminReportsPage.tsx`

### 27.1 Tổng quan
Trang quản lý báo cáo vi phạm (posts/comments), cho phép xử lý vi phạm (xóa nội dung) hoặc bỏ qua báo cáo.

### 27.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Title | Heading (h1) | "Quản lý báo cáo" |
| Results Count | Paragraph | "Có X báo cáo (Trang Y/Z)" |
| Reports Table | Table | Columns: ID, Loại, Lý do, Chi tiết, Người báo cáo, Ngày tạo, Chức năng |
| Pagination | Div | Nút điều hướng |

### 27.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `reports` | AdminReport[] | Danh sách báo cáo |
| `pagination` | Pagination \| null | Pagination info |
| `resolvedIds` | Set<string> | IDs đã xử lý |
| `currentPage` | number | Trang hiện tại |
| `isLoading` | boolean | Đang tải |
| `actionLoading` | string \| null | ID đang xử lý |

### 27.4 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchReports()` | `adminService.getReports({ page, limit: 10 })` | Lấy danh sách |
| `handleProcessViolation()` (post) | `adminService.deletePost(targetId, reason)` | Xóa bài viết vi phạm |
| `handleProcessViolation()` (comment) | `adminService.deleteComment(targetId)` | Xóa comment vi phạm |
| `handleMarkReviewed()` | `adminService.dismissReport(reportId)` | Bỏ qua báo cáo |

---

## 28. AdminLogPage (Log Hoạt động)

**File:** `src/frontend/pages/admin/AdminLogPage.tsx`

### 28.1 Tổng quan
Trang xem log hoạt động hệ thống, hỗ trợ lọc theo user_id và action type.

### 28.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Title | Heading (h1) | "Log hoạt động" |
| Filters | Div | User ID input + Action type select + Count |
| Log Table | Table | Columns: user_id, action, ip, time, details |
| Pagination | Div | Nút điều hướng |

### 28.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `logs` | AuditLog[] | Danh sách logs |
| `pagination` | { total, limit, offset } | Pagination info |
| `currentPage` | number | Trang hiện tại |
| `isLoading` | boolean | Đang tải |
| `actionFilter` | string | Lọc theo action type |
| `userIdFilter` | string | Lọc theo user ID |

### 28.4 Action Types

| Value | Label |
|-------|-------|
| `` (empty) | Tất cả |
| `login` | Đăng nhập |
| `logout` | Đăng xuất |
| `register` | Đăng ký |
| `password_change` | Đổi mật khẩu |
| `profile_update` | Cập nhật profile |
| `create_post` | Tạo bài viết |
| `like_post` | Like bài viết |
| `create_comment` | Tạo comment |
| `report_content` | Báo cáo |

### 28.5 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| `fetchLogs()` | `adminService.getAuditLogs({ limit, offset, user_id, action_type })` | Lấy danh sách logs |

---

## 29. AdminAddPlacePage (Thêm Địa điểm)

**File:** `src/frontend/pages/admin/AdminAddPlacePage.tsx`

### 29.1 Tổng quan
Form thêm địa điểm mới với đầy đủ thông tin: tên, quận, loại hình, mô tả, tọa độ, giờ mở cửa, giá, ảnh.

### 29.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Title | Heading (h1) | "Thêm địa điểm" |
| **Left Column** | | |
| Name Input | Input | Tên địa điểm* |
| District Select | Select | Quận/Phường* |
| Place Type Select | Select | Loại hình* |
| Description Input | Input | Mô tả |
| Location Inputs | 2 Inputs | Kinh độ + Vĩ độ |
| **Right Column** | | |
| Time Inputs | 2 Inputs | Mở cửa + Đóng cửa |
| Price Inputs | 2 Inputs | Min + Max |
| Image Upload | Button + Hidden Input | Thêm ảnh |
| Image Previews | Div | Thumbnails + Remove buttons |
| Submit Button | Button | "Thêm địa điểm" |

### 29.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `isLoading` | boolean | Đang tải districts/types |
| `isCreating` | boolean | Đang tạo địa điểm |
| `isUploading` | boolean | Đang upload ảnh |
| `districts` | District[] | Danh sách quận |
| `placeTypes` | PlaceType[] | Danh sách loại hình |
| `images` | string[] | URLs ảnh đã upload |
| `formData` | PlaceCreateRequest | Dữ liệu form |

### 29.4 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| (on load) | `placeService.getDistricts()` | Lấy danh sách quận |
| (on load) | `placeService.getPlaceTypes()` | Lấy loại địa điểm |
| `handleImageUpload()` | `uploadService.uploadFiles(files)` | Upload ảnh |
| `handleSubmit()` | `adminService.createPlace(formData)` | Tạo địa điểm |

### 29.5 Workflow

1. Tạo địa điểm trước (không có ảnh)
2. Upload ảnh với `place_id` vừa tạo
3. Update địa điểm với URLs ảnh
4. Navigate về `/admin/locations`

---

## 30. AdminEditPlacePage (Sửa Địa điểm)

**File:** `src/frontend/pages/admin/AdminEditPlacePage.tsx`

### 30.1 Tổng quan
Form sửa địa điểm có sẵn, tương tự AdminAddPlacePage nhưng load dữ liệu từ API.

### 30.2 URL Params

- `id`: ID địa điểm cần sửa

### 30.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `isLoading` | boolean | Đang tải dữ liệu |
| `isUpdating` | boolean | Đang cập nhật |
| `isUploading` | boolean | Đang upload ảnh |
| `districts` | District[] | Danh sách quận |
| `placeTypes` | PlaceType[] | Danh sách loại hình |
| `images` | string[] | URLs ảnh |
| `formData` | PlaceUpdateRequest | Dữ liệu form |

### 30.4 API Calls

| Hàm | API Service | Mô tả |
|-----|-------------|-------|
| (on load) | `placeService.getPlaceById(id)` | Lấy thông tin địa điểm |
| (on load) | `placeService.getDistricts()` | Lấy danh sách quận |
| (on load) | `placeService.getPlaceTypes()` | Lấy loại địa điểm |
| `handleImageUpload()` | `uploadService.uploadPlaceImages(files, placeId)` | Upload ảnh |
| `handleSubmit()` | `adminService.updatePlace(id, formData)` | Cập nhật địa điểm |

---

## Dependencies chung Phần 6:

- **adminService:** Tất cả API admin (`getDashboardStats`, `getUsers`, `getPosts`, `getPlaces`, `getReports`, `getAuditLogs`, `getVisitAnalytics`, ban/unban/delete operations, etc.)
- **placeService:** `getPlaces()`, `getDistricts()`, `getPlaceTypes()`, `getPlaceById()`
- **uploadService:** `uploadFiles()`, `uploadPlaceImages()`
- **Icons:** Graph, Search, Ban, Edit, Trash, Check từ config/constants
- **formatTimeAgo:** Utility format thời gian
- **AdminHeader:** Component header admin

### CSS Files:
- `AdminHomePage.css`
- `AdminUsersPage.css`
- `AdminPostsPage.css`
- `AdminLocationsPage.css`
- `AdminReportsPage.css`
- `AdminLogPage.css`
- `AdminAddPlacePage.css` (shared với EditPlacePage)

---

# PHẦN 7: ADMIN COMPONENTS + ROUTING CONFIGURATION

---

## 31. AdminHeader (Component Header Admin)

**File:** `src/frontend/components/admin/AdminHeader.tsx`

### 31.1 Tổng quan
Component header cho phần quản trị, bao gồm logo, navigation links với active state, và user dropdown menu.

### 31.2 Thành phần giao diện (UI Components)

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| Logo | Link + Img | Logo → Link đến `/admin` |
| **Navigation** | Nav | 6 nav links |
| Duyệt bài | Link | → `/admin/posts` |
| Kiểm tra log | Link | → `/admin/log` |
| Thống kê Tổng quan | Link | → `/admin` (exact match) |
| Quản lý Địa điểm | Link | → `/admin/locations` |
| Quản lý Báo cáo | Link | → `/admin/reports` |
| Quản lý Người dùng | Link | → `/admin/users` |
| **User Menu** | | |
| User Avatar | Div + Img | Avatar hoặc placeholder |
| Dropdown Menu | Div | Items: Hồ sơ, Đăng xuất |

### 31.3 Trạng thái (States)

| State | Kiểu dữ liệu | Mô tả |
|-------|--------------|-------|
| `showUserMenu` | boolean | Hiển thị user dropdown |

**Từ AuthContext:**
- `user`, `logout`

**Từ react-router-dom:**
- `location` (dùng cho active link detection)

### 31.4 Tương tác (Interactions)

| Hành động | Sự kiện | Xử lý |
|-----------|---------|-------|
| Click Avatar | `onClick` | Toggle `showUserMenu` |
| Click Outside | `mousedown` | Đóng dropdown |
| Click Đăng xuất | `onClick` | `logout()` → Navigate to `/` |

### 31.5 Active Link Detection

```typescript
const isActiveLink = (path: string, exact = false) => {
    if (exact) {
        return location.pathname === path;
    }
    return location.pathname === path || location.pathname.startsWith(path + '/');
};
```

- `/admin` sử dụng exact match
- Các routes khác sử dụng prefix match (e.g., `/admin/locations/add` → active cho `/admin/locations`)

---

## 32. Routing Configuration (main.tsx)

**File:** `src/frontend/main.tsx`

### 32.1 Tổng quan
File cấu hình routing cho toàn bộ ứng dụng, bao gồm public routes, auth routes, protected routes, và admin routes.

### 32.2 Route Guards

| Guard | Mô tả |
|-------|-------|
| `PublicRoute` | Redirect user đã đăng nhập về home |
| `ProtectedRoute` | Yêu cầu đăng nhập |
| `AdminRoute` | Yêu cầu đăng nhập + role admin |

### 32.3 Route Configuration

#### Public Routes (Không cần đăng nhập):

| Path | Component | Mô tả |
|------|-----------|-------|
| `/` | App | Trang chủ |
| `/search` | SearchResultsPage | Kết quả tìm kiếm |
| `/trend-places` | TrendPlacesPage | Điểm đến phổ biến |
| `/places` | PlacesPage | Tất cả địa điểm |
| `/blogs` | BlogPage | Blog/Newfeed |
| `/blog/:id` | BlogDetailPage | Chi tiết bài viết |
| `/location/:id` | LocationInfoPage | Chi tiết địa điểm |
| `/user/:id` | UserProfilePage | Profile người khác |
| `/places/favourite/:userId` | FavoritePlacesPage | Favorites của user khác |
| `/posts/user/:userId` | UserPostsPage | Bài viết của user khác |

#### Auth Routes (PublicRoute - Redirect nếu đã đăng nhập):

| Path | Component | Mô tả |
|------|-----------|-------|
| `/login` | Login | Đăng nhập |
| `/register` | Register | Đăng ký |
| `/forgot-password` | ForgotPassword | Quên mật khẩu |
| `/reset-password` | ResetPassword | Đặt lại mật khẩu |

#### Protected Routes (ProtectedRoute - Yêu cầu đăng nhập):

| Path | Component | Mô tả |
|------|-----------|-------|
| `/profile` | UserProfilePage | Profile của mình |
| `/places/favourite` | FavoritePlacesPage | Favorites của mình |
| `/posts/user` | UserPostsPage | Bài viết của mình |

#### Admin Routes (AdminRoute - Yêu cầu role admin):

| Path | Component | Mô tả |
|------|-----------|-------|
| `/admin` | AdminHomePage | Dashboard admin |
| `/admin/users` | AdminUsersPage | Quản lý người dùng |
| `/admin/locations` | AdminLocationsPage | Quản lý địa điểm |
| `/admin/locations/add` | AdminAddPlacePage | Thêm địa điểm |
| `/admin/locations/edit/:id` | AdminEditPlacePage | Sửa địa điểm |
| `/admin/reports` | AdminReportsPage | Quản lý báo cáo |
| `/admin/posts` | AdminPostsPage | Duyệt bài viết |
| `/admin/log` | AdminLogPage | Log hoạt động |

### 32.4 App Structure

```tsx
ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
      <Chatbot />  {/* Global chatbot - hiển thị trên tất cả pages */}
    </AuthProvider>
  </StrictMode>
);
```

### 32.5 Error Handling

- `/` → `errorElement: <ErrorPage />`
- `/admin` → `errorElement: <ErrorPage />`

---

## Dependencies Phần 7:

- **react-router-dom:** `createBrowserRouter`, `RouterProvider`, `Link`, `useNavigate`, `useLocation`
- **AuthContext:** `user`, `logout`
- **Route Guards:** `ProtectedRoute`, `PublicRoute`, `AdminRoute`

### CSS Files:
- `AdminHeader.css`

---

# TỔNG KẾT TÀI LIỆU UI

## Thống kê tổng quan:

| Phần | Số lượng modules | Mô tả |
|------|------------------|-------|
| Phần 1 | 4 | Authentication Pages |
| Phần 2 | 4 | Blog Pages + Components |
| Phần 3 | 6 | Places Pages + Components |
| Phần 4 | 3 | User Pages |
| Phần 5 | 5 | Client Components |
| Phần 6 | 8 | Admin Pages |
| Phần 7 | 2 | Admin Components + Routing |
| **Tổng** | **32** | **Modules** |

## Danh sách đầy đủ:

### Client Pages (17):
1. Login
2. Register
3. ForgotPassword
4. ResetPassword
5. BlogPage
6. BlogDetailPage
7. PlacesPage
8. LocationInfoPage
9. FavoritePlacesPage
10. TrendPlacesPage
11. UserProfilePage
12. UserPostsPage
13. SearchResultsPage

### Common Components (2):
14. BlogCard (`components/common/`)
15. LocationCard (`components/common/`)

### Client Components (7):
16. PostCard (`components/client/`)
17. LocationCardHorizontal (`components/client/`)
18. Header (`components/client/`)
19. Footer (`components/client/`)
20. Chatbot (`components/client/`)
21. CreatePostModal (`components/client/`)
22. HeroCarousel (`components/client/`)

### Admin Pages (8):
23. AdminHomePage
24. AdminUsersPage
25. AdminPostsPage
26. AdminLocationsPage
27. AdminReportsPage
28. AdminLogPage
29. AdminAddPlacePage
30. AdminEditPlacePage

### Admin Components + Config (2):
31. AdminHeader (`components/admin/`)
32. Routing Configuration (main.tsx)
