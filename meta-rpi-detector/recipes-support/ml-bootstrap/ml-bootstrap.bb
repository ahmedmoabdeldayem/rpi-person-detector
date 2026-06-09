SUMMARY = "First-boot systemd service that installs ultralytics and downloads YOLOv8n weights"
DESCRIPTION = "PyTorch and ultralytics cannot be cleanly cross-compiled with Yocto due to \
the size and complexity of the dependency tree. This oneshot service runs once after \
first network-up, installs them via pip, and downloads the YOLOv8n model weights."
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://ml-bootstrap.sh \
    file://ml-bootstrap.service \
"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE:${PN} = "ml-bootstrap.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/ml-bootstrap.sh ${D}${bindir}/ml-bootstrap

    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/ml-bootstrap.service \
        ${D}${systemd_system_unitdir}/ml-bootstrap.service
}

FILES:${PN} += " \
    ${bindir}/ml-bootstrap \
    ${systemd_system_unitdir}/ml-bootstrap.service \
"

RDEPENDS:${PN} = "python3-pip"
