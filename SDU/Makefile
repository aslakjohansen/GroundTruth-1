TARGETS = \
	demo_temperature_of_hx_prim_in.txt \

all: demos

clean:
	rm sdu_gtc.ttl ${TARGETS}

mrproper: clean
	rm -f *~

sdu_gtc.ttl: generator
	./generator

demos: ${TARGETS}

demo_temperature_of_hx_prim_in.txt: ./demo_temperature_of_hx_prim_in sdu_gtc.ttl
	./demo_temperature_of_hx_prim_in > demo_temperature_of_hx_prim_in.txt

