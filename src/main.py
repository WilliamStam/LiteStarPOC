import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        port=443,
        host="0.0.0.0",
        proxy_headers=True,
        forwarded_allow_ips='172.16.125.15'
    )