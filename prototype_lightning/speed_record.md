* Doing it on the DB, Frederic said that it can handle at max 100 relationships/ distance calculations per s.
* With geopandas + zmq + gevent with the right architecture, in Andu's laptop: 400 relationships/ calculations in 90s
* With geopy + zmq + gevent with the right architecture, in Andu's laptop: 400 relationships/ calculations in 0.04s. 
This is 10k operations/ s.
* Without calculating distance: 400 relationships/ calculations in 0.02s. This is 20k operations/ s. 
This is the ceiling on the speed of operations per core. 