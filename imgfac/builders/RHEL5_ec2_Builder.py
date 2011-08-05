#   Copyright 2011 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import oz.RHEL_5
import ConfigParser
from Fedora_ec2_Builder import Fedora_ec2_Builder

class RHEL5RemoteGuest(oz.RHEL_5.RHEL5Guest):
    def __init__(self, tdl, config, auto):
        # The debug output in the Guest parent class needs this property to exist
        self.host_bridge_ip = "0.0.0.0"
        # Add virtio as dummy arguments below - doesn't actually matter what we put
        oz.RHEL_5.RHEL5Guest.__init__(self, tdl, config, auto, "virtio",
                                      "virtio")

    def connect_to_libvirt(self):
        pass

class RHEL5_ec2_Builder(Fedora_ec2_Builder):
    def init_guest(self, guesttype):
        # populate a config object to pass to OZ
        # This allows us to specify our own output dir but inherit other Oz behavior
        # TODO: Messy?
        config_file = "/etc/oz/oz.cfg"
        config = ConfigParser.SafeConfigParser()
        config.read(config_file)
        config.set('paths', 'output_dir', self.app_config["imgdir"])
        if guesttype == "local":
            self.guest = oz.RHEL_5.get_class(self.tdlobj, config, None)
        else:
            self.guest = RHEL5RemoteGuest(self.tdlobj, config, None)
        self.guest.diskimage = self.app_config["imgdir"] + "/base-image-" + self.new_image_id + ".dsk"
        # Oz assumes unique names - TDL built for multiple backends guarantees they are not unique
        # We don't really care about the name so just force uniqueness
        self.guest.name = self.guest.name + "-" + self.new_image_id

    def install_euca_tools(self, guestaddr):
        # For RHEL5 we need to enable EPEL, install, then disable EPEL
        # TODO: This depends on external infra which is bad, and trusts external SW, which may be bad
        # For now we also mount up /mnt
        self.guest.guest_execute_command(guestaddr, "mount /dev/sdf /mnt")
        self.guest.guest_execute_command(guestaddr, "rpm -ivh http://download.fedora.redhat.com/pub/epel/5/i386/epel-release-5-4.noarch.rpm")
        self.guest.guest_execute_command(guestaddr, "yum -y install euca2ools")
        self.guest.guest_execute_command(guestaddr, "rpm -e epel-release")