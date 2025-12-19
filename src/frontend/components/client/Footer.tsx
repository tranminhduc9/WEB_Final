import React from 'react';
import { Icons } from '../../config/constants';
import '../../assets/styles/components/Footer.css';
import logo from '../../assets/images/logo.png';

// Nếu Footer sau này có nhận props (ví dụ màu nền), bạn khai báo interface ở đây
// interface FooterProps {
//   bgColor?: string;
// }

// Sử dụng React.FC (Functional Component)
const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer__container">
        
        {/* --- Brand Column --- */}
        <div className="footer__brand-col">
           <div className="footer__logo-box">
             {/* Thay src bằng đường dẫn logo thật của bạn */}
             <img 
               src={logo} 
               alt="Hanoivivu Logo" 
               className="footer__logo-img" 
             />
           </div>
           
           <div className="footer__socials">
             <button className="footer__social-btn" aria-label="X (Twitter)">
                {/* Đảm bảo Icons.Close là 1 component hợp lệ */}
                <Icons.Close /> 
             </button>
             <button className="footer__social-btn" aria-label="Instagram">
                <Icons.Instagram />
             </button>
             <button className="footer__social-btn" aria-label="Youtube">
                <Icons.Youtube />
             </button>
           </div>
        </div>

        {/* --- Column 1: Về Hanoivivu --- */}
        <div className="footer__link-col">
          <h3 className="footer__title">VỀ Hanoivivu</h3>
          <ul className="footer__list">
            <li><a href="#" className="footer__link">Về chúng tôi</a></li>
            <li><a href="#" className="footer__link">Du lịch bền vững</a></li>
          </ul>
        </div>

        {/* --- Column 2: Đối tác --- */}
        <div className="footer__link-col">
          <h3 className="footer__title">Đối tác</h3>
          <ul className="footer__list">
            <li><a href="#" className="footer__link">Đăng ký đối tác</a></li>
            <li><a href="#" className="footer__link">Đối tác liên kết</a></li>
          </ul>
        </div>

        {/* --- Column 3: Điều khoản --- */}
        <div className="footer__link-col">
          <h3 className="footer__title">Điều khoản sử dụng</h3>
          <ul className="footer__list">
            <li><a href="#" className="footer__link">Chính sách bảo mật của Hanoivivu</a></li>
            <li><a href="#" className="footer__link">Chính sách cookie</a></li>
          </ul>
        </div>
      </div>
      
      {/* --- Copyright Section --- */}
      <div className="footer__copyright">
        <p className="footer__copyright-text">© 2014-2025 hanoivivu. All Rights Reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;