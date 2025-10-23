import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { MatchesPage } from "./pages/MatchesPage";
import { ImportLogsPage } from "./pages/ImportLogsPage";
import { StatsPage } from "./pages/StatsPage";

function App() {
  return (
    <BrowserRouter>
      <div
        style={{
          padding: "2rem",
          fontFamily: "Inter, sans-serif",
          backgroundColor: "#121212",
          minHeight: "100vh",
          color: "#F5F5F5",
        }}
      >
        <h1 style={{ color: "#fff", marginBottom: "1.5rem" }}>
          Hearthstone Battlegrounds Dashboard
        </h1>

        {/* === NAVBAR === */}
        <nav
          style={{
            marginBottom: "2rem",
            display: "flex",
            gap: "1rem",
            flexWrap: "wrap",
          }}
        >
          <Link to="/" style={navLinkStyle}>
            🏠 Dashboard
          </Link>
          <Link to="/matches" style={navLinkStyle}>
            📜 Partite
          </Link>
          <Link to="/import-logs" style={navLinkStyle}>
            🧩 Log Import
          </Link>
          <Link to="/stats" style={navLinkStyle}>
            📊 Statistiche
          </Link>
        </nav>

        {/* === ROUTES === */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/matches" element={<MatchesPage />} />
          <Route path="/import-logs" element={<ImportLogsPage />} />
          <Route path="/stats" element={<StatsPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

const navLinkStyle: React.CSSProperties = {
  color: "#61dafb",
  textDecoration: "none",
  fontWeight: "bold",
  transition: "color 0.2s ease",
};

export default App;
