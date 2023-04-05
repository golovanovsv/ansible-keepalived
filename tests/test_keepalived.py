import testinfra
import pytest

@pytest.fixture()
def AnsibleVars(host):
  default_vars = host.ansible("include_vars", "file=defaults/main.yml")["ansible_facts"]
  test_vars = host.ansible("include_vars", "file=molecule/default/vars.yml")["ansible_facts"]
  merged_vars = { **default_vars, **test_vars }
  return merged_vars

def test_keepalived_is_installed(host):
  assert host.package("keepalived").is_installed

def test_service_is_enabled(host):
  assert host.service("keepalived").is_enabled

def test_service_is_running(host):
  assert host.service("keepalived").is_running

def test_keepalived_config_is_exist(host):
  config = host.file("/etc/keepalived/keepalived.conf")
  assert config.is_file
  assert config.user == "root"
  assert config.group == "root"
  assert oct(config.mode) == "0o600"

def test_keepalived_config_content(host, AnsibleVars):
  config = host.file("/etc/keepalived/keepalived.conf").content_string
  assert AnsibleVars["keepalived_rid"] in config
  assert AnsibleVars["keepalived_vrid"] in config
  assert AnsibleVars["keepalived_priority"] in config
  assert AnsibleVars["keepalived_pass"] in config
  for ip in AnsibleVars["keepalived_vips"]:
    assert ip in config

def test_keepalive_have_ips(host, AnsibleVars):
  interface_ips = host.interface.default().addresses
  for ip in AnsibleVars["keepalived_vips"]:
    assert ip in interface_ips
