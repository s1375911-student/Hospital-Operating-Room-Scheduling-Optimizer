import sys


def main():
    """Main launcher for CLI or GUI."""
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        from gui import main as gui_main
        gui_main()
    elif len(sys.argv) > 1 and sys.argv[1] == "--cli":
        from cli import run_cli
        run_cli()
    else:
        print("Hospital Operating Room Scheduling Optimizer")
        print("=" * 60)
        print("\nUsage:")
        print("  python main.py --cli    Run command-line interface")
        print("  python main.py --gui    Run graphical interface")
        print("\nDefault (no args): Show this help message")


if __name__ == "__main__":
    main()
