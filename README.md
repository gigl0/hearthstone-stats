#python script for populate the db
from app.services.bg_importer import import_from_hdt
import_from_hdt("BgsLastGames.xml")
