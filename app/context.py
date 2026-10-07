from datetime import date
def inject_globals():
    return {"today": date.today().isoformat()}
