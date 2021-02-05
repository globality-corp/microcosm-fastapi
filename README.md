# microcosm-fastapi

A bridge between FastAPI and microcosm. Provide state-of-the-art speed of hosting microservices in Python along with dependency injection.

## Test Project

We have set up a test project to demonstrate how the new API would look like when deployed within a service. To get started create a new DB:

```
createuser test_project
createdb -O test_project test_project_db
createdb -O test_project test_project_test_db
```