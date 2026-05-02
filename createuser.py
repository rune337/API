import argparse
import iamfunction
import yaml


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


def get_target_users(account, cli_users):
    if cli_users:
        return cli_users

    return account.get('create_users', [])


def login_account(account, use_account_id):
    if use_account_id:
        return iamfunction.login_as_account(account['account_id'])

    return iamfunction.login(
        account['access_key'],
        account['secret_key'],
    )


def build_account_from_args(args):
    account_names = args.account or ['cli-account']

    if len(account_names) > 1:
        raise ValueError('configなしの場合、--account は1つだけ指定してください')

    if not args.user:
        raise ValueError('configなしの場合、--user を指定してください')

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
        'create_users': args.user,
    }


def process_account(account, cli_users, use_account_id):
    account_name = account['name']
    users = get_target_users(account, cli_users)

    print('=== processing ' + account_name + ' ===')

    if len(users) == 0:
        print('作成対象ユーザーなし')
        return

    iam = login_account(account, use_account_id)

    for user_name in users:
        result = iamfunction.create_user(user_name, iam)
        print(result['Note'])
        if result['Created']:
            print('AccessKeyId: ' + result['AccessKeyId'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config')
    parser.add_argument('--account', action='append')
    parser.add_argument('--user', action='append')
    parser.add_argument('--use-account-id', action='store_true')
    parser.add_argument('--account-id')
    parser.add_argument('--access-key')
    parser.add_argument('--secret-key')
    args = parser.parse_args()

    try:
        if args.config:
            config = load_config(args.config)
            accounts = filter_accounts(config['accounts'], args.account)
        else:
            accounts = [build_account_from_args(args)]
    except ValueError as e:
        print('入力エラー: ' + str(e))
        return

    if len(accounts) == 0:
        print('対象アカウントがありません')
        return

    for account in accounts:
        process_account(account, args.user, args.use_account_id)


if __name__ == '__main__':
    main()
