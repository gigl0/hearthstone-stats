import React from "react";
import { Minion } from "./MinionCard";

export interface Match {
  player_id: string;
  hero: string;
  start_time: string;
  end_time: string;
  placement: number;
  rating: number;
  rating_after: number;
  minions: Minion[];
}

interface MatchTableProps {
  matches: Match[];
}

const MatchTable: React.FC<MatchTableProps> = ({ matches }) => {
  return (
    <table>
      <thead>
        <tr>
          <th>Hero</th>
          <th>Start</th>
          <th>End</th>
          <th>Placement</th>
          <th>Rating</th>
          <th>Rating After</th>
          <th>Minions</th>
        </tr>
      </thead>
      <tbody>
        {matches.map((m, idx) => (
          <tr key={idx}>
            <td>{m.hero}</td>
            <td>{new Date(m.start_time).toLocaleString()}</td>
            <td>{new Date(m.end_time).toLocaleString()}</td>
            <td>{m.placement}</td>
            <td>{m.rating}</td>
            <td>{m.rating_after}</td>
            <td>
              {m.minions.map((min) => (
                <img key={min.id} src={min.image} alt={min.name} width={40} />
              ))}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default MatchTable;
