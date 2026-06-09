SUMMARY = "Person detection service using YOLOv8 and MQTT"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://detector.py \
    file://mqtt_publisher.py \
    file://config.py \
    file://person-detector.service \
"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE:${PN} = "person-detector.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install() {
    install -d ${D}/home/pi/rpi-person-detector/src
    install -m 0755 ${WORKDIR}/detector.py      ${D}/home/pi/rpi-person-detector/src/
    install -m 0644 ${WORKDIR}/mqtt_publisher.py ${D}/home/pi/rpi-person-detector/src/
    install -m 0644 ${WORKDIR}/config.py         ${D}/home/pi/rpi-person-detector/src/

    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/person-detector.service \
        ${D}${systemd_system_unitdir}/person-detector.service
}

FILES:${PN} += " \
    /home/pi/rpi-person-detector/ \
    ${systemd_system_unitdir}/person-detector.service \
"

RDEPENDS:${PN} = "python3 python3-opencv python3-paho-mqtt python3-numpy"
