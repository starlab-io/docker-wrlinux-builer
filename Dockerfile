# Same as what poky does: must explicitly delcare the base OS
ARG BASE_DISTRO=SPECIFY_ME

FROM crops/yocto:$BASE_DISTRO-base
USER root
RUN apt-get update && \
    apt-get install -y \
        qemu-system && \
    rm -rf /var/lib/apt/lists/*
COPY entry.py /usr/bin
COPY become_owner_of /usr/bin
ENTRYPOINT ["/usr/bin/entry.py"]
WORKDIR /

# Environment variables for our build setup
ENV SSTATE_DIR=/var/lib/sstate
ENV BB_ENV_EXTRAWHITE="$BB_ENV_EXTRAWHITE SSTATE_DIR STARLAB_LAYERS"