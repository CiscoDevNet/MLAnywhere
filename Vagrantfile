# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure(2) do |config|

  config.vm.box = "generic/ubuntu1804"

config.vm.network "forwarded_port", host_ip: '127.0.0.1', guest: 5000, host: 5000

  config.vm.synced_folder ".", "/home/vagrant"

  config.vm.provision :shell, path: "mlanywhere-bootstrap.sh"

end