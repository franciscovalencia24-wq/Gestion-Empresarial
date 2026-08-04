import sys
import os

sys.path.append(os.path.abspath("."))
from src.database.connection import SessionLocal
from src.database.models import Prospect

db = SessionLocal()

owner_rut = "8116116-K"
prospect_temp = db.query(Prospect).filter_by(rut=owner_rut).first()

if prospect_temp:
    related_prospects = prospect_temp.get_related_prospects(db)
    print(f"Viewing owner: {prospect_temp.nombre}")
    print(f"Related found: {len(related_prospects)}")
    
    for rp in related_prospects:
        if rp.profile:
            has_notes = bool(rp.profile.notas_neuroventas)
            has_audio = bool(rp.profile.audio_path and os.path.exists(rp.profile.audio_path))
            print(f" - Related: {rp.nombre} | Notes: {has_notes} | Audio: {has_audio} ({rp.profile.audio_path})")
            if has_notes or has_audio:
                print("   => WILL BE SHOWN IN UI")
            else:
                print("   => NOT SHOWN IN UI")
        else:
            print(f" - Related: {rp.nombre} has no profile")

db.close()
