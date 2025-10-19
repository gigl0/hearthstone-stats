from sqlalchemy import Column, Integer, String
from app.db.session import Base

class BattlegroundsMatch(Base):
    __tablename__ = "battlegrounds_matches"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String)
    hero = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    placement = Column(Integer)
    rating = Column(Integer)
    rating_after = Column(Integer)
    minions = Column(String)
