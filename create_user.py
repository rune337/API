import argparse

import iamcli_common
import iamfunction


def get_target_users(account, cli_users):
    if cli_users:
        return cli_users

    return account.get('create_users', [])


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    parser.add_argument('--user', action='append')
    args = parser.parse_args()

    def process_account(account, iam):
        users = get_target_users(account, args.user)

        if len(users) == 0:
            print('作成対象ユーザーなし')
            return

        for user_name in users:
            result = iamfunction.create_user(user_name, iam)
            print(result['Note'])
            if result['Created']:
                print('AccessKeyId: ' + result['AccessKeyId'])

    if not args.config and not args.user:
        print('入力エラー: configなしの場合、--user を指定してください')
        return

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
