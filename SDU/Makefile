TARGETS = \
	demo_inheritance.txt \
	demo_list_upstream_heating_elements.txt \
	demo_temperature_of_hx_prim_in.txt \
	demo_verb_matching.txt \

all: demos

clean:
	rm sdu_gtc.ttl ${TARGETS}

mrproper: clean
	rm -f *~

sdu_gtc.ttl: generator rooms.json
	./generator

demos: ${TARGETS}

demo_inheritance.txt: ./demo_inheritance
	./demo_inheritance > demo_inheritance.txt

demo_list_upstream_heating_elements.txt: ./demo_list_upstream_heating_elements sdu_gtc.ttl
	./demo_list_upstream_heating_elements > demo_list_upstream_heating_elements.txt

demo_temperature_of_hx_prim_in.txt: ./demo_temperature_of_hx_prim_in sdu_gtc.ttl
	./demo_temperature_of_hx_prim_in > demo_temperature_of_hx_prim_in.txt

demo_verb_matching.txt: ./demo_verb_matching
	./demo_verb_matching > demo_verb_matching.txt

