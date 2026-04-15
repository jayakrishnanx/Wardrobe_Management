#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
    
    # Add 'apps' to sys.path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(base_dir, 'apps'))

    # Patch runserver to show the local network IP
    if 'runserver' in sys.argv:
        try:
            import socket
            def get_ip():
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(('10.255.255.255', 1))
                    IP = s.getsockname()[0]
                except Exception:
                    IP = '127.0.0.1'
                finally:
                    s.close()
                return IP

            from django.core.management.commands.runserver import Command as RunserverCommand
            original_inner_run = RunserverCommand.inner_run

            def patched_inner_run(self, *args, **options):
                if self.addr == '0.0.0.0' or self.addr == '127.0.0.1':
                    local_ip = get_ip()
                    self.stdout.write(self.style.SUCCESS(f"\n🚀 Network access: http://{local_ip}:{self.port}/"))
                    self.stdout.write(self.style.SUCCESS(f"💻 Local access:   http://127.0.0.1:{self.port}/\n"))
                original_inner_run(self, *args, **options)

            RunserverCommand.inner_run = patched_inner_run
        except Exception:
            pass
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
