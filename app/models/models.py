# app/models/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BattlegroundsMatch(Base):
    __tablename__ = "battlegrounds_matches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String, nullable=False)
    hero = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    placement = Column(Integer, nullable=False)
    rating = Column(Integer)
    rating_after = Column(Integer)
    minions = Column(String)  # salviamo la lista come stringa separata da ';'
