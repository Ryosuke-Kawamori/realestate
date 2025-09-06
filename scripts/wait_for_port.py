import socket, sys, time, os

host = os.environ.get("POSTGRES_HOST","db")
port = int(os.environ.get("POSTGRES_PORT","5432"))
timeout = 60

print(f"Waiting for {host}:{port} ...")
t0 = time.time()
while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            print("Port is open.")
            sys.exit(0)
    except OSError:
        if time.time() - t0 > timeout:
            print("Timeout waiting for port.", file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
