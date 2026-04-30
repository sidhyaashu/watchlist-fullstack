```plaintext
watchlist_service/
│
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── watchlist.py
│   │   │   │   └── watchlist_item.py
│   │   │   └── router.py
│   │   └── deps.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── constants.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── migrations/
│   │
│   ├── models/
│   │   ├── watchlist.py
│   │   └── watchlist_item.py
│   │
│   ├── schemas/
│   │   ├── watchlist.py
│   │   └── watchlist_item.py
│   │
│   ├── repository/
│   │   ├── watchlist_repo.py
│   │   └── watchlist_item_repo.py
│   │
│   ├── services/
│   │   ├── watchlist_service.py
│   │   └── watchlist_item_service.py
│   │
│   ├── integrations/
│   │   └── instrument_query.py   # DB access for instruments
│   │
│   ├── cache/
│   │   └── watchlist_cache.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   └── exceptions.py
│   │
│   └── main.py
│
├── tests/
│   ├── test_watchlist.py
│   └── test_watchlist_item.py
│
├── scripts/
│   └── seed_data.py
│
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .env.example
└── README.md
```