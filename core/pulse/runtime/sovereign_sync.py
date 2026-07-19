import os
import sys
import logging
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv

# Add parent directory to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Sovereign Logging
logging.basicConfig(level=logging.INFO, format="[SOVEREIGN SYNC]: %(message)s")

load_dotenv()

def sync_from_huggingface(repo_id: str, filename: str = "checkpoints/latest_4bit.pt", local_dir: str = "./checkpoints"):
    """
    Sovereign Sync Hook: Pulls 4-bit weights from Hugging Face.
    """
    token = os.getenv("HF_TOKEN")
    if not token:
        logging.error("HF_TOKEN not found in .env. Please add it to sync weights.")
        return False

    logging.info(f"Initiating Pull from {repo_id}...")
    try:
        os.makedirs(local_dir, exist_ok=True)
        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            token=token
        )
        logging.info(f"Intelligence Pulled Successfully: {path}")
        return True
    except Exception as e:
        logging.error(f"Sync Failed: {e}")
        return False

if __name__ == "__main__":
    # Example usage:
    # sync_from_huggingface("your-hf-username/nia", "checkpoints/latest_4bit.pt")
    repo = os.getenv("HF_REPO")
    if repo:
        sync_from_huggingface(repo)
    else:
        logging.warning("HF_REPO not set in .env. Skipping auto-sync.")
