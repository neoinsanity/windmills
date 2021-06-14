* Doing it on the DB engine, it is said that it can handle at max 100 relationships/ distance calculations per s.
* With geopandas + zmq + gevent with the right architecture, in Andu's laptop: 400 relationships/ distance calculations 
in 90s or roughly 0.25 operation per second.
* With geopy + zmq + gevent with the right architecture, in Andu's laptop: 400 relationships/ calculations in 0.04s. 
This is 10k operations/ s per CPU core.
* Without calculating distance: 400 relationships/ calculations in 0.02s. This is 20k operations/ s. 
This is the ceiling on the speed of operations per CPU core. 