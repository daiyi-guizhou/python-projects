Run build_dpkg.sh to build deb file.

Use following Command to install deb

```bash
sudo apt update
sudo apt --reinstall install -y -f --allow-downgrades ./falcon_agent-20181026_091752.deb
```

If failed to install go-1.10. Please run following to install go-1.10

```bash
sudo add-apt-repository ppa:gophers/archive
sudo apt-get update
```
