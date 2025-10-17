const apiBase = "http://127.0.0.1:8000/api/v1/bg";

// Mostra statistiche generali
async function loadStats() {
    const res = await fetch(`${apiBase}/stats`);
    const data = await res.json();

    let html = `
        <p><strong>Totale partite:</strong> ${data.total_matches}</p>
        <p><strong>Media Placement:</strong> ${data.average_placement}</p>
        <p><strong>Top Heroes:</strong> ${data.top_heroes.map(h => h.hero + " (" + h.wins + " vittorie)").join(", ")}</p>
    `;
    document.getElementById("stats").innerHTML = html;
}

// Mostra partite
async function loadMatches() {
    const res = await fetch(`${apiBase}/matches?limit=12`);
    const matches = await res.json();

    const tbody = document.querySelector("#matches tbody");
    tbody.innerHTML = "";
    matches.forEach(m => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${m.player_id}</td>
            <td>${m.hero}</td>
            <td>${m.start_time}</td>
            <td>${m.end_time}</td>
            <td>${m.placement}</td>
            <td>${m.rating}</td>
            <td>${m.rating_after}</td>
            <td>${m.minions.join(", ")}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Carica dati all'apertura della pagina
loadStats();
loadMatches();
