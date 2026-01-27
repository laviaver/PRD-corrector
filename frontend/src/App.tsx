import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/" element={
            <div>
              <h1>PRD Reviewer</h1>
              <p>Application setup in progress...</p>
            </div>
          } />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
