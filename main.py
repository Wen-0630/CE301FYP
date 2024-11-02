# main.py
from src import create_app
from src.investment import start_websocket_thread  # Import WebSocket thread starter


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

