import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Converter } from "./pages/Converter";
import { Download } from "./pages/Download";

function App() {
  return (
    <div>
      <Router>
        <Routes>
          <Route path="/" element={<Converter />} />
          <Route path="/download" element={<Download />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
