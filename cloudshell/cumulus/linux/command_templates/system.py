from cloudshell.cli.command_template.command_template import CommandTemplate

from cloudshell.cumulus.linux.command_templates import (
    ERROR_MAP,
    NotSupports2VlanAwareBridges,
)

CURL_ERROR_MAP = {
    r"curl:|[Ff]ail|[Ee]rror": "Uploading/downloading file via CURL failed"
}
CURL_ERROR_MAP.update(ERROR_MAP)


CREATE_TEMP_FILE = CommandTemplate("mktemp", error_map=ERROR_MAP)
CREATE_TEMP_DIR = CommandTemplate("mktemp -d", error_map=ERROR_MAP)
CREATE_FOLDER = CommandTemplate("mkdir -p {folder_path}", error_map=ERROR_MAP)


COPY_FOLDER = CommandTemplate(
    "cp --parents -rv {src_folder} {dst_folder}/", error_map=ERROR_MAP
)
COPY_FILE = CommandTemplate(
    "cp --parents -fv {src_file} {dst_folder}/", error_map=ERROR_MAP
)

TAR_COMPRESS_FOLDER = CommandTemplate(
    "tar -cvf {compress_name} {folder}", error_map=ERROR_MAP
)
TAR_UNCOMPRESS_FOLDER = CommandTemplate(
    "tar xvf {compressed_file} --overwrite --strip-components 1 -C {destination}",
    error_map=ERROR_MAP,
)

IF_RELOAD_ERROR_MAP = {
    r"[Oo]nly one object with attribute ['\"]bridge-vlan-aware yes['\"] allowed": (
        NotSupports2VlanAwareBridges()
    ),
    **ERROR_MAP,
}
IF_RELOAD = CommandTemplate("ifreload -a", error_map=IF_RELOAD_ERROR_MAP)
RESTART_SERVICE = CommandTemplate("service {name} restart", error_map=ERROR_MAP)
START_SERVICE = CommandTemplate("service {name} start", error_map=ERROR_MAP)
STOP_SERVICE = CommandTemplate("service {name} stop", error_map=ERROR_MAP)

CURL_UPLOAD_FILE = CommandTemplate(
    "curl --insecure --upload-file {file_path} {remote_url}", error_map=CURL_ERROR_MAP
)
CURL_DOWNLOAD_FILE = CommandTemplate(
    "curl --insecure {remote_url} -o {file_path}", error_map=CURL_ERROR_MAP
)

# if file don't have new line at the end last line will be lost when we remove prompt
READ_FILE = CommandTemplate("cat {file_path} && echo", error_map=ERROR_MAP)
WRITE_FILE = CommandTemplate('printf "{text}" > {file_path}', error_map=ERROR_MAP)

SHUTDOWN = CommandTemplate("shutdown -h now", error_map=ERROR_MAP)
REBOOT = CommandTemplate("reboot", error_map=ERROR_MAP)
