#!/usr/bin/env python3
"""Migrate existing chat_*.txt files into the database.

It uses the same database configuration as `app.py`. If no MySQL URI is set
via the `MYSQL_URI` or `DATABASE_URL` env var, it will use `sqlite:///chat.db`.
"""
import glob
import os
import re
from datetime import datetime

from app import db, Message


def parse_line(line, fallback_ts):
    line = line.rstrip('\n')
    # [YYYY-MM-DD HH:MM:SS] Name: Message
    m = re.match(r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+([^:]+):\s+(.*)$', line)
    if m:
        ts = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
        name = m.group(2).strip()
        msg = m.group(3).strip()
        return ts, name, msg
    # Name: Message
    if ': ' in line:
        name, msg = line.split(': ', 1)
        return fallback_ts, name.strip(), msg.strip()
    # fallback
    return fallback_ts, 'Anonymous', line.strip()


def migrate():
    db.create_all()
    files = glob.glob('chat_*.txt')
    print('Found', len(files), 'chat files to import')
    for fn in files:
        print('Importing', fn)
        mtime = datetime.fromtimestamp(os.path.getmtime(fn))
        with open(fn, 'r', encoding='utf-8') as f:
            for ln in f:
                if not ln.strip():
                    continue
                ts, name, msg = parse_line(ln, mtime)
                mm = Message(room=fn[len('chat_'):-4], timestamp=ts, username=name, text=msg)
                db.session.add(mm)
        db.session.commit()
        print('Imported', fn)


if __name__ == '__main__':
    migrate()
    print('Migration complete')
