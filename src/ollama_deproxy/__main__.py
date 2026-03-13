try:
    from __init__ import run
except ImportError:
    from .__init__ import run

if __name__ == "__main__":
    run()

__all__ = ["run"]
