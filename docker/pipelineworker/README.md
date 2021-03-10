* This assumes you have your environment configured with AWS creds.
* To get an Azure personal access token, follow these directions: https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=preview-page
* You'll need an ssh keypair registered in AWS. Then reference the name of the key in your secrets.yaml file as `aws_ssh_key_name`. The path to the local file containing the private key should be set in `ansible_ssh_private_key_file`.
