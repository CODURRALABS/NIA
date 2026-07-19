"""
FileManagerAgent: Handles file system operations with safety checks.
"""
import os
import shutil
import logging
import glob

logger = logging.getLogger("FileManagerAgent")

class FileManagerAgent:
    def list_dir(self, path: str = ".", pattern: str = "*"):
        """Lists files in a directory matching a pattern."""
        try:
            search_path = os.path.join(path, pattern)
            return glob.glob(search_path)
        except Exception as e:
            logger.error(f"List dir error: {e}")
            return []

    def read_file(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Read file error: {e}")
            return None

    def write_file(self, path: str, content: str):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Write file error: {e}")
            return False

    def delete(self, path: str):
        """Deletes a file or directory (CAUTION)."""
        logger.warning(f"Deleting: {path}")
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return True
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False

    def search_recursive(self, root: str, query: str):
        results = []
        for r, d, f in os.walk(root):
            for file in f:
                if query.lower() in file.lower():
                    results.append(os.path.join(r, file))
        return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fm = FileManagerAgent()
    print(fm.list_dir(os.path.expanduser("~"), "Desktop/*"))
