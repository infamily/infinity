0. Update site.yml according to application names.

1. Generate the SSH keypair:

mkdir -p roles/app/files/.ssh && ssh-keygen -t rsa -N '' -C "ubuntu@wfx" -f roles/app/files/.ssh/id_rsa

2. Add the generated public key (roles/app/files/.ssh/id_rsa.pub) to Github.

3. Add the hosts to provision to the "hosts" files.
The hostname in the first row must be a real domain that has DNS synced, to be used for nginx configuration and obtaining the Letsencrypt certificate.

# NOTE: While the DNS records had not yet propagate, adding domain to /etc/hosts may be useful.

4. Open Port 80 Letsencrypt to verify the domain.

5. Configure passwordless key-based log-in to root user.

4. Run ansible:
ansible-playbook -i hosts site.yml

After installation, ssh to the application, and do:

cd app_name && ./.git/hooks/post-merge
