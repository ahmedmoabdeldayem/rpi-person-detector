SUMMARY = "Raspberry Pi image for person detection with YOLOv8 and MQTT"
DESCRIPTION = "Embedded Linux image that runs the person-detector service on boot. \
System packages (OpenCV, paho-mqtt, numpy) are baked in via Yocto. \
The ultralytics package and YOLOv8n model weights are installed on first boot \
via a systemd oneshot service, because the PyTorch dependency tree is too large \
to cross-compile cleanly with Yocto."
LICENSE = "MIT"

inherit core-image

IMAGE_FEATURES += "ssh-server-openssh"

IMAGE_INSTALL:append = " \
    python3 \
    python3-pip \
    python3-numpy \
    python3-opencv \
    python3-paho-mqtt \
    person-detector \
    ml-bootstrap \
    v4l-utils \
"

IMAGE_ROOTFS_SIZE ?= "2097152"
IMAGE_OVERHEAD_FACTOR ?= "1.3"

hostname:pn-base-files = "person-detector"
