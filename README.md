## Prerequisites
- docker compose
- this repository


## Initial setup
- start the orm
- `docker compose up django -d`
- run migrations
- `docker compose exec django django-admin migrate`
- `docker compose exec django django-admin migrate --database=facts`
- create user for admin site
- `docker compose exec django django-admin createsuperuser`


# Build Vue app & collectstatic
- `cd vue`
- `npm install`
- `npm run build`
- `docker compose exec django django-admin collectstatic`


## Collecting data
`docker compose up background -d`

After the initial setup, you can just start everything together:
`docker compose up -d`


## Stack Notes
Revision Creation event info is stored in MW_EVENTS
Scores are stored in MW_SCORES

- uses multiple SQLite databases
- uses django channels to allow a more event-driven design vs resquest/response
- asgi webserver and async middleware allow fully async operation
- code concerned with sets of things (such as data collection) now live in model managers
- all web client code is now fully async
- event consumers now fire model manager methods to perform those long running tasks
- asgi server sends ingest messages to queue on startup
- data presented with async rest apis only
- front end is a vue3 app that calls apis


## Usage
visit http://localhost/ to see a list of revisions scored by both models and the elapsed time for getting scores of each.

You can filter revisions by query parameter, eg. `?model_name=&dt_after=&dt_before=&rev_id_min=&rev_id_max=`

visit http://localhost/api/scores/ to view the underlying api.

More to come.
