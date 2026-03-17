from airflow.decorators import dag, task
from airflow.providers.redis.hooks.redis import RedisHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime

@dag(dag_id='enterprise_stock_pipeline', start_date=datetime(2024, 1, 1), 
     schedule='* * * * *', catchup=False)
def stock_orchestrator():

    @task()
    def check_watchlist():
        r = RedisHook(redis_conn_id='redis_default').get_conn()
        return [s.decode('utf-8') for s in r.smembers("active_stocks")]

    @task(pool='stock_api_pool')
    def dispatch_work(symbol):
        r = RedisHook(redis_conn_id='redis_default').get_conn()
        if not r.exists(f"lock:{symbol}"):
            import json
            r.rpush("stock_tasks", json.dumps({"symbol": symbol}))
        return symbol

    @task()
    def persist_to_db(symbol):
        if not symbol or "SKIP" in str(symbol): 
            return
        
        r = RedisHook(redis_conn_id='redis_default').get_conn()
        pg = PostgresHook(postgres_conn_id='postgres_default')
        
        price = r.get(f"price:{symbol}")
        
        if price:
            # 1. Ensure the table exists before inserting
            pg.run("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    dt TIMESTAMP,
                    symbol TEXT,
                    price FLOAT
                );
            """)
            
            # 2. Now perform the insert
            pg.run(
                "INSERT INTO stock_prices (dt, symbol, price) VALUES (NOW(), %s, %s)",
                parameters=(symbol, float(price))
            )
            print(f"Successfully persisted {symbol} at {price}")

    # Pipeline
    watchlist = check_watchlist()
    dispatched = dispatch_work.expand(symbol=watchlist)
    persist_to_db.expand(symbol=dispatched)

stock_orchestrator()