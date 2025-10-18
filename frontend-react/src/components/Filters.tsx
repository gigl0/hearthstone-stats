import React, { useState } from "react";

interface FiltersProps {
  onFilter: (hero: string, minPlacement: number | null) => void;
}

const Filters: React.FC<FiltersProps> = ({ onFilter }) => {
  const [hero, setHero] = useState("");
  const [minPlacement, setMinPlacement] = useState<number | "">("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilter(hero, minPlacement === "" ? null : Number(minPlacement));
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Hero"
        value={hero}
        onChange={(e) => setHero(e.target.value)}
      />
      <input
        type="number"
        placeholder="Max Placement"
        value={minPlacement}
        onChange={(e) => {
          const value = e.target.value;
          setMinPlacement(value === "" ? "" : Number(value));
        }}
      />
      <button type="submit">Apply Filters</button>
    </form>
  );
};

export default Filters;
