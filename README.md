🧙‍♂️ Hearthstone Battlegrounds Stats Tracker

Applicazione completa per analizzare le partite di Hearthstone Battlegrounds usando i log di Hearthstone Deck Tracker (HDT).
Comprende un backend FastAPI, un frontend React e alcuni script di manutenzione automatica.

📁 Struttura del progetto
hearthstone-stats/
│
├── app/                     # Backend FastAPI
│   ├── data/                # Database e file JSON
│   │   ├── bgs.db
│   │   ├── heroes_bg.json
│   │   ├── minions_bg.json
│   │   └── stats_summary.json
│   │
│   ├── db/                  # Configurazione database
│   │   └── session.py
│   │
│   ├── models/              # Modelli ORM
│   │   └── models.py
│   │
│   ├── routers/             # API endpoints
│   │   ├── import_router.py
│   │   ├── matches_router.py
│   │   └── stats_router.py
│   │
│   ├── services/            # Importer e watcher HDT
│   │   ├── bg_importer_enhanced.py
│   │   ├── watch_hdt_realtime.py
│   │   └── bg_stats.py
│   │
│   └── main.py              # Entrypoint FastAPI
│
├── frontend-react/          # Frontend React + TypeScript
│   ├── public/              # Immagini e mapping
│   │   ├── images/
│   │   ├── heroes_bg.json
│   │   └── minions_bg.json
│   │
│   └── src/                 # Codice React
│       ├── api/
│       ├── components/
│       └── pages/           # Dashboard, Stats, Matches, Logs
│
├── scripts/                 # Script di manutenzione
│   └── reanalyze_incomplete_matches.py
│
├── requirements.txt         # Dipendenze Python
├── README.md                # Questo file
└── .env                     # Configurazione locale

⚙️ Prerequisiti

Python 3.12+

Node.js 18+

PostgreSQL o SQLite (default bgs.db)

Hearthstone Deck Tracker installato
(genera BgsLastGames.xml in %APPDATA%\HearthstoneDeckTracker)

🐍 Backend (FastAPI)
Installazione
pip install -r requirements.txt

Avvio del server
uvicorn app.main:app --reload


Server in ascolto su http://localhost:8000

Import manuale
python -m app.services.bg_importer_enhanced

Watcher in tempo reale
python -m app.services.watch_hdt_realtime


Monitora automaticamente BgsLastGames.xml e importa nuovi match appena finiti.

🖥️ Frontend (React + TypeScript)
Installazione
cd frontend-react
npm install

Avvio in modalità sviluppo
npm run dev


Apri http://localhost:5173

Ricorda di configurare nel file .env:

REACT_APP_API_URL=http://localhost:8000

🔧 Script di manutenzione
Rianalisi partite incomplete

Corregge record con placement o minion mancanti:

python -m scripts.reanalyze_incomplete_matches


Esempio output:

🧩 Trovati 4 match da correggere...
🔁 Aggiornato Arch-Villain Rafaam → placement 4, 7 minion
✅ Correzione completata: 4 match aggiornati.

🗃️ Query utili SQL

Controlla partite incomplete

SELECT COUNT(*) FROM battlegrounds_match
WHERE placement IS NULL OR placement = 0
   OR game_result = 'unknown' OR minions_count = 0;


Ultime partite giocate

SELECT hero_name, placement, game_result, rating_delta, start_time
FROM battlegrounds_match
ORDER BY start_time DESC
LIMIT 10;

🧰 Comandi rapidi
Azione	Comando
Avvia backend	uvicorn app.main:app --reload
Avvia watcher HDT	python -m app.services.watch_hdt_realtime
Import manuale	python -m app.services.bg_importer_enhanced
Re-analizza partite	python -m scripts.reanalyze_incomplete_matches
Avvia frontend	npm run dev
Build frontend	npm run build
#python script for populate the db
from app.services.bg_importer import import_from_hdt
import_from_hdt("BgsLastGames.xml")
