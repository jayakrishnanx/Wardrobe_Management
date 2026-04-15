import socket
import io
from django.core.management.commands.runserver import Command as RunserverCommand


class CleanOutput(io.TextIOWrapper):
    """Wraps stdout to replace 0.0.0.0 with 127.0.0.1 in server output."""
    def __init__(self, wrapped):
        self._wrapped = wrapped

    def write(self, msg):
        msg = msg.replace('http://0.0.0.0:8000/', 'http://127.0.0.1:8000/')
        msg = msg.replace('http://0.0.0.0:', 'http://127.0.0.1:')
        self._wrapped.write(msg)

    def flush(self):
        self._wrapped.flush()

    def __getattr__(self, attr):
        return getattr(self._wrapped, attr)


class Command(RunserverCommand):
    help = 'Runs the development server and displays your local IP for mobile access.'

    def handle(self, *args, **options):
        # Force the server to listen on all interfaces
        options['addrport'] = '0.0.0.0:8000'

        # Dynamically get the local IP address
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = "127.0.0.1"

        # Print clean header
        self.stdout.write(self.style.SUCCESS("\n" + "="*50))
        self.stdout.write(self.style.SUCCESS("  WARDROBE MANAGER DEVELOPMENT SERVER"))
        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write(f"  Computer: http://127.0.0.1:8000")
        self.stdout.write(self.style.WARNING(f"  Mobile:   http://{local_ip}:8000"))
        self.stdout.write(self.style.SUCCESS("="*50 + "\n"))

        # Wrap stdout so Django's own "Starting at http://0.0.0.0" becomes 127.0.0.1
        self.stdout = CleanOutput(self.stdout)

        super().handle(*args, **options)
