TARGETS = \
	demo_inheritance.txt \
	demo_list_upstream_heating_elements.txt \
	demo_temperature_of_hx_prim_in.txt \
	demo_verb_matching.txt \
	demo_extra_namespace.txt \
	demo_equipment.txt \

all: demos

test: sdu_gtc_simple.ttl
	python ../apps/RUN_APPS.py sdu_gtc_simple.ttl

demos: ${TARGETS}

clean:
	rm sdu_gtc.ttl ${TARGETS}

mrproper: clean
	rm -f *~

sdu_gtc.ttl: generator rooms.json
	./generator

sdu_gtc_simple.ttl: simple_generator rooms.json
	./simple_generator

demo_extra_namespace.ttl: demo_extra_namespace
	./demo_extra_namespace

demo_extra_namespace.txt: demo_extra_namespace.ttl
	./demo_extra_namespace_query > demo_extra_namespace.txt

demo_inheritance.txt: ./demo_inheritance
	./demo_inheritance > demo_inheritance.txt

demo_list_upstream_heating_elements.txt: ./demo_list_upstream_heating_elements sdu_gtc.ttl
	./demo_list_upstream_heating_elements > demo_list_upstream_heating_elements.txt

demo_temperature_of_hx_prim_in.txt: ./demo_temperature_of_hx_prim_in sdu_gtc.ttl
	./demo_temperature_of_hx_prim_in > demo_temperature_of_hx_prim_in.txt

demo_verb_matching.txt: ./demo_verb_matching
	./demo_verb_matching > demo_verb_matching.txt

demo_equipment.txt: demo_equipment
	./demo_equipment > demo_equipment.txt

