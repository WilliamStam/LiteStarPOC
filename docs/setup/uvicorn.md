# Litestar + uvicorn setup

Use the `src/main.py` file to start the service in production.

```python
# src/main.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        port=80,
        host="0.0.0.0",
    )
```

If its behind a proxy like haproxy or nginx then refactor it a bit (replace the ip with your proxy's ip).

```python
 # src/main.py
 import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        port=80,
        host="0.0.0.0",
        proxy_headers=True,
        forwarded_allow_ips='xx.xxx.xxx.xxx'
    )
```

use `src/app.py` for your actual litestar setup.

```python
# app.py
app = Litestar(...)
```


setup and activate the venv

```shell
python3.12 install -m venv venv
source venv/bin/activate
```

Install the requirements (if you aren't using requirements.txt i highly recommend it)

```
pip install -r requirements.txt
```

cd into the `src` folder

```shell
cd src
```

and now you're ready to run the service

```shell
python main.py
```