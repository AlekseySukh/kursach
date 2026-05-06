import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.database import init_db
from ui.main_window import MainWindow

if __name__ == "__main__":
    init_db()
    app = MainWindow()
    app.mainloop()
