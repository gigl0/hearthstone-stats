import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { MatchesPage } from "./pages/MatchesPage";
import { GlobalStatsCards } from "./components/GlobalStatsCards";
import { HeroStatsChart } from "./components/HeroStatsChart";
import { CompositionPieChart } from "./components/CompositionPieChart";

function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: "2rem", fontFamily: "Inter, sans-serif" }}>
        <h1>Hearthstone Battlegrounds Dashboard</h1>
        <nav style={{ marginBottom: "2rem" }}>
          <Link to="/" style={{ marginRight: "1rem" }}>Dashboard</Link>
          <Link to="/matches">Partite</Link>
        </nav>

        <Routes>
          <Route
            path="/"
            element={
              <>
                <GlobalStatsCards />
                <HeroStatsChart />
                <CompositionPieChart />
              </>
            }
          />
          <Route path="/matches" element={<MatchesPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
