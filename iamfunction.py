import boto3
import json


URL = 'http://127.0.0.1:5000'
REGION = 'ap-northeast-1'


def login(aws_access_key_id, aws_secret_access_key):
    iam = boto3.client(
        'iam',
        endpoint_url=URL,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=REGION,
    )

    return iam


def login_as_account(account_id):
    sts = boto3.client(
        'sts',
        endpoint_url=URL,
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name=REGION,
    )

    resp = sts.assume_role(
        RoleArn='arn:aws:iam::' + account_id + ':role/test-role',
        RoleSessionName='test-session',
    )

    c = resp['Credentials']

    iam = boto3.client(
        'iam',
        endpoint_url=URL,
        aws_access_key_id=c['AccessKeyId'],
        aws_secret_access_key=c['SecretAccessKey'],
        aws_session_token=c['SessionToken'],
        region_name=REGION,
    )

    return iam


def list_all_users(iam):
    paginator = iam.get_paginator('list_users')
    result = []

    for page in paginator.paginate():
        for user in page['Users']:
            result.append(user)

    return result


def create_user(user_name, iam):
    try:
        iam.create_user(UserName=user_name)

    except iam.exceptions.EntityAlreadyExistsException:
        return {
            'UserName': user_name,
            'Created': False,
            'Note': user_name + 'は既に作成されているのでスキップします',
        }

    resp = iam.create_access_key(UserName=user_name)

    return {
        'UserName': user_name,
        'AccessKeyId': resp['AccessKey']['AccessKeyId'],
        'SecretAccessKey': resp['AccessKey']['SecretAccessKey'],
        'Created': True,
        'Note': user_name + 'を作成しました',
    }


def delete_user(user_name, iam):
    try:
        for key in iam.list_access_keys(UserName=user_name)['AccessKeyMetadata']:
            iam.delete_access_key(
                UserName=user_name,
                AccessKeyId=key['AccessKeyId'],
            )

        for policy in iam.list_attached_user_policies(UserName=user_name)['AttachedPolicies']:
            iam.detach_user_policy(
                UserName=user_name,
                PolicyArn=policy['PolicyArn'],
            )

        for group in iam.list_groups_for_user(UserName=user_name)['Groups']:
            iam.remove_user_from_group(
                GroupName=group['GroupName'],
                UserName=user_name,
            )

        iam.delete_user(UserName=user_name)

    except iam.exceptions.NoSuchEntityException:
        return {
            'Deleted': False,
            'Note': user_name + 'は存在しません',
        }

    return {
        'Deleted': True,
        'Note': user_name + 'を削除しました',
    }


def list_all_groups(iam):
    paginator = iam.get_paginator('list_groups')
    result = []

    for page in paginator.paginate():
        for group in page['Groups']:
            result.append(group)

    return result


def create_group(group_name, iam):
    try:
        iam.create_group(GroupName=group_name)

    except iam.exceptions.EntityAlreadyExistsException:
        return {
            'Created': False,
            'Note': group_name + 'は既に作成されているのでスキップします',
        }

    return {
        'Created': True,
        'Note': group_name + 'を作成しました',
    }


def delete_group(group_name, iam):
    try:
        group_users = iam.get_group(GroupName=group_name)['Users']
        for user in group_users:
            iam.remove_user_from_group(
                GroupName=group_name,
                UserName=user['UserName'],
            )

        for policy in iam.list_attached_group_policies(GroupName=group_name)['AttachedPolicies']:
            iam.detach_group_policy(
                GroupName=group_name,
                PolicyArn=policy['PolicyArn'],
            )

        iam.delete_group(GroupName=group_name)

    except iam.exceptions.NoSuchEntityException:
        return {
            'Deleted': False,
            'Note': group_name + 'は存在しません',
        }

    return {
        'Deleted': True,
        'Note': group_name + 'を削除しました',
    }


def list_all_policies(iam, scope='Local'):
    paginator = iam.get_paginator('list_policies')
    result = []

    for page in paginator.paginate(Scope=scope):
        for policy in page['Policies']:
            result.append(policy)

    return result


def get_policy_document(policy_arn, iam, version_id=None):
    policy = iam.get_policy(PolicyArn=policy_arn)['Policy']

    if not version_id:
        version_id = policy['DefaultVersionId']

    version = iam.get_policy_version(
        PolicyArn=policy_arn,
        VersionId=version_id,
    )['PolicyVersion']

    return {
        'PolicyName': policy['PolicyName'],
        'PolicyArn': policy['Arn'],
        'VersionId': version['VersionId'],
        'IsDefaultVersion': version['IsDefaultVersion'],
        'Document': version['Document'],
    }


def create_policy(policy_name, policy_document, iam):
    if not isinstance(policy_document, str):
        policy_document = json.dumps(policy_document)

    try:
        resp = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=policy_document,
        )

    except iam.exceptions.EntityAlreadyExistsException:
        return {
            'Created': False,
            'Note': policy_name + 'は既に作成されているのでスキップします',
        }

    return {
        'Created': True,
        'PolicyArn': resp['Policy']['Arn'],
        'Note': policy_name + 'を作成しました',
    }


def delete_policy(policy_arn, iam):
    try:
        versions = iam.list_policy_versions(PolicyArn=policy_arn)['Versions']
        for version in versions:
            if not version['IsDefaultVersion']:
                iam.delete_policy_version(
                    PolicyArn=policy_arn,
                    VersionId=version['VersionId'],
                )

        iam.delete_policy(PolicyArn=policy_arn)

    except iam.exceptions.NoSuchEntityException:
        return {
            'Deleted': False,
            'Note': policy_arn + 'は存在しません',
        }

    return {
        'Deleted': True,
        'Note': policy_arn + 'を削除しました',
    }


def delete_non_default_policy_versions(policy_arn, iam, keep_version_id=None):
    deleted_versions = []
    versions = iam.list_policy_versions(PolicyArn=policy_arn)['Versions']

    for version in versions:
        version_id = version['VersionId']

        if version['IsDefaultVersion']:
            continue

        if keep_version_id and version_id == keep_version_id:
            continue

        iam.delete_policy_version(
            PolicyArn=policy_arn,
            VersionId=version_id,
        )
        deleted_versions.append(version_id)

    return deleted_versions


def update_policy(policy_arn, policy_document, iam):
    if not isinstance(policy_document, str):
        policy_document = json.dumps(policy_document)

    deleted_versions = delete_non_default_policy_versions(policy_arn, iam)

    resp = iam.create_policy_version(
        PolicyArn=policy_arn,
        PolicyDocument=policy_document,
        SetAsDefault=True,
    )
    new_version_id = resp['PolicyVersion']['VersionId']
    deleted_versions.extend(
        delete_non_default_policy_versions(
            policy_arn,
            iam,
            keep_version_id=new_version_id,
        )
    )

    return {
        'Updated': True,
        'VersionId': new_version_id,
        'DeletedVersions': deleted_versions,
        'Note': policy_arn + 'を更新しました',
    }


def attach_user_policy(user_name, policy_arn, iam):
    iam.attach_user_policy(
        UserName=user_name,
        PolicyArn=policy_arn,
    )

    return {
        'Attached': True,
        'Note': user_name + 'にポリシーを追加しました',
    }


def detach_user_policy(user_name, policy_arn, iam):
    iam.detach_user_policy(
        UserName=user_name,
        PolicyArn=policy_arn,
    )

    return {
        'Detached': True,
        'Note': user_name + 'からポリシーを削除しました',
    }


def attach_group_policy(group_name, policy_arn, iam):
    iam.attach_group_policy(
        GroupName=group_name,
        PolicyArn=policy_arn,
    )

    return {
        'Attached': True,
        'Note': group_name + 'にポリシーを追加しました',
    }


def detach_group_policy(group_name, policy_arn, iam):
    iam.detach_group_policy(
        GroupName=group_name,
        PolicyArn=policy_arn,
    )

    return {
        'Detached': True,
        'Note': group_name + 'からポリシーを削除しました',
    }
