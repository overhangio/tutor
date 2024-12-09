# Get or create Meilisearch API key
python -c "
import meilisearch
client = meilisearch.Client('{{ MEILISEARCH_URL }}', '{{ MEILISEARCH_MASTER_KEY }}')
try:
    client.get_key('{{ MEILISEARCH_API_KEY_UID }}')
    print('Key already exists')
except meilisearch.errors.MeilisearchApiError:
    print('Key does not exist: creating...')
    client.create_key({
        'name': 'Open edX backend API key',
        'uid': '{{ MEILISEARCH_API_KEY_UID }}',
        'actions': ['*'],
        'indexes': ['{{ MEILISEARCH_INDEX_PREFIX }}*'],
        'expiresAt': None,
        'description': 'Use it for backend API calls -- Created by Tutor',
    })
"
