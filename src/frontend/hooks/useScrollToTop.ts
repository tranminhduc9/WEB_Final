/**
 * useScrollToTop - Custom hook to scroll to top on route change
 * Use this in page components to auto-scroll to top when navigating
 */

import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export const useScrollToTop = () => {
    const { pathname } = useLocation();

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [pathname]);
};

export default useScrollToTop;
