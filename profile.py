"""This profile sets up a simple NFS server and a network of clients. The NFS server uses 
*temporary* storage on one of your nodes, the contents will be lost when you terminate your
experiment. We have a different profile available if you need your NFS server data to
persist after your experiment is terminated. 

Instructions:
Click on any node in the topology and choose the `shell` menu item. Your shared NFS directory is mounted at `/nfs` on all nodes."""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Client image list
imageList = [
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD', 'UBUNTU 22.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04'),
]

# Do not change these unless you change the setup scripts too.
nfsServerName = "nfs"
nfsLanName    = "nfsLan"
nfsDirectory  = "/nfs"

# NFS Server Type (Source Server)
pc.defineParameter("serverType", "Source Server Type",
                   portal.ParameterType.STRING, "d710")

# NFS Client Type (Target Server)
pc.defineParameter("clientType", "Target Server Type",
                   portal.ParameterType.STRING, "d710")

pc.defineParameter("osImage", "Select OS image for servers",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList)

pc.defineParameter("nfsSize", "Size of NFS Storage",
                   portal.ParameterType.STRING, "200GB",
                   longDescription="Size of disk partition to allocate on NFS server")

# Always need this when using parameters
params = pc.bindParameters()

# The NFS network. All these options are required.
nfsLan = request.LAN(nfsLanName)
nfsLan.best_effort       = True
nfsLan.vlan_tagging      = True
nfsLan.link_multiplexing = True

# The NFS server.
nfsServer = request.RawPC("snode")
nfsServer.disk_image = params.osImage
nfsServer.hardware_type = params.serverType
# Attach server to lan.
iface0 = nfsServer.addInterface('interface-0', pg.IPv4Address('192.168.6.2','255.255.255.0'))
nfsLan.addInterface(iface0)
# Storage file system goes into a local (ephemeral) blockstore.
nfsBS = nfsServer.Blockstore("nfsBS", nfsDirectory)
nfsBS.size = params.nfsSize
# Initialization script for the server
nfsServer.addService(pg.Execute(shell="sh", command="sudo /bin/bash /local/repository/nfs-server.sh"))

# The NFS client, also attached to the NFS lan.
nfsClient = request.RawPC("tnode")
nfsClient.disk_image = params.osImage
nfsClient.hardware_type = params.clientType
iface2 = nfsClient.addInterface('interface-1', pg.IPv4Address('192.168.6.3','255.255.255.0'))
nfsLan.addInterface(iface2)
# Initialization script for the clients
nfsClient.addService(pg.Execute(shell="sh", command="sudo /bin/bash /local/repository/nfs-client.sh"))

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
