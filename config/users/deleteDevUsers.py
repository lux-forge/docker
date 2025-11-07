import subprocess
import logging

logger = logging.getLogger("Cleanup")
logger.setLevel(logging.INFO)

def remove_identity(name: str):
    # Check if the name exists as a user
    
    try:
        subprocess.run(["id", name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        logger.info(f"User '{name}' does not exist. Skipping.")
        return
    
    try:
        subprocess.run(["sudo", "userdel", "-r", name], check=True)
        logger.info(f"✅ Removed user '{name}' and home directory.")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Failed to remove user '{name}': {e}")


    # Check if the name exists as a group
    try:
        subprocess.run(["getent", "group", name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        logger.info(f"Group '{name}' does not exist. Skipping.")
        return

    try:
        subprocess.run(["sudo", "groupdel", name], check=True)
        logger.info(f"✅ Removed group '{name}'.")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Failed to remove group '{name}': {e}")

def get_test_users():
    test_users = []
    with open("/etc/passwd", "r") as f:
        for line in f:
            username = line.split(":")[0]
            if username.startswith("test"):
                test_users.append(username)
    if len(test_users) == 0:
        logger.info("No test users found for removal.")
    else:
        logger.info(f"Found test users for removal: {test_users}")
    return test_users

if __name__ == "__main__":
    targets = get_test_users()
    logger.info(f"Found {len(targets)} test users to remove.")
    for user in targets:
        remove_identity(user)