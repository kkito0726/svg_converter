import { Converter } from "./pages/Converter";

// 画面は1ページのみ。未知のパス (旧 /download など) は nginx が / へリダイレクトする
function App() {
  return <Converter />;
}

export default App;
