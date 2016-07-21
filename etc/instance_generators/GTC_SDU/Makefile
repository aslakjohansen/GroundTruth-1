TARGETS = \
	gtc_brick.ttl \


all: ${TARGETS}

install: gtc_brick.ttl
	cp gtc_brick.ttl ../../../building_instances/

clean:
	rm ${TARGETS}

mrproper: clean
	rm -f *~


gtc_brick.ttl: gtc_brickgenerator.py gtc.json gtc_vavs.json rooms.json
	./gtc_brickgenerator.py

