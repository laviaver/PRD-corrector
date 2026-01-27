import { BrowserRouter, Routes, Route } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/upload" element={<UploadPage />} />
          {/* Analysis and results routes will be added in Phase 4-5 */}
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
