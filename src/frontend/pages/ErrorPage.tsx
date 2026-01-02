import { useRouteError, isRouteErrorResponse, useNavigate } from 'react-router-dom';
import { Icons } from '../config/constants';
import '../assets/styles/pages/ErrorPage.css';

/**
 * Error Page Component
 * Hiển thị lỗi khi có error trong route
 */
export default function ErrorPage() {
  const error = useRouteError();
  const navigate = useNavigate();

  // Determine error message
  let errorTitle = 'Đã xảy ra lỗi!';
  let errorMessage = 'Có vấn đề không mong muốn xảy ra.';
  let statusCode: number | null = null;

  if (isRouteErrorResponse(error)) {
    // Route error (404, 500, etc.)
    statusCode = error.status;
    errorTitle = `Lỗi ${error.status}`;
    
    switch (error.status) {
      case 404:
        errorMessage = 'Trang bạn tìm kiếm không tồn tại.';
        break;
      case 403:
        errorMessage = 'Bạn không có quyền truy cập trang này.';
        break;
      case 500:
        errorMessage = 'Lỗi máy chủ. Vui lòng thử lại sau.';
        break;
      default:
        errorMessage = error.statusText || errorMessage;
    }
  } else if (error instanceof Error) {
    // JavaScript error
    errorMessage = error.message || errorMessage;
  } else if (typeof error === 'object' && error !== null) {
    // Generic error object
    const errorObj = error as { message?: string; status?: number };
    errorMessage = errorObj.message || errorMessage;
    statusCode = errorObj.status || null;
  }

  const handleGoBack = () => {
    navigate(-1);
  };

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="error-page">
      <div className="error-page__container">
        <div className="error-page__icon">
          <Icons.AlertCircle className="error-page__icon-svg" />
        </div>
        
        <h1 className="error-page__title">{errorTitle}</h1>
        <p className="error-page__message">{errorMessage}</p>
        
        {statusCode && (
          <div className="error-page__status">
            Mã lỗi: <strong>{statusCode}</strong>
          </div>
        )}

        <div className="error-page__actions">
          <button 
            className="error-page__button error-page__button--primary"
            onClick={handleGoBack}
          >
            <Icons.ArrowLeft className="error-page__button-icon" />
            Quay lại
          </button>
          <button 
            className="error-page__button error-page__button--secondary"
            onClick={handleGoHome}
          >
            <Icons.Home className="error-page__button-icon" />
            Về trang chủ
          </button>
        </div>

        {process.env.NODE_ENV === 'development' && error instanceof Error && (
          <details className="error-page__details">
            <summary className="error-page__details-summary">
              Chi tiết lỗi (chỉ hiển thị trong môi trường development)
            </summary>
            <pre className="error-page__details-content">
              {error.stack || error.toString()}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}

