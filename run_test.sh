find . -type f -iname \*.pyc -delete
nosetests -c nose.cfg
nosetests -c nose-doctest.cfg
