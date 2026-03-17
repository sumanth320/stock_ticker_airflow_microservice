import redis
import json
import requests
import os
import time

r = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=6379, decode_responses=True)

def fetch_worker():
    print("Worker active...")
    while True:
        _, task_data = r.blpop("stock_tasks")
        task = json.loads(task_data)
        symbol = task['symbol']
        
        # Check 1-minute safety lock
        if r.exists(f"lock:{symbol}"):
            continue

        api_key = os.getenv('STOCK_API_KEY')
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
        
        try:
            res = requests.get(url).json()
            price = res['Global Quote']['05. price']
            
            # Store price and set 60s lock
            r.set(f"price:{symbol}", price, ex=3600) 
            r.set(f"lock:{symbol}", "active", ex=60)
            print(f"Fetched {symbol}: {price}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    fetch_worker()