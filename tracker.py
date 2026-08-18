from init_check import init_check
from args_check import args_run


def main() -> None:
    args, TRACKER_DIR, is_db = init_check() # File checks and input flags

    if args_run(args, TRACKER_DIR, is_db) == 1: # Checks and completes input flags functionality
        return

if __name__ == "__main__":
    main()
