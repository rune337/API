import argparse
import json

import iamfunction
import yaml


def add_account_args(parser):
    parser.add_argument('--config')
    parser.add_argument('--account', action='append')
    parser.add_argument('--use-account-id', action='store_true')
    parser.add_argument('--account-id')
    parser.add_argument('--access-key')
    parser.add_argument('--secret-key')


def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def filter_accounts(accounts, target_account_names):
    if not target_account_names:
        return accounts

    return [
        account for account in accounts
        if account['name'] in target_account_names
    ]


def build_account_from_args(args):
    account_names = args.account or ['cli-account']

    if len(account_names) > 1:
        raise ValueError('configなしの場合、--account は1つだけ指定してください')

    if args.use_account_id:
        if not args.account_id:
            raise ValueError('--use-account-id を使う場合、--account-id が必要です')
    else:
        if not args.access_key or not args.secret_key:
            raise ValueError('keyログインの場合、--access-key と --secret-key が必要です')

    return {
        'name': account_names[0],
        'account_id': args.account_id,
        'access_key': args.access_key,
        'secret_key': args.secret_key,
    }


def get_accounts(args):
    if args.config:
        config = load_config(args.config)
        return filter_accounts(config['accounts'], args.account)

    return [build_account_from_args(args)]


def login_account(account, use_account_id):
    if use_account_id:
        return iamfunction.login_as_account(account['account_id'])

    return iamfunction.login(
        account['access_key'],
        account['secret_key'],
    )


def run_for_accounts(args, process):
    try:
        accounts = get_accounts(args)
    except ValueError as e:
        print('入力エラー: ' + str(e))
        return

    if len(accounts) == 0:
        print('対象アカウントがありません')
        return

    for account in accounts:
        print('=== processing ' + account['name'] + ' ===')
        iam = login_account(account, args.use_account_id)
        process(account, iam)


def load_json_arg(json_text, json_file):
    if json_file:
        with open(json_file, 'r') as f:
            return json.load(f)

    if json_text:
        return json.loads(json_text)

    raise ValueError('--policy-json または --policy-file が必要です')


def get_config_list(account, key):
    values = account.get(key, [])

    if values is None:
        return []

    if isinstance(values, list):
        return values

    return [values]


def get_named_policy(account, policy_name):
    policies = account.get('policies', {})

    if not policy_name or policy_name not in policies:
        return None

    policy = policies[policy_name]

    if isinstance(policy, str):
        return {
            'name': policy_name,
            'arn': policy,
        }

    result = dict(policy)
    result.setdefault('name', policy_name)
    return result


def get_policy_arn(account, cli_policy_arn=None, policy_name=None, config_value=None):
    if cli_policy_arn:
        return cli_policy_arn

    if config_value:
        if isinstance(config_value, str):
            policy = get_named_policy(account, config_value)
            if policy:
                return policy['arn']
            return config_value

        if 'arn' in config_value:
            return config_value['arn']

        if 'policy_arn' in config_value:
            return config_value['policy_arn']

        if 'policy' in config_value:
            return get_policy_arn(account, policy_name=config_value['policy'])

        if 'policy_name' in config_value:
            return get_policy_arn(account, policy_name=config_value['policy_name'])

        if 'name' in config_value:
            return get_policy_arn(account, policy_name=config_value['name'])

    policy = get_named_policy(account, policy_name)
    if policy:
        return policy['arn']

    raise ValueError('--policy-arn または config の policies が必要です')


def load_policy_document(account, args, config_value=None):
    policy_json = getattr(args, 'policy_json', None)
    policy_file = getattr(args, 'policy_file', None)

    if policy_json or policy_file:
        return load_json_arg(policy_json, policy_file)

    if config_value:
        config_policy_name = (
            config_value.get('policy_name')
            or config_value.get('policy')
            or config_value.get('name')
        )

        if 'json' in config_value:
            return config_value['json']

        if 'policy_json' in config_value:
            return config_value['policy_json']

        if 'file' in config_value:
            return load_json_arg(None, config_value['file'])

        if 'policy_file' in config_value:
            return load_json_arg(None, config_value['policy_file'])

        policy = get_named_policy(account, config_policy_name)

        if policy:
            if 'json' in policy:
                return policy['json']

            if 'policy_json' in policy:
                return policy['policy_json']

            if 'file' in policy:
                return load_json_arg(None, policy['file'])

            if 'policy_file' in policy:
                return load_json_arg(None, policy['policy_file'])

    policy_name = getattr(args, 'policy_name', None)
    policy = get_named_policy(account, policy_name)

    if policy:
        if 'json' in policy:
            return policy['json']

        if 'policy_json' in policy:
            return policy['policy_json']

        if 'file' in policy:
            return load_json_arg(None, policy['file'])

        if 'policy_file' in policy:
            return load_json_arg(None, policy['policy_file'])

    raise ValueError('--policy-json / --policy-file または config の policy file/json が必要です')
