# RSS Reader
An RSS reader written in Python (Django) and JavaScript (React).

## Setup
First clone the project:
```
git clone https://github.com/mahyarap/rss-reader && cd rss-reader
```

The project consists of several `Dockerfile`s and a `docker-compose.yml`.
To bring the whole project up, simply run:
```
docker-compose up -d
```

Then run the migrations:
```
docker-compose exec python manage.py migrate
```

Optionally create a super user:
```
docker-compose exec python manage.py createsuperuser
```

When migrations are done, enter the following URL in your favorite browser:
```
http://localhost:8000
```

The API can be reached at:
```
http://localhost:8080
```

## Architecture
There are 5 services in the project:

* Backend powered by Django and DRF
* Frontend powered by React
* Task queue powered by Celery for async an periodic jobs
* redis server as the message broker
* PostGreSQL server as the database

You can find the summary of each service (except for postgres and redis) in the
following paragraphs:

The backend only exposes a REST API to be consumed by the frontend. Having an
API-only backend makes it possible to develop any services around a common API
such mobile applications.

The authentication method for the backend is token. For every registered user,
a token is automatically generated. All the routes are protected except the
routes for login and registration.

The frontend is a simple React SPA application. To keep the frontend simple, I
didn't use Redux for state management. One implication of it is that the app
does not support inter-component communication except for parent-child
communication. This means there are few places that need manual refresh.

For the task queue I used Celery. Celery is simple to use and integrates well
with Django. It uses redis as its broker.
The task queue consists of two components: worker and heart beat generator for
periodic tasks. There can be actually more that one worker by simply scaling
the `scraper` service in the `docker-compose.yml`.
For example, to have 4 workers, simply run:
```
docker-compose up -d --scale scraper=4
```

### Main Features
To ease the reviewing of the app, in the following lines, I have highlighted
the main features of the backend service.

In the system, no duplicate feed or feed entry can be created and it is
enforced at the database level. Each user just subscribes to a feed (the
relation between user and feed is many-to-many) and has its own private read
entries and bookmarks (read entries and bookmarks have many-to-one relation
with entry). The result is that each user has its own view of the feeds without
having their own private feeds.

There is a back-off mechanism for misbehaving feeds. Feeds have 3 different
priorities. Priority is a non-negative integer where smaller values indicate
higher priority. When a feed is added, it is marked as high priority. During
the update phase, if the feed does not respond in time and times out, it's
penalized with a lower priority. The lower priority, the less frequent it is
checked for updates. Each time the feed responds in time, it's awarded with
higher priority.

Since the nature of updating the feeds is IO-bound (in contrast with e.g.
image resizing which is CPU-bound), I used the `eventlet` execution pool of
Celery. `eventlet` uses cooperative multitasking which works very well for
IO-bound use cases.

The API is versioned to facilitate introducing new features and removing
deprecated ones.

I used the `signiture` and `group` features of Celery for parallel processing
of the tasks in the workers. 

The `queryset` for most `viewset`s it tuned to use `prefetch_related` of Django
to avoid the N+1 query problem in most cases.

Logging is enabled for critical paths such as creating and indexing feeds.

Django settings are split into development and production. The `wsgi.py` and
`celery.py` are configured to use the production settings by default to avoid
accidentally revealing settings and secrets to the public. However in the
`docker-compose.yml` it is set to use development settings.

All services use multi-stage docker build to reduce their final image size
except for the frontend image because its final artifact is a static bundle not
a service (one could put the bundle in an Nginx image and serve it).

## Running Tests
To run the tests simply run:
```
docker-compose exec web python manage.py test
```

## Final Notes
Please note that the way this project has been configured is not
production-ready. For production it needs many more configurations such as
removing the hard-coded secrets and passing environment variables.

The frontend should actually reside in a separate repository. I put it in this
repo to have everything in one place in order to ease the reviewing.
