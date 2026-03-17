import streamlit as st
import redis
import os
from streamlit_autorefresh import st_autorefresh

# 1. Setup Connection
r = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=6379, decode_responses=True)

st.set_page_config(page_title="Live Stock Monitor", layout="wide")

# 2. THE HEARTBEAT: Refresh the UI every 5 seconds
# This ensures that as soon as the worker updates Redis, the UI shows it.
st_autorefresh(interval=5000, key="datarefresh")

st.title("📈 Stock Microservice Command Center")

# --- Section 1: Sidebar Controls ---
with st.sidebar:
    st.header("Add New Ticker")
    new_ticker = st.text_input("Ticker Symbol (e.g. TSLA):").upper()
    if st.button("Add to System"):
        if new_ticker:
            r.sadd("active_stocks", new_ticker)
            st.toast(f"Added {new_ticker}!")

# --- Section 2: Live Watchlist ---
st.subheader("Live Market Feed")
watchlist = list(r.smembers("active_stocks"))

if not watchlist:
    st.info("Watchlist is currently empty. Add a ticker in the sidebar to begin.")
else:
    # Create a grid of cards
    cols = st.columns(3) 
    for i, ticker in enumerate(watchlist):
        with cols[i % 3]:
            # Get data from Redis
            price = r.get(f"price:{ticker}")
            lock_ttl = r.ttl(f"lock:{ticker}")
            
            with st.container(border=True):
                st.write(f"### {ticker}")
                
                if price:
                    st.metric("Latest Price", f"${price}")
                else:
                    st.write("⏳ *Waiting for first fetch...*")
                
                # Show status of the 60-second limit
                if lock_ttl > 0:
                    st.progress(lock_ttl / 60, text=f"Refreshing in {lock_ttl}s")
                else:
                    st.caption("✅ Ready for next update")
                
                if st.button(f"Delete {ticker}", key=f"del_{ticker}"):
                    r.srem("active_stocks", ticker)
                    st.rerun()