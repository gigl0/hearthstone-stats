import React from "react";

export interface Minion {
  id: string;
  name: string;
  type: string;
  effect: string;
  attack: number;
  health: number;
  image: string;
}

interface MinionCardProps {
  minion: Minion;
}

const MinionCard: React.FC<MinionCardProps> = ({ minion }) => {
  return (
    <div className="minion-card">
      <img src={minion.image} alt={minion.name} />
      <h4>{minion.name}</h4>
      <p>Type: {minion.type}</p>
      <p>Attack: {minion.attack} | Health: {minion.health}</p>
      <p dangerouslySetInnerHTML={{ __html: minion.effect }} />
    </div>
  );
};

export default MinionCard;
