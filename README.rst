=============================
Simple messaging service demo
=============================
:Info: Simple demo using MongoDB. Basically a copy of a demo written for SimpleDB.
:Author: Mike Dirolf <mike@10gen.com>

About
=====
This is a demonstration web app using MongoDB for storage. All messages are
stored in a single MongoDB collection. Images and thumbnails are stored using
GridFS on independent collections.

Dependencies (all available via easy_install)
=============================================

- web.py
- PIL
- PyMongo
