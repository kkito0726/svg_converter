import {
  BrowserRouter as Router,
  Navigate,
  Routes,
  Route,
} from "react-router-dom";
import { Converter } from "./pages/Converter";

function App() {
  return (
    <div>
      <Router>
        <Routes>
          <Route path="/" element={<Converter />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
