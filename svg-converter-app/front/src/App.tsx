import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Converter } from "./pages/Converter";

function App() {
  return (
    <div>
      <Router>
        <Routes>
          <Route path="/" element={<Converter />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
