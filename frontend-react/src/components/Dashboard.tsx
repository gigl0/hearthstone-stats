import React, { useEffect, useState } from "react";
import MatchTable, { Match } from "./MatchTable";
import Filters from "./Filters";

const Dashboard: React.FC = () => {
  const [matches, setMatches] = useState<Match[]>([]);

  const fetchMatches = (hero?: string, minPlacement?: number) => {
    let url = "http://localhost:4000/api/v1/matches?";
    if (hero) url += `hero=${hero}&`;
    if (minPlacement !== undefined) url += `min_placement=${minPlacement}&`;

    fetch(url)
      .then((res) => res.json())
      .then((data) => setMatches(data))
      .catch(console.error);
  };

  useEffect(() => {
    fetchMatches();
  }, []);

  return (
    <div>
      <h1>Battlegrounds Dashboard</h1>
      <Filters onFilter={(hero, minPlacement) => fetchMatches(hero, minPlacement!)} />
      <MatchTable matches={matches} />
    </div>
  );
};

export default Dashboard;
