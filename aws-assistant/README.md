# AWS Assistant

A chat page that answers questions about an AWS account, with read-only access: resources,
costs and CloudTrail activity.

This folder starts empty. Its lab guide is added to [docs/](../docs/) before the AWS lab.
# AWS AI Assistant — Windows setup with an IAM role

This guide builds an AWS-only Streamlit assistant using LangChain, Anthropic, and AWS MCP. It uses a manually created IAM role, not IAM Identity Center. Commands below use PowerShell.

```text
Browser → Streamlit → LangChain + Anthropic → AWS MCP → AWS APIs
                                              ↑
                         agent-readonly profile assumes AgentReadOnly
```

## 1. Prerequisites

- AWS CLI v2: [installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
- uv (includes uvx): [installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
- An Anthropic API key and access to the configured model.
- An existing AWS CLI source identity and an administrator able to create the role and policies.

Check your terminal:

```powershell
aws --version
uv --version
uvx --version
aws sts get-caller-identity --profile default
```

Never paste access keys, tokens, or your `.env` into chat. A role has no permanent access keys; your existing identity obtains temporary role credentials.

## 2. Identify who will assume the role

Read the `Arn` from the previous command.

- If it is `arn:aws:iam::ACCOUNT_ID:user/USER_NAME`, use that exact ARN as `SOURCE_PRINCIPAL_ARN` below, including any user path.
- If it is an STS `assumed-role` ARN, obtain the underlying IAM role ARN from IAM → Roles. Use the IAM role ARN, including its path, not the STS session ARN. Your administrator must permit this source role to assume the new role.
- If it ends with `:root`, configure a non-root source identity first. Do not create root access keys.
- If the source profile is missing, configure your organization's existing approved credentials before continuing. For an existing IAM user's keys, `aws configure --profile default` prompts locally; temporary credentials also require a session token and expire.

The setup assumes the source identity and target role are in the same account. Replace every placeholder; do not paste placeholder ARNs into AWS unchanged.

## 3. Create the IAM role

1. Sign in to the AWS Console with permission to manage IAM.
2. Open **IAM → Roles → Create role**.
3. Choose **Custom trust policy**.
4. Paste the following, replacing `SOURCE_PRINCIPAL_ARN` with the exact IAM user or role ARN from step 2:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": "SOURCE_PRINCIPAL_ARN"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

5. Click **Next**. Search for **ReadOnlyAccess**.
6. Select the exact AWS-managed policy named `ReadOnlyAccess`. Search also matches service-specific policies; use pagination if needed. Verify ARN `arn:aws:iam::aws:policy/ReadOnlyAccess`.
7. Click **Next**, name the role **AgentReadOnly**, and create it.
8. Open the role and copy its ARN, for example `arn:aws:iam::ACCOUNT_ID:role/AgentReadOnly`.

`ReadOnlyAccess` is broad and can read data as well as inventory. The prompt's prohibition on data retrieval is guidance, not an IAM restriction. For strict metadata-only access, replace this policy with an approved explicit inventory-action policy. Do not attach administrator or write policies to this role.

## 4. Permit your source identity to assume the role

1. Open **IAM → Users → your source user**, or **IAM → Roles → your source role**.
2. Under **Permissions**, choose **Add permissions → Create inline policy**.
3. Choose JSON and paste this, replacing the role ARN with the one you copied:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::ACCOUNT_ID:role/AgentReadOnly"
    }
  ]
}
```

4. Name it **AssumeAgentReadOnly** and save.

The trust policy names who can assume the role; this policy permits the source identity to request it. The target role's permissions govern its session, rather than inheriting the source identity's administrator permissions. Organization policies and explicit denies can still restrict access.

## 5. Create the local role profile

Replace `ACCOUNT_ID` (and the role path if applicable):

```powershell
aws configure set role_arn arn:aws:iam::ACCOUNT_ID:role/AgentReadOnly --profile agent-readonly
aws configure set source_profile default --profile agent-readonly