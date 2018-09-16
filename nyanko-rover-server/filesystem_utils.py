# Filesystem utilities written by Takashi Kumagai

# Returns true if a file (either a regular file or a symbolic link)
# with the specified pathname exists
def file_exists(pathname):
  if not os.path.exists(pathname):
    print('Path "{}" does not exist.'.format(pathname))
    logging.debug('Path "{}" does not exist.'.format(pathname))
    return False
  elif not os.path.isfile(pathname):
    print('Path "{}" is not a file.'.format(pathname))
    logging.debug('Path "{}" is not a file.'.format(pathname))
    return False
  else:
    return True

