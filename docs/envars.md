# Environment Variables

Sometimes, during development you will need to manage the environment variables, such as 3rd party tokens, and things like that.

To encrypt/decrypt pip `env_production` variables, use Ansible vault:

```
ANSIBLE_VAULT_PASSWORD_FILE=.vault_password.txt ansible-vault decrypt .env_production.vault --output .env_production
```

```
ANSIBLE_VAULT_PASSWORD_FILE=.vault_password.txt ansible-vault encrypt .env_production --output .env_production.vault
```

where, the `.vault_password.txt` is symmetrically encrypted with `passphrase` (same as `VAULT_PASSWORD_KEY` on Travis), decryptable by:

`gpg -d .vault_password.txt.gpg > .vault_password.txt` 

provide the `passphrase` by decrypting `passphrase.txt.gpg`, which is encrypted for all [contributors](https://api.github.com/repos/infamily/infinity/contributors), with their public GPG keys. [Generate and upload](https://help.github.com/articles/generating-a-new-gpg-key/) your public GPG key to github, and ask a current project member to encrypt it again. The current project member will re-import the public keys of contributors, like so:

```
gpg -e -o passphrase.gpg -f recipients passphrase.txt
```

The `recipients` file contains a list of public GPG keys of contributors, which you can use [convenience commands](https://gist.github.com/mindey/ebb24a49c7abe53a938222e9cc75642f) to automatically import and manage.

```
gpg -d passphrase.gpg
```
