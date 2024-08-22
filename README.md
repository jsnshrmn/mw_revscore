## Prerequisites
- docker compose
- this repository

## Initial setup
start the orm
`docker compose up django -d`
run migrations
`docker compose exec django django-admin migrate`
create user for admin site
`docker compose exec django django-admin createsuperuser`

## Collecting data
`docker compose up ingest -d`

After the initial setup, you can just start everything together:
`docker compose up -d`

## Notes
Revision Creation event info is stored in MW_EVENTS
Scores are stored in MW_SCORES

visit http://localhost:8800/ to see a list of revisions scored by both models and the elapsed time for getting scores of each. More to come.
