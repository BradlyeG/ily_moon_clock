# Need to mount storage as read/write
# Connected devices will not be able to write
# Delete this file in the REPL if changes need made
import storage

storage.remount("/", False)