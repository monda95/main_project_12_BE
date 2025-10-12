import { createBrowserRouter } from 'react-router-dom';

import { AppLayout } from '../components/layout/AppLayout';
import { AdminPage } from '../pages/AdminPage';
import { HistoryPage } from '../pages/HistoryPage';
import { HomePage } from '../pages/HomePage';
import { MyPage } from '../pages/MyPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <NotFoundPage />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'history', element: <HistoryPage /> },
      { path: 'mypage', element: <MyPage /> },
      { path: 'admin', element: <AdminPage /> },
      { path: '*', element: <NotFoundPage /> }
    ]
  }
]);
