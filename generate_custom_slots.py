import re
import string
import random
import os
from kodi_voice import KodiConfigParser, Kodi

config_file = os.path.join(os.path.dirname(__file__), "kodi.config")
config = KodiConfigParser(config_file)

kodi = Kodi(config)


def most_words(l=[]):
  longest = 0
  for s in l:
    if len(s.split()) > longest:
      longest = len(s.split())
  return longest


def sort_by_words(l, longest):
  distributed = []
  for i in range(1, longest + 1):
    dl = [s for s in l if len(s.split()) == i]
    if dl:
      distributed.append(dl)
  return distributed


def clean_results(resp, cat, key, limit=None):
  if not limit:
    try:
      limit = kodi.config.get('alexa', 'slot_items_max')
      if limit and limit != 'None':
        limit = int(limit)
      else:
        limit = None
    except:
      limit = None
  if not limit:
    limit = 100

  cleaned = []
  if 'result' in resp and cat in resp['result']:
    for v in retrieved['result'][cat]:
      name = kodi.sanitize_name(v[key], normalize=False)
      # omit titles with digits, as Amazon never passes numbers as digits
      if not re.search(r'\d', name):
        cleaned.append(name)

  cleaned = {v.lower(): v for v in cleaned}.values()
  cleaned = filter(None, cleaned)
  random.shuffle(cleaned)

  # distribute strings evenly by number of words
  if len(cleaned) > limit:
    longest = most_words(cleaned)
    distributed = sort_by_words(cleaned, longest)
    if distributed:
      total = 0
      cleaned = []
      while total < limit:
        for l in distributed:
          if l:
            total += 1
            cleaned.append(l.pop())

  # sort by number of words just for visibility
  if cleaned:
    longest = most_words(cleaned)
    distributed = sort_by_words(cleaned, longest)
    if distributed:
      cleaned = []
      for dl in distributed:
        cleaned += [l for l in dl]

  return cleaned[:limit]


def write_file(filename, items=[]):
  print 'Writing: %s' % (filename)
  f = open(filename, 'w')
  for a in items:
    f.write("%s\n" % a.encode("utf-8"))
  f.close()


# Generate MUSICPLAYLISTS Slot
retrieved = kodi.GetMusicPlaylists()
cl = clean_results(retrieved, 'files', 'label')
write_file('MUSICPLAYLISTS', cl)


# Generate MUSICGENRES Slot
retrieved = kodi.GetMusicGenres()
cl = clean_results(retrieved, 'genres', 'label')
write_file('MUSICGENRES', cl)


# Generate MUSICARTISTS Slot
retrieved = kodi.GetMusicArtists()
cl = clean_results(retrieved, 'artists', 'artist')
write_file('MUSICARTISTS', cl)


# Generate MUSICALBUMS Slot
retrieved = kodi.GetAlbums()
cl = clean_results(retrieved, 'albums', 'label')
write_file('MUSICALBUMS', cl)


# Generate MUSICSONGS Slot
retrieved = kodi.GetSongs()
cl = clean_results(retrieved, 'songs', 'label')
write_file('MUSICSONGS', cl)
