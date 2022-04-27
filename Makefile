# This should be run locally, and the results committed.

WARNING_BANNER_1 = "\# AUTO-GENERATED FILE.  DO NOT EDIT."
WARNING_BANNER_2 = "\# Edit Dockerfile.in, re-run make, and commit results."

VARIANTS = "ubuntu-20.04 ubuntu-18.04 debian-9"

M4_FLAGS = -DWARNING_BANNER_1=$(WARNING_BANNER_1) \
	   -DWARNING_BANNER_2=$(WARNING_BANNER_2)


TARGETS = Dockerfile.ubuntu-20.04 \
	  Dockerfile.ubuntu-18.04 \
	  Dockerfile.debian-9

all: $(TARGETS)

Dockerfile.ubuntu-20.04: M4_FLAGS += -DBASE_IMAGE=crops/yocto:ubuntu-20.04-base

Dockerfile.ubuntu-18.04: M4_FLAGS += -DBASE_IMAGE=crops/yocto:ubuntu-18.04-base

Dockerfile.debian-9: M4_FLAGS += -DBASE_IMAGE=crops/yocto:debian-9-base

# Results in a harmless circular dependency warning. I don't care enough to fix
# it.
$(TARGETS): Dockerfile.in
	m4 $(M4_FLAGS) $< > $@
