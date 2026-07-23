- 💥[Improvement] Upgrade Meilisearch to v1.36.0. This changes the on-disk index format, so v1.36.0 refuses to start on a database created by v1.8.4: the container restart-loops with a "database version (1.8.4) is incompatible with your current engine version (1.36.0)" error. Meilisearch is only a derived index in Open edX and never a source of truth, so the existing index must be discarded and rebuilt after upgrading. Stop the platform, delete `data/meilisearch/data.ms`, then re-run initialisation and reindex: (by @HammadYousaf01)

      tutor local stop
      rm -rf "$(tutor config printroot)/data/meilisearch/data.ms"
      tutor local start -d
      tutor local do init
      tutor local exec cms ./manage.py cms reindex_studio
      tutor local exec cms ./manage.py cms reindex_course --active

- On a large site, the reindex takes a while and search stays incomplete until it finishes, so plan a maintenance window.

- Rolling back is not just reverting the image tag. Because the format only moves forward, v1.8.4 cannot read a v1.36.0 database either, so you also need to restore your pre-upgrade data/meilisearch/data.ms backup.