# Vault

## A Flet app for secret management

The goal of this app is to test the Python based Flet framework that uses Flutter to create cross platform apps.

The secondarry goal is to create a desktop (mobile too?) app to manage secrets that uses 0-trust to keep the secrets safe.

### Main conepts

1. Client side only. All the encryption/decription happens on the client side, no data is sent to no Vault related server (in fact there is no Vault server)
2. The use decides where they keep their encrypted data. An USB stick, an external hardrive, the internal harddrive will do. The use could decide to replicate the encrypted data over a number of cloud providers like One Drive, Google Drive, etc. by syncing their local worskpace folder to the cloud.
3. The final goal would be to integrate with git servers as a mean to keep the encrypted secrets safe and also provide a wayback mechanism in case a secret is deleted by mistake.

### Drawback
1. If the encryption password is lost there is no way to recover the secrets
2. Not sure if this will be achivable on mobile...

### Contributors are welcome, contact me :)

### Check the [LICENSE.MD](LICENSE.MD) for the license.