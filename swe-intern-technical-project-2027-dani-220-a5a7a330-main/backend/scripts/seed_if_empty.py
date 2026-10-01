# Loads the raw data on first deploy: runs the ingest only when the possession table is empty,
# so redeploys never wipe or duplicate data.

from django.db import transaction

import ingest_raw_data as ingest  # sets up Django on import
from app.dbmodels.models import Possession

if __name__ == '__main__':
    if Possession.objects.exists():
        print('seed_if_empty: data already present, skipping')
    else:
        with transaction.atomic():
            ingest.ingest_teams()
            ingest.ingest_games()
            ingest.ingest_players()
            ingest.ingest_possessions()
        print(f'seed_if_empty: loaded {Possession.objects.count()} possessions')
