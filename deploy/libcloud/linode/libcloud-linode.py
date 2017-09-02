import os
from libcloud.compute.base import NodeAuthSSHKey
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

cls = get_driver(Provider.LINODE)

driver = cls(open('libcloud-key.txt','r').read())

driver.list_nodes()

# For example, create (Ubuntu 16.04, 2048, Singapore):
size = [s for s in driver.list_sizes() if s.id == '2'][0]
image = [i for i in driver.list_images() if 'Ubuntu 16.04' in i.name][0]
location = [l for l in driver.list_locations() if l.id == '9'][0]
ssh_key = NodeAuthSSHKey(open(os.path.expanduser('~/.ssh/id_rsa.pub'), 'r').read())

node = driver.create_node(
    name='test_server',
    size=size,
    image=image,
    location=location,
    auth=ssh_key,
    ex_swap=512,
    ex_private=True
)

driver.list_nodes()
