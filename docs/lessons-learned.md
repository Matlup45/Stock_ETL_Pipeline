“Symptom: relation does not exist after down -v. Cause: down -v deletes the data volume, and the init script wasn’t re-run. Fix: idempotent init_db.py.”

Date	Symptom	Root cause	Fix
2026-11-18	relation raw.daily_prices does not exist	docker compose down -v deleted the data, and the init script wasn’t re-run	Idempotent init_db.py script
2026-11-18	TCS had only 1 month of history	Watermark loading only looks forward and can’t see gaps behind it	Backfill with --backfill-from
2026-11-20	Airflow couldn’t write logs / see DAGs	The Windows E: drive mounts had wrong permissions inside Docker	Docker volume for logs, docker cp sync script
2026-11-20	DAG failed in 1 second, repeatedly	IndentationError in extract.py broke the import	Read the real error with a direct run, plus py_compile before each sync
2026-11-20	Unknown ticker was logged NO_DATA and the run stayed green	Empty results weren’t counted as failures	Empty result now fails the run